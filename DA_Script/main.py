# This script will serve as the main entry point for the visualization. Every function should be as basic
# as possible, reusability and maintainability are the highest priority. 

import pandas as pd
import glob
import os

import plotly.graph_objects as go
import matplotlib.pyplot as plt
import time
from datetime import datetime

import math
import shapely
from shapely import affinity

import safety_metrics.umich_metrics as sm
import dsa_metrics_analysis as sma
import config
import DA_Script.metric_violation_formulas as metric_violation_formulas
import DA_Script.agent as agent
import visualization

# Get current directory
current_directory = os.getcwd()

data_folder = os.path.join(current_directory + '/Data')
input_folder = os.path.join(data_folder + '/Input')
output_folder = os.path.join(data_folder + '/Output')

def main():
    print('Hello')

def create_folders():
    # Create the Data directory
    if not os.path.isdir(data_folder):
        os.makedirs(data_folder)
        os.makedirs(input_folder)
        os.makedirs(output_folder)

    # Grab the input data
    if not os.path.exists(input_folder):
        print('Input folder path not found. Please place input data into the Input folder and re-run this script. (main.create_folders)')
        os.makedirs(input_folder)
        exit()

    # Create the output file path
    if not os.path.exists(output_folder):
        print('Output folder path not found. Creating folder... (main.create_folders)')
        os.makedirs(output_folder)

def process_single_record(data_frame):
    a = 1

def process_records():
    multiple_da_score_list = []

    records = sorted(glob.glob(input_folder + '/*.csv'))

    # Check to see if there are any files to be processed
    if len(input_folder) == 0:
        print('ERROR: No files found to be processed. Aborting. (main.process_records)')
        exit()
    else:
        print('Files to be processed: {}'.format(input_folder))

    for record in records:
        #clear_metric_values()
        record_name = sma.get_record_name_from_record(record)

        now = datetime.now()
        modified_record_name = record_name + '---' + now.strftime('%d') + '-' + now.strftime('%m') + '-' + now.strftime('%Y') + '-' + now.strftime('%H %M %S')

        if config.create_record_output_folders:
            record_output_folder = os.path.join(output_folder, modified_record_name)

            if not os.path.exists(record_output_folder):
                print('Record output folder not found. Creating folder... (main.process_records)')
                os.makedirs(record_output_folder)
            else:
                record_output_folder = output_folder

        print('PROCESSING log file: {}'.format(record_name))

        current_record_df = pd.read_csv(record, sep=r',', skipinitialspace=True)
        
        if config.time_tracking:
            start_elapsed_time = time.time()

        # processed_record_df is a config.processed_record object.
        processed_record_df = process_single_record(current_record_df)

        if config.time_tracking:
            print('Time taken to process: {} [min] (main.process_records)'.format((time.time()-start_elapsed_time)/60.0))

        resulting_csv_name = os.path.join(record_output_folder, record_name + '-dsa_results.csv')

        visualization.create_visualization_output_files(df = processed_record_df, output_path=scen_folder_path)

        if config.time_tracking:
            print('Time taken to visualize: {} [min] (main.process_records)'.format((time.time()-start_elapsed_time)/60.0))

        processed_record_df.df.to_csv(resulting_csv_name, index=False)

        processed_record_df.da_score_dict['DA Score'] = processed_record_df.overall_da_score
        processed_record_df.da_score_dict['Scenario Number'] = record_name

        multiple_da_score_list.append(processed_record_df.df)

    if config.time_tracking:
        end_elapsed_time = (time.time()-start_elapsed_time)
        print('Total elapsed time: {}[min] (main.process_records)'.format(end_elapsed_time/60.0))

    pd.DataFrame(multiple_da_score_list).to_csv(os.path.join(output_folder, now.strftime('%d') + '-' + now.strftime('%m') + '-' + now.strftime('%Y') + '-' + now.strftime('%H%M%S') + 'DA Scores.csv'))

    


    



if __name__ == "__main__":
    main()
