import math
import shapely
from shapely import affinity
import vehicles
import config
import math

def debug_print(message):
    if config.global_debug:
        print(message)

def measured_boundary_headway(ego_vehicle, challenger_vehicle):
    return shapely.distance(ego_vehicle.front_bumper().point, challenger_vehicle.front_bumper().point)

def measured_safety_envelope_mdse(ego_vehicle, challenger_vehicle):
    return {"d_lon": calculate_d_lon(ego_vehicle, challenger_vehicle), "d_lat": calculate_d_lat(ego_vehicle, challenger_vehicle)}

def calculated_safety_envelope_mdse(ego_vehicle, challenger_vehicle):
    return {"d_lon_min": calculate_d_lon_min(ego_vehicle, challenger_vehicle), "d_lat_min": calculate_d_lat_min(ego_vehicle, challenger_vehicle)}

def angle_difference(angle1, angle2):
    """Computes the smallest difference between two angles in radians."""
    diff = (angle2 - angle1) % (2 * math.pi)
    if diff > math.pi:
        diff -= 2 * math.pi
    return abs(diff)

def get_vehicle_orientation(ego_vehicle, challenger_vehicle):
    """Determines the orientation of two vehicles considering both position and heading.
    
    Parameters:
    pos1, pos2: Tuples representing (x, y) positions of the vehicles.
    heading1, heading2: Headings of the vehicles in radians (0-2π, where 0 is east, π/2 is north).
    
    Returns:
    One of "same direction", "opposite", or "intersection".
    """
    diff = angle_difference(ego_vehicle.heading, challenger_vehicle.heading)
    
    if diff < math.radians(30):  # Vehicles are roughly aligned
        return "same direction"
    elif diff > math.radians(150):  # Vehicles are nearly opposite
        return "opposite"
    else:
        # Check if the vehicles are approaching an intersection
        dx = challenger_vehicle.center.x - ego_vehicle.center.x
        dy = challenger_vehicle.center.y - ego_vehicle.center.y
        
        direction1 = math.atan2(dy, dx)
        direction2 = (direction1 + math.pi) % (2 * math.pi)  # Opposite direction
        
        if angle_difference(ego_vehicle.heading, direction1) < math.radians(45) or angle_difference(challenger_vehicle.heading, direction2) < math.radians(45):
            debug_print(f"utils.py: Vehicle orientation = intersection")
            return "intersection"
        else:
            if diff < math.radians(90):
                debug_print(f"utils.py: Vehicle orientation = same direction")
                return "same direction"
            else:
                debug_print(f"utils.py: Vehicle orientation = opposite")
                return "opposite"
        
        
def is_vehicle_following(ego_vehicle, challenger_vehicle):
    """
    Determines if the VUT (Vehicle Under Test) is following or leading the challenger vehicle.
    
    Parameters:
    vut: The VUT vehicle object with position and heading attributes.
    challenger: The challenger vehicle object with position and heading attributes.
    
    Returns:
    True if the VUT is following the challenger, False if the VUT is leading the challenger.
    """
    # Calculate the angle between the vehicles
    dx = ego_vehicle.center.x - challenger_vehicle.center.x
    dy = ego_vehicle.center.y - challenger_vehicle.center.y
    
    forward_x, forward_y = math.cos(challenger_vehicle.heading), math.sin(challenger_vehicle.heading)
    projection = dx * forward_x + dy * forward_y
    
    if projection < 0:
        debug_print(f"utils.py: ego_vehicle behind challenger_vehicle")
        return True
    else:
        debug_print(f"utils.py: challenger_vehicle behind ego_vehicle")
        return False
    
def get_relative_position(ego_vehicle, challenger_vehicle):
    """Determines if pos2 is to the left or right of pos1 based on pos1's heading.
    
    Parameters:
    pos1: Tuple representing (x, y) position of the first vehicle.
    heading1: Heading of the first vehicle in radians (0-2π, where 0 is east, π/2 is north).
    pos2: Tuple representing (x, y) position of the second vehicle.
    
    Returns:
    "left" if pos2 is to the left of pos1, "right" if pos2 is to the right.
    """
    dx = challenger_vehicle.center.x - ego_vehicle.center.x
    dy = challenger_vehicle.center.y - ego_vehicle.center.y
    
    relative_angle = math.atan2(dy, dx)
    relative_angle = (relative_angle - ego_vehicle.heading) % (2 * math.pi)
    
    if 0 < relative_angle < math.pi:
        return "left"
    else:
        return "right"

def calculate_mdsev(ego_vehicle, challenger_vehicle):
    # MDSE = Minimum Distance Safety Envelope
    # This function determines if there is a violation of the minimum distance safety envelope between two vehicles.
    
    # in meters
    d_lon = calculate_d_lon(ego_vehicle, challenger_vehicle)
    d_lat = calculate_d_lat(ego_vehicle, challenger_vehicle)
    
    # in meters
    d_lon_min = calculate_d_lon_min(ego_vehicle, challenger_vehicle)
    d_lat_min = calculate_d_lat_min(ego_vehicle, challenger_vehicle)
    
    orientation = get_vehicle_orientation(ego_vehicle, challenger_vehicle)
    
    debug_print(f"MDSE Calculation: d_lon={d_lon}, d_lat={d_lat}, d_lon_min={d_lon_min}, d_lat_min={d_lat_min}, orientation={orientation}")
    
    if orientation == "intersection":
        if d_lon < d_lon_min:
            return 1
    else:
        if d_lon < d_lon_min and d_lat < d_lat_min:
            return 1
        else:
            return 0    
    
    
