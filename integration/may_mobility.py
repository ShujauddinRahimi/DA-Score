import vehicles
import math

# Define the vehicles

ego_vehicle = vehicles.vehicle()
ego_vehicle.length = 5.1816
ego_vehicle.width = 2.0066
ego_vehicle.type = 'vehicle'
ego_vehicle.id = 'vut'

challenger_vehicle = vehicles.vehicle()
challenger_vehicle.length = 4.6
challenger_vehicle.width = 1.8
challenger_vehicle.type = 'vehicle'
challenger_vehicle.id = 'challenger'

""" 
Define the column names from your data .csv (VUT x, VUT y, etc.)
VUT = vehicle under test / ego vehicle
Challenger = adversary 

The purpose of this section is so that you only need to define the columns from your csv in your data once
"""

timestamp = 'timestamp'

vut_lon = 'VUT lon'
vut_lat = 'VUT lat'
vut_x = 'VUT x'
vut_y = 'VUT y'
vut_sp = 'VUT sp'
vut_lon_sp = 'VUT lon sp'
vut_lat_sp = 'VUT lat sp'
vut_acc = 'VUT acc'
vut_lon_acc = 'VUT lon acc'
vut_lat_acc = 'VUT lat acc'
vut_heading = 'VUT heading' # Should be in radians

challenger_lon = 'challenger lon'
challenger_lat = 'challenger lat'
challenger_x = 'challenger x'
challenger_y = 'challenger y'
challenger_sp = 'challenger sp'
challenger_lon_sp = 'challenger lon sp'
challenger_lat_sp = 'challenger lat sp'
challenger_acc = 'challenger acc'
challenger_lon_acc = 'challenger lon acc'
challenger_lat_acc = 'challenger lat acc'
challenger_heading = 'challenger heading'

# Safety envelope variables, the same values are used for both vehicles depending on the scenario
lateral_fluctuation_margin = 0
vehicle_response_time = 0.75
lon_max_accel = 2.3
lon_min_decel = 1.78
lon_max_decel = 2.7
lat_max_accel = 2.79
lat_min_decel = 0 # Unknown
lat_max_decel = 0 # Unknown