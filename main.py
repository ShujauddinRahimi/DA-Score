import config
import data_handler
        
if __name__ == '__main__':
    # Load the data
    input_scenarios = data_handler.load_data(config.data_path)
    data_handler.batch_process_logs(input_scenarios)