def get_triangle_legs(hypotenuse, angle_radians):
    """
    Calculates the lengths of the legs of a right triangle given the hypotenuse and one of the angles.
    
    Parameters:
    hypotenuse: The length of the hypotenuse.
    angle_degrees: The angle in radians between the hypotenuse and one of the legs.
    
    Returns:
    A tuple containing the lengths of the two legs (leg1, leg2).
    """
    
    # Calculate the lengths of the legs using trigonometric functions
    leg1 = hypotenuse * math.cos(angle_radians)
    leg2 = hypotenuse * math.sin(angle_radians)
    
    return leg1, leg2    
    
def calculate_d_lon(ego_vehicle, challenger_vehicle):
    d_lon = math.inf
    
    front_bumper_point = ego_vehicle.front_bumper().point
    bounding_box = challenger_vehicle.get_bbox()
    
    distance = front_bumper_point.distance(bounding_box)
    
    angle = angle_difference(ego_vehicle.heading, challenger_vehicle.heading)
    
    leg_a, leg_b = get_triangle_legs(distance, angle)
    
    # Leg A is the one perpendicular to the vehicle
    d_lon = leg_a
    
    debug_print(f"Calculate d_lon: distance={distance}, angle={angle}, leg_a={leg_a}, leg_b={leg_b}, d_lon={d_lon}")
    
    return d_lon

def calculate_d_lat(ego_vehicle, challenger_vehicle):
    d_lat = math.inf
    
    if get_relative_position(ego_vehicle, challenger_vehicle) == "left":
        left_vehicle = ego_vehicle
        right_vehicle = challenger_vehicle
    else:
        left_vehicle = challenger_vehicle
        right_vehicle = ego_vehicle
        
    left_vehicle_right_side_point = left_vehicle.right_side().point
    bounding_box = right_vehicle.get_bbox()
    
    distance = left_vehicle_right_side_point.distance(bounding_box)
    
    angle = angle_difference(left_vehicle.heading, right_vehicle.heading)
    
    leg_a, leg_b = get_triangle_legs(distance, angle)
    
    d_lat = leg_b
    
    debug_print(f"Calculate d_lat: distance={distance}, angle={angle}, leg_a={leg_a}, leg_b={leg_b}, d_lat={d_lat}")
    
    return d_lat
        
