import os

""" global """

# Set to True to enable debugging
global_debug = True

""" main.py """

safety_envelope_formulations = [
    'RSS',      # Responsibility Sensitive Safety
    'MM',       # May Mobility
    'TTC'       # Time to Collision
    'Unstructured' # Unstructured
]

# If a new metric is added, it must be added to the metrics_dict and magnitude_dict dictionaries by adding it to metrics_list and magnitude_list.
metrics_list = [
    'SERV',     # Safety Envelope Ratio Violation
    'SEI',      # Safety Envelope Infringement
    'SEV',      # Safety Envelope Violation
    'SERTV',    # Safety Envelope Restoration Time Violation
    'CI',       # Crash Instance
    'LDV',      # Lane Departure Violation
    'TLV',      # Traffic Law Violation
    'AAV',      # Aggressive Acceleration Violation
    'CERHTCD',  # Compliance Error Rate to Human Traffic Controller Directions
    'ERTV'      # Event Response Time Violation
]

metrics_dict = {metric: {'metric': [], 'magnitude': []} for metric in metrics_list}

# metrics_dict = {metric: [] for metric in metrics_list}

# magnitude_list = [metric + 'M' for metric in metrics_list]

# magnitude_dict = {magnitude: [] for magnitude in magnitude_list}

# # Combine keys from metrics_dict and magnitude_dict
# all_metrics = list(metrics_dict.keys()) + list(magnitude_dict.keys())

# Initialize da_score_dict with all values set to 0
da_score_dict = {metric: {'metric': 0, 'magnitude': 0} for metric in metrics_list}

# Add additional keys with specific initial values
# da_score_dict.update({
#     'Scenario Number': 0,
#     'DA Score': 0
# })

# For debugging use when visualizing the data
debug_list = {
    'VUT Accel': [],
    'VUT Speed': [],
    'Distance to SO': [],
    'Safety Envelope Distance': []
}

""" data_loader.py """
data_path = "C:/" # Enter your data_path here
input_path = os.path.join(data_path + '/input')
output_path = os.path.join(data_path + '/output')


create_scenario_folders = True


""" visualizations.py """
enable_live_visualization = True
save_visualizations = True

columns_to_remove = [
    'SER LON',
    'SER LAT',
    'SER',
    'SERV LON',
    'SERV LAT',
    'SEI LON',
    'SEI LAT'
]

enable_matplotlib_graph = False
enable_plotly_graph = True
enable_mu_bands = False

# Plotting options: 1: minimal, 2: d_lon_min + d_lat_min, 3: full
plot_option = 1

# Viewing options: 1: step-by-step, 2: automatic
view_option = 2

""" vehicles.py """
heading_vector_length = 1000
bumper_line_length = 1000
side_line_length = 1000

""" metrics.py """
#Safety Envelope Ratio Violation
SER_min = 1
SER_max = 1.1

#Safety Envelope Infringement

#Safety Envelope Violation

#Safety Envelope Restoration Time Violation
SERTV_threshold = 5 # seconds

#Crash Violation
#Lane Departure Violation
#Traffic Law Violation
#Aggressive Acceleration Violation
#Compliance Error Rate to Human Traffic Controller Directions

#Event Response Time Violation
ERTV_threshold = 1 # second

""" magnitudes.py """
# n is a percentage applied to the lead vehicle deceleration indicating a proportion of the maximum assumed deceleration for a given scenario (from 0 to 100%)
mrd_n = 0.5

# Safety Envelope Restoration Time Violation Magnitude
# The maximum time allowed for the safety envelope to be restored
SERTVM_min = SERTV_threshold
SERTVM_max = 7 # seconds

# Event Response Time Violation Magnitude
ERTVM_min = ERTV_threshold
ERTVM_max = 4 # seconds

# Aggressive Acceleration Violation Magnitude
AAVM_accel_min = 1.8 # m/s^2
AAVM_accel_max = 3.7 # m/s^2

AAVM_decel_min = 4.51 # m/s^2 = 0.46 g
AAVM_decel_max = 7.84532 # m/s^2 = 0.8 g