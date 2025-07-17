import config
from datetime import datetime
import glob
import os
import pandas as pd
import time
import visualizations
import utils
import integration.may_mobility as integration
import metrics
import magnitudes

# Begin Helper Functions
def clear_metric_values(metrics_dict, da_score_dict):
    """
    Input: The metrics and da_score dictionaries
    Output: The metrics and da_score dictionaries with all values set to 0
    """
    metrics_dict = {metric: {'metric': 0, 'magnitude': 0} for metric in metrics_dict}
    da_score_dict = {metric: {'metric': 0, 'magnitude': 0} for metric in metrics_dict}

    return metrics_dict, da_score_dict

def get_scenario_name_from_scenario(scenario):
    """
    Input: The scenario file name
    Output: The scenario file name without the extension
    """
    if scenario.endswith('.csv'): 
        file_name_without_extension, extension = os.path.splitext(os.path.basename(scenario))

        return file_name_without_extension
    else:
        return None
#End Helper Functions

def load_data(data_path):
    """
    Input: The master data path
    Output: An array of the input files sorted from A-Z
    """
    input_scenarios = sorted(glob.glob(config.input_path + '/*.csv'))
    
    if not os.path.exists(config.input_path):
        print('data_handler.py: Input folder path not found. Please place input scenarios into the Input folder and re-run this script.')
        os.makedirs(config.input_path)
        exit()
        
    if not os.path.exists(config.output_path):
        print('data_handler.py: Output folder path not found. Creating path...')
        os.makedirs(config.output_path)

    input_scenarios = sorted(glob.glob(config.input_path + '/*.csv'))

    if len(input_scenarios) == 0:
        print('data_handler.py: No scenarios found to be processed. Aborting.')
        exit()
    else:
        print('data_handler.py: Scenarios to be processed: {}'.format(input_scenarios))

    return input_scenarios

