""" 
Title: Safety Metrics Magnitude Module
Author: Shujauddin Rahimi
Supporting Material: SAE J3237

BLACK BOX Magnitudes
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
 
GREY BOX Magnitudes:
 - [Inside the ODD] ADS DDT Non-Execution Violation
 ...
 
Currently, only black box magnitudes have been integrated. 
Further work to integrate Grey Box and White Box magnitudes is ongoing.
"""

import utils
import config
import math

# BLACK BOX MAGNITUDES

def SERV_magnitude():
    """
    Needs a magnitude definition. For now, this is set to be 0.1
    """
    return 0.1

def SEI_magnitude(SEI, orientation, ego_vehicle, challenger_vehicle):
    """
    When an SEI occurs, it uses the same magnitude formulation as an SEV.
    """
    
    return SEV_magnitude(SEI, orientation, ego_vehicle, challenger_vehicle)

def SEV_magnitude(SEV, orientation, ego_vehicle, challenger_vehicle):
    """
    Source: 
    Operational Safety Assessment Methodology Framework:
    An Approach to Quantifying Autonomous Vehicle Safety
    by
    Steven G. Como Jr.
    
    Page 35
    """
    # The magnitude is only calculated when there is a violation
    if SEV == 0:
        return 0
    
    if orientation == "intersection":
        ego_vehicle_d_lon = utils.calculate_d_lon(ego_vehicle, challenger_vehicle)
        challenger_vehicle_d_lon = utils.calculate_d_lon(challenger_vehicle, ego_vehicle)
        
        magnitude = (challenger_vehicle.speed_lon / (2 * max(ego_vehicle_d_lon, challenger_vehicle_d_lon))) / ego_vehicle.safety_envelope_variables["lon_max_accel"]
                
    elif orientation == "opposite":
        # This is considered a very dangerous situation, therefore the magnitude is set to 1
        return 1
    else:
        n = config.mrd_n
        mrd = (ego_vehicle.speed_lon ** 2) / (2 * utils.calculate_d_lon_min(ego_vehicle, challenger_vehicle) + ((challenger_vehicle.speed_lon ** 2) / (2 * n * challenger_vehicle.safety_envelope_variables["lon_max_decel"])))
        
        magnitude = mrd / ego_vehicle.safety_envelope_variables["lon_max_decel"]
        
    # Magnitude must be between 0 and 1
    return max(min(magnitude, 1), 0)
        
def SERTV_magnitude(SERTV, SERT):
    """This magnitude is calculated as a linear equation.

    Args:
        SERT (_type_): _description_

    Returns:
        _type_: _description_
    """
    # The magnitude is only calculated when there is a violation
    if SERTV == 0:
        return 0
    
    return max(min((SERT - config.SERTVM_min)/(config.SERTVM_max - config.SERTVM_min), 1), 0)

def CI_magnitude(CI, ego_vehicle, challenger_vehicle):
    """
    Source: 
    Operational Safety Assessment Methodology Framework:
    An Approach to Quantifying Autonomous Vehicle Safety
    by
    Steven G. Como Jr.
    
    Page 42
    """
    # The magnitude is only calculated when there is a violation
    if CI == 0:
        return 0
    
    distance_to_l_side = ego_vehicle.front_bumper().point.distance(challenger_vehicle.left_side().point)
    distance_to_r_side = ego_vehicle.front_bumper().point.distance(challenger_vehicle.right_side().point)
    distance_to_rear = ego_vehicle.front_bumper().point.distance(challenger_vehicle.rear_bumper().point)
    distance_to_front = ego_vehicle.front_bumper().point.distance(challenger_vehicle.front_bumper().point)
    
    case = min(distance_to_l_side, distance_to_r_side, distance_to_rear, distance_to_front)
    
    delta_v = abs(ego_vehicle.speed_lon - challenger_vehicle.speed_lon)
    
    if (case == distance_to_l_side or case == distance_to_r_side):
        return 0.1548 * math.e ** (0.1784 * delta_v)
    elif (case == distance_to_rear):
        return 0.0137 * math.e ** (0.1733 * delta_v)
    elif (case == distance_to_front):
        return 0.0458 * math.e ** (0.165 * delta_v)

def LDV_magnitude():
    """
    Not yet implemented.
    """
    
    return 0

def TLV_magnitude():
    """
    Not yet implemented.
    """
    
    return 0
    
def AAV_magnitude(AAV, ego_vehicle):
    """
    """
    # The magnitude is only calculated when there is a violation
    if AAV == 0:
        return 0
    
    if ego_vehicle.acceleration_lon >= 0:
        #Accelerating case
        
        aa = abs(ego_vehicle.acceleration) - config.AAVM_accel_min
        diff = config.AAVM_accel_max - config.AAVM_accel_min
        
        return max(min(aa/diff, 1), 0)
    else:
        # Decelerating case
        
        aa = abs(ego_vehicle.acceleration) - config.AAVM_decel_min
        diff = config.AAVM_decel_max - config.AAVM_decel_min
        
        return max(min(aa/diff, 1), 0)
        

def CERHTCD_magnitude():
    """
    Not yet implemented.
    """
    
    return 0

def ERTV_magnitude(ERTV, ERT):
    """This magnitude is calculated as a linear equation.

    Args:
        ERT (_type_): _description_

    Returns:
        _type_: _description_
    """
    # The magnitude is only calculated when there is a violation
    if ERTV == 0:
        return 0
    
    return max(min((ERT - config.ERTVM_min)/(config.ERTVM_max - config.ERTVM_min), 1), 0)