def calculate_d_lon_min(ego_vehicle, challenger_vehicle):
    d_lon_min = 0
    
    orientation = get_vehicle_orientation(ego_vehicle, challenger_vehicle)
    
    if orientation == "same direction":
        # Minimum longitudinal distance between two vehicles traveling in the same lon direction
        rear_vehicle = None
        lead_vehicle = None
        
        if (is_vehicle_following(ego_vehicle, challenger_vehicle)):
            rear_vehicle = ego_vehicle
            lead_vehicle = challenger_vehicle
        else:
            rear_vehicle = challenger_vehicle
            lead_vehicle = ego_vehicle
        
        rear_vehicle_v_lon = rear_vehicle.speed_lon
        rear_vehicle_vrt = rear_vehicle.safety_envelope_variables["vehicle_response_time"]
        rear_vehicle_lon_max_accel = rear_vehicle.safety_envelope_variables["lon_max_accel"]
        rear_vehicle_lon_min_decel = rear_vehicle.safety_envelope_variables["lon_min_decel"]
        
        lead_vehicle_v_lon = lead_vehicle.speed_lon
        lead_vehicle_lon_max_accel = lead_vehicle.safety_envelope_variables["lon_max_accel"]
        
        d_lon_min_same = (
            (rear_vehicle_v_lon * rear_vehicle_vrt)
            + (0.5 * rear_vehicle_lon_max_accel * rear_vehicle_vrt ** 2)
            + ((rear_vehicle_v_lon + rear_vehicle_vrt * rear_vehicle_lon_max_accel) ** 2 / (2 * rear_vehicle_lon_min_decel))
            - ((lead_vehicle_v_lon) ** 2 / (2 * lead_vehicle_lon_max_accel))
        )
        
        d_lon_min = d_lon_min_same
    
    elif orientation == "opposite":
        # subscript 1 designates the object moving in the same direction as the prescribed direction of travel 
        # for the lane it is occupying, and subscript 2 designates the object moving opposite to 
        # the prescribed direction of travel for the lane it is occupying
        
        vehicle_one = ego_vehicle
        vehicle_two = challenger_vehicle
        
        vehicle_one_v_lon = vehicle_one.speed_lon
        vehicle_one_vrt = vehicle_one.safety_envelope_variables["vehicle_response_time"]
        vehicle_one_lon_max_accel = vehicle_one.safety_envelope_variables["lon_max_accel"]
        vehicle_one_lon_min_decel = vehicle_one.safety_envelope_variables["lon_min_decel"]
        
        vehicle_two_v_lon = abs(vehicle_two.speed_lon)
        vehicle_two_vrt = vehicle_two.safety_envelope_variables["vehicle_response_time"]
        vehicle_two_lon_max_accel = vehicle_two.safety_envelope_variables["lon_max_accel"]
        vehicle_two_lon_min_decel = vehicle_two.safety_envelope_variables["lon_min_decel"]

        d_lon_min_opp = (
            (2 * vehicle_one_v_lon + vehicle_one_vrt * vehicle_one_lon_max_accel) / 2 * vehicle_one_vrt
            + ((vehicle_one_v_lon + vehicle_one_vrt * vehicle_one_lon_max_accel) ** 2 / (2 * vehicle_one_lon_min_decel))
            + ((2 * vehicle_two_v_lon + vehicle_two_vrt * vehicle_two_lon_max_accel) / (2 * vehicle_two_vrt))
            + ((vehicle_two_v_lon + vehicle_two_vrt * vehicle_two_lon_max_accel) ** 2 / (2 * vehicle_two_lon_min_decel))
        )
        
        d_lon_min = d_lon_min_opp
    
    elif orientation == "intersection":
        # subscript 1 refers to the non-prioritized vehicle, where the non-priorized road user is the one
        # that does not have the right-of-way when intersecting at a conflict point with the trajectory of
        # a priororized road user
        
        # at this point, the ego_vehicle is the prioritized vehicle
        vehicle_one = challenger_vehicle
        vehicle_two = ego_vehicle
        
        vehicle_one_v_lon = vehicle_one.speed_lon
        vehicle_one_vrt = vehicle_one.safety_envelope_variables["vehicle_response_time"]
        vehicle_one_lon_max_accel = vehicle_one.safety_envelope_variables["lon_max_accel"]
        vehicle_one_lon_min_decel = vehicle_one.safety_envelope_variables["lon_min_decel"]

        d_lon_min_intersect = (
            vehicle_one_v_lon * vehicle_one_vrt
            + (1/2 * vehicle_one_lon_max_accel * vehicle_one_vrt ** 2)
            + ((vehicle_one_v_lon + vehicle_one_vrt * vehicle_one_lon_max_accel) ** 2) / (2 * vehicle_one_lon_min_decel)
        )
        
        d_lon_min = d_lon_min_intersect
    
    debug_print(f"Calculate d_lon_min: d_lon_min={d_lon_min}")
    
    return d_lon_min

def calculate_d_lat_min(ego_vehicle, challenger_vehicle):
    # Calculate d_lat and determine if it needs to be split up  
    
    # subscript 1 designates the vehicle on the left, subscript 2 is the vehicle on the right
    
    left_vehicle = None
    right_vehicle = None
    
    if (get_relative_position(ego_vehicle, challenger_vehicle) == "left"):
        left_vehicle = ego_vehicle
        right_vehicle = challenger_vehicle
    else:
        left_vehicle = challenger_vehicle
        right_vehicle = ego_vehicle
    
    left_vehicle_lat_fluctuation_margin = left_vehicle.safety_envelope_variables["lateral_fluctuation_margin"]
    left_vehicle_v_lat = left_vehicle.speed_lat
    left_vehicle_vrt = left_vehicle.safety_envelope_variables["vehicle_response_time"]
    left_vehicle_lat_max_accel = left_vehicle.safety_envelope_variables["lat_max_accel"]
    left_vehicle_lat_min_decel = left_vehicle.safety_envelope_variables["lat_min_decel"]

    right_vehicle_v_lat = right_vehicle.speed_lat
    right_vehicle_vrt = right_vehicle.safety_envelope_variables["vehicle_response_time"]
    right_vehicle_lat_max_accel = right_vehicle.safety_envelope_variables["lat_max_accel"]
    right_vehicle_lat_min_decel = right_vehicle.safety_envelope_variables["lat_min_decel"]

    d_lat_min = (
        left_vehicle_lat_fluctuation_margin
        + (2 * (left_vehicle_v_lat + left_vehicle_vrt * left_vehicle_lat_max_accel) / 2 * left_vehicle_vrt)
        + ((left_vehicle_v_lat + left_vehicle_vrt * left_vehicle_lat_max_accel) ** 2 / (2 * left_vehicle_lat_min_decel))
        - ((2 * right_vehicle_v_lat - right_vehicle_vrt * right_vehicle_lat_max_accel) / 2 * right_vehicle_vrt)
        - ((right_vehicle_v_lat - right_vehicle_vrt * right_vehicle_lat_max_accel) ** 2 / (2 * right_vehicle_lat_min_decel))
    )
    
    debug_print(f"Calculate d_lat_min: d_lat_min={d_lat_min}")
    
    return d_lat_min