# To change the integration that you want to use, import it here and update the code accordingly
# 'integration' is used in the rest of the code to define the active integration
def process_scenario(scenario_df):
    # Initialize vehicles
    ego_vehicle = integration.ego_vehicle
    challenger_vehicle = integration.challenger_vehicle
    
    # Calculate the boundaries for drawing the visualization
    if config.enable_live_visualization:
        x_lim_min = min(scenario_df[integration.vut_x].min(), scenario_df[integration.challenger_x].min()) - 10
        x_lim_max = max(scenario_df[integration.vut_x].max(), scenario_df[integration.challenger_x].max()) + 10
        
        y_lim_min = min(scenario_df[integration.vut_y].min(), scenario_df[integration.challenger_y].min()) - 10
        y_lim_max = max(scenario_df[integration.vut_y].max(), scenario_df[integration.challenger_y].max()) + 10

    # Iterate through each row in the dataframe
    for index, row in scenario_df.iterrows():
        # Get data from the dataframe
        timestamp = row[integration.timestamp]
        
        ego_vehicle.set_center(row[integration.vut_x], row[integration.vut_y])
        ego_vehicle.set_heading(row[integration.vut_heading]) 
        
        ego_vehicle.set_speed(row[integration.vut_sp])
        ego_vehicle.set_speed_lon(row[integration.vut_lon_sp])
        ego_vehicle.set_speed_lat(row[integration.vut_lat_sp])
        
        ego_vehicle.set_acceleration(row[integration.vut_acc])
        ego_vehicle.set_acceleration_lon(row[integration.vut_lon_acc])
        ego_vehicle.set_acceleration_lat(row[integration.vut_lat_acc])
        
        ego_vehicle.safety_envelope_variables["lateral_fluctuation_margin"] = integration.lateral_fluctuation_margin
        ego_vehicle.safety_envelope_variables["vehicle response time"] = integration.vehicle_response_time
        ego_vehicle.safety_envelope_variables["lon_max_accel"] = integration.lon_max_accel
        ego_vehicle.safety_envelope_variables["lon_min_decel"] = integration.lon_min_decel
        ego_vehicle.safety_envelope_variables["lon_max_decel"] = integration.lon_max_decel
        ego_vehicle.safety_envelope_variables["lat_max_accel"] = integration.lat_max_accel
        ego_vehicle.safety_envelope_variables["lat_min_decel"] = integration.lat_min_decel
        ego_vehicle.safety_envelope_variables["lat_max_decel"] = integration.lat_max_decel

        challenger_vehicle.set_center(row[integration.challenger_x], row[integration.challenger_y])
        challenger_vehicle.set_heading(row[integration.challenger_heading])
        
        challenger_vehicle.set_speed(row[integration.challenger_sp])
        challenger_vehicle.set_speed_lon(row[integration.challenger_lon_sp])
        challenger_vehicle.set_speed_lat(row[integration.challenger_lat_sp])
        
        challenger_vehicle.set_acceleration(row[integration.challenger_acc])
        challenger_vehicle.set_acceleration_lon(row[integration.challenger_lon_acc])
        challenger_vehicle.set_acceleration_lat(row[integration.challenger_lat_acc])

        challenger_vehicle.safety_envelope_variables["lateral_fluctuation_margin"] = integration.lateral_fluctuation_margin
        challenger_vehicle.safety_envelope_variables["vehicle response time"] = integration.vehicle_response_time
        challenger_vehicle.safety_envelope_variables["lon_max_accel"] = integration.lon_max_accel
        challenger_vehicle.safety_envelope_variables["lon_min_decel"] = integration.lon_min_decel
        challenger_vehicle.safety_envelope_variables["lon_max_decel"] = integration.lon_max_decel
        challenger_vehicle.safety_envelope_variables["lat_max_accel"] = integration.lat_max_accel
        challenger_vehicle.safety_envelope_variables["lat_min_decel"] = integration.lat_min_decel
        challenger_vehicle.safety_envelope_variables["lat_max_decel"] = integration.lat_max_decel

        # Draw the visualization if enabled
        if config.enable_live_visualization:
            visualizations.draw_scenario(timestamp, ego_vehicle, challenger_vehicle, x_lim_min, x_lim_max, y_lim_min, y_lim_max)
        
        #calculate metrics and magnitudes
        
        #'SERV',     # Safety Envelope Ratio Violation
        # Page 18 of J3237
        orientation = utils.get_vehicle_orientation(ego_vehicle, challenger_vehicle)
        measured_boundary = utils.measured_safety_envelope_mdse(ego_vehicle, challenger_vehicle)
        calculated_boundary = utils.calculated_safety_envelope_mdse(ego_vehicle, challenger_vehicle)
        
        SERV = metrics.safety_envelope_ratio_violation(orientation, measured_boundary, calculated_boundary)
        config.metrics_dict['SERV']['metric'].append(SERV)
        
        #'SERVM',    # Safety Envelope Ratio Violation Magnitude
        SERVM = magnitudes.SERV_magnitude()
        config.metrics_dict['SERV']['magnitude'].append(SERVM)
        
        #'SEI',      # Safety Envelope Infringement
        SEI = metrics.safety_envelope_infringement(orientation, measured_boundary, calculated_boundary)
        config.metrics_dict['SEI']['metric'].append(SEI)
        
        #'SEIM',     # Safety Envelope Infringement Magnitude
        SEIM = magnitudes.SEI_magnitude(SEI, orientation, ego_vehicle, challenger_vehicle)
        config.metrics_dict['SEI']['magnitude'].append(SEIM)

        #'SEV',      # Safety Envelope Violation
        SEV = metrics.safety_envelope_violation(SEI, challenger_vehicle)
        config.metrics_dict['SEV']['metric'].append(SEV)
        
        #'SEVM',     # Safety Envelope Violation Magnitude
        SEVM = magnitudes.SEV_magnitude(SEV, orientation, ego_vehicle, challenger_vehicle)
        config.metrics_dict['SEV']['magnitude'].append(SEVM)

        #'SERTV',    # Safety Envelope Restoration Time Violation
        SERT = 0
        SERTV_flag = 0
        SERT_start = 0
        
        # If a safety envelope infringement has occurred, start the timer
        if SEI == 1 and SERTV_flag == 0:
            SERTV_flag = 1
            SERT_start = timestamp
            
        # While the timer is running, check if the safety envelope has been restored
        if SERTV_flag == 1:
            if SEI == 0:
                SERT = timestamp - SERT_start
                SERTV_flag = 0
        
        SERTV = metrics.safety_envelope_restoration_time_violation(SERT)
        config.metrics_dict['SERTV']['metric'].append(SERTV)
        
        #'SERTVM',   # Safety Envelope Restoration Time Violation Magnitude
        SERTVM = magnitudes.SERTV_magnitude(SERTV, SERT)
        config.metrics_dict['SERTV']['magnitude'].append(SERTVM)

        #'CI',       # Crash Instance
        CI = metrics.collision_incident(ego_vehicle, challenger_vehicle)
        config.metrics_dict['CI']['metric'].append(CI)
        
        #'CIM',      # Collision Incident Magnitude
        CIM = magnitudes.CI_magnitude(CI, ego_vehicle, challenger_vehicle)
        config.metrics_dict['CI']['magnitude'].append(CIM)

        #'LDV',      # Lane Departure Violation
        # Not yet integrated
        LDV = metrics.lane_departure_violation()
        config.metrics_dict['LDV']['metric'].append(LDV)
        
        #'LDVM',     # Lane Departure Violation Magnitude
        LDVM = magnitudes.LDV_magnitude()
        config.metrics_dict['LDV']['magnitude'].append(LDVM)

        #'TLV',      # Traffic Law Violation
        # Not yet integrated
        TLV = metrics.traffic_law_violation()
        config.metrics_dict['TLV']['metric'].append(TLV)
        
        #'TLVM',     # Traffic Law Violation Magnitude
        TLVM = magnitudes.TLV_magnitude()
        config.metrics_dict['TLV']['magnitude'].append(TLVM)

        #'AAV',      # Aggressive Acceleration Violation
        AAV = metrics.aggressive_acceleration_violation(ego_vehicle)
        config.metrics_dict['AAV']['metric'].append(AAV)
        
        #'AAVM',     # Aggressive Acceleration Violation Magnitude
        AAVM = magnitudes.AAV_magnitude(AAV, ego_vehicle)
        config.metrics_dict['AAV']['magnitude'].append(AAVM)

        #'CERHTCD',  # Compliance Error Rate to Human Traffic Controller Directions
        # Not yet integrated
        CERHTCD = metrics.compliance_error_rate_to_htc_directions()
        config.metrics_dict['CERHTCD']['metric'].append(CERHTCD)
        
        #'CERHTCDM',     # Compliance Error Rate to Human Traffic Controller Directions Magnitude
        CERHTCDM = magnitudes.CERHTCD_magnitude()
        config.metrics_dict['CERHTCD']['magnitude'].append(CERHTCDM)
        
        #'ERTV'      # Event Response Time Violation
        ERT = 0
        ERTV_flag = 0
        ERTV_start = 0
        
        # If a safety envelope infringement has occurred, start the timer
        if SEI == 1 and ERTV_flag == 0:
            ERTV_flag = 1
            ERTV_start = timestamp
            
        # While the timer is running, check if the ego_vehicle has responded by decelerating
        if ERTV_flag == 1:
            if ego_vehicle.acceleration_lon < 0:
                ERT = timestamp - ERTV_start
                ERTV_flag = 0
                
        ERTV = metrics.event_response_time_violation(ERT)
        config.metrics_dict['ERTV']['metric'].append(ERTV)
        
        #'ERTVM'     # Event Response Time Violation Magnitude
        ERTVM = magnitudes.ERTV_magnitude(ERTV, ERT)
        config.metrics_dict['ERTV']['magnitude'].append(ERTVM)
    
    utils.debug_print(f"Metrics: {config.metrics_dict}")
    
    # Return the metrics and magnitudes
    return config.metrics_dict
    
