""" 
Title: Safety Metrics Module
Author: Shujauddin Rahimi
Supporting Material: SAE J3237

BLACK BOX METRICS
 - Safety Envelope Ratio Violation
 - Safety Envelope Infringement
 - Safety Envelope Violation
 - Safety Envelope Restoration Time Violation
 
 - Collision Incident
 - Lane Departure Violation
 - Traffic Law Violation
 - Aggressive Acceleration Violation
 - Compliance Error Rate to Human Traffic Controller Directions
 - Event Response Time Violation
 
GREY BOX METRICS:
 - [Inside the ODD] ADS DDT Non-Execution Violation
 ...
 
Currently, only black box metrics have been integrated. 
Further work to integrate Grey Box and White Box metrics is ongoing.
"""

import config

import shapely

# BLACK BOX METRICS
def safety_envelope_ratio_violation(orientation, measured_boundary, safety_envelope_boundary):
    """

    Args:
        measured_boundary (float): The measured spatio-temporal boundary between the SV and a salient object (e.g., headway distance)
        safety_envelope_boundary (float): The calculated spatio-temporal safety envelope between the SV and a salient object as defined by a given safety envelope formulation.

    Returns:
        _type_: _description_
    """
    # SER = measured_boundary/safety_envelope_boundary
    
    # if SER > config.SER_max or SER < config.SER_min:
    #     return 0
    # else:
    #     return 1
    
    # MODIFICATION: In order for this metric to work with the MDSE formulation, we need to change the formula to:
    if orientation == "intersection":
        SER_lon = measured_boundary["d_lon"]/safety_envelope_boundary["d_lon_min"]
        
        if SER_lon > config.SER_min and SER_lon < config.SER_max:
            return 0
        else:
            return 1
    else:
        SER_lon = measured_boundary["d_lon"]/safety_envelope_boundary["d_lon_min"]
        SER_lat = measured_boundary["d_lat"]/safety_envelope_boundary["d_lat_min"]
    
        if (SER_lon > config.SER_min and SER_lon < config.SER_max) and (SER_lat > config.SER_min and SER_lat < config.SER_max):
            return 0
        else:
            return 1
    
def safety_envelope_infringement(orientation, measured_boundary, safety_envelope_boundary):
    # if SER >= 1:
    #     return 0
    # else:
    #     return 1
    
    # MODIFICATION: In order for this metric to work with the MDSE formulation, we need to change the formula to:
    if orientation == "intersection":
        SER_lon = measured_boundary["d_lon"]/safety_envelope_boundary["d_lon_min"]
        
        if SER_lon >= 1:
            return 0
        else:
            return 1
    else:
        SER_lon = measured_boundary["d_lon"]/safety_envelope_boundary["d_lon_min"]
        SER_lat = measured_boundary["d_lat"]/safety_envelope_boundary["d_lat_min"]
    
        if (SER_lon >= 1) or (SER_lat >= 1):
            return 0
        else:
            return 1
    
def safety_envelope_violation(SEI, challenger_vehicle):
    challenger_braking_safely = False
    challenger_steering_safely = False
    
    if SEI == 1:
        if challenger_vehicle.acceleration_lon <= challenger_vehicle.safety_envelope_variables["lon_max_decel"]:
            challenger_braking_safely = True
            
        if challenger_vehicle.acceleration_lat <= challenger_vehicle.safety_envelope_variables["lat_max_accel"]:
            challenger_steering_safely = True
            
        if challenger_braking_safely and challenger_steering_safely:
            return 1
        else:
            return 0
    
    return 0
    
def safety_envelope_restoration_time_violation(SERT_duration):
    """
    Inputs:
     - SERT_duration: How long did it take for the safety envelope to be restored?
    
    Outputs:
     - [0, 1] depending on violation criteria

    Refer to data_handler.py for the SERT_duration calculation
    """
    if SERT_duration > config.SERTV_threshold:
        return 1
    else:
        return 0
    
    
def collision_incident(ego_vehicle, challenger_vehicle):
    """ 
    If there is a collision indicator, this function can be amended like so:
     def collision_incident(collision_indicator):
        return int(collision_indicator)
    """
    return int(shapely.intersects(ego_vehicle.get_bbox(), challenger_vehicle.get_bbox()))
    
def lane_departure_violation():
    """
    This has not yet been implemented.
    """
    
    return 0
    
def traffic_law_violation():
    """
    This has not yet been implemented.
    """
    
    return 0

def aggressive_acceleration_violation(vehicle):
    if vehicle.acceleration >= 0:
        # Accelerating
        if abs(vehicle.acceleration) > 1.8:
            return 1
        else:
            return 0
    else:
        # Braking
        if abs(vehicle.acceleration) > 4.51:
            return 1
        else:
            return 0

def compliance_error_rate_to_htc_directions():
    """
    This has not yet been implemented.
    """
    
    return 0
    
def event_response_time_violation(ERT_duration):
    """
    Inputs:
     - ERT_duration: How long did it take for the safety envelope to be restored?
    
    Outputs:
     - [0, 1] depending on violation criteria

    Refer to data_handler.py for the ERT_duration calculation
    """
    if ERT_duration > config.ERTV_threshold:
        return 1
    else:
        return 0