def calculate_da_score(metrics_dict):
    # Calculate the DA Score
    da_score = 0
    metric_sum = 0
    
    for metric in config.da_score_dict.keys():
        if metric in metrics_dict.keys():
            config.da_score_dict[metric]['metric'] = max(metrics_dict[metric]['metric'])
            config.da_score_dict[metric]['magnitude'] = max(metrics_dict[metric]['magnitude'])
    
    for metric in config.da_score_dict.keys():
        metric_sum += config.da_score_dict[metric]['metric'] * config.da_score_dict[metric]['magnitude']
        
    da_score =  max(1 - metric_sum, 0) * 100
    
    # config.da_score_dict['DA Score'] = da_score
    
    utils.debug_print(f"da_score_dict: {config.da_score_dict}")
    
    return config.da_score_dict

def batch_process_logs(input_scenarios):
    da_score_list = []
    
    utils.debug_print(f"Processing {len(input_scenarios)}")
    
    start_elapsed_time = time.time()
    
    for scenario in input_scenarios:
        metrics_dict, da_score_dict = clear_metric_values(config.metrics_dict, config.da_score_dict)
        utils.debug_print(f"metrics_dict: {metrics_dict}, da_score_dict: {da_score_dict}")
        
        scenario_name = get_scenario_name_from_scenario(scenario)
        
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        processed_scenario_name = f"{scenario_name}_processed_{timestamp}.csv"
        
        utils.debug_print(f"Processing scenario file: {scenario_name}, will be saved as {processed_scenario_name}")
        
        if config.create_scenario_folders:
            scenario_folder_path = os.path.join(config.output_path, processed_scenario_name)
            if not os.path.exists(scenario_folder_path):
                utils.debug_print("Scenario folder path not found. Creating path...")
                os.makedirs(scenario_folder_path)
        else:
            scenario_folder_path = config.output_path
            
        current_scenario_df = pd.read_csv(scenario, sep=r',', skipinitialspace=True)
        
        metrics_dict = process_scenario(current_scenario_df)
        
        result_file = os.path.join(scenario_folder_path, f"{processed_scenario_name}")
        
        metrics_df_to_save = current_scenario_df.copy(deep=True)
        
        for metric in metrics_dict.keys():
            metrics_df_to_save[f"{metric}"] = metrics_dict[metric]["metric"]
            metrics_df_to_save[f"{metric}M"] = metrics_dict[metric]["magnitude"]
        
        # Save the dataframe to a .csv
        pd.DataFrame.from_dict(metrics_df_to_save).to_csv(result_file, index=False)
        
        da_score_dict = calculate_da_score(metrics_dict)
        # da_score_dict["Scenario Number"] = scenario_name
        
        da_score_list.append(da_score_dict)
        
        # If visualization is enabled, save the visualization
        if config.save_visualizations:
            visualizations.create_visualizations(metrics_df_to_save, scenario_folder_path, scenario_name)
        
    end_elapsed_time = (time.time() - start_elapsed_time)
    utils.debug_print(f"Time taken to process scenarios: {end_elapsed_time/60.0} [min]")
    
    pd.DataFrame(da_score_list).to_csv(os.path.join(config.output_path, f"{timestamp}_DA_Scores.csv"))