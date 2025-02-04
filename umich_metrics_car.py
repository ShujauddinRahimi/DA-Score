
#!/usr/bin/env python

#####################################################
## DSA Metrics Calculation for Scenarios
##
## Code by Shujauddin Rahimi
## Based on safety_metrics_calculation.py
## Written by Maria S. Elli
#####################################################

import numpy as np
from skspatial.objects import Line
import math
from math import cos, sin, sqrt, pow
import shapely
from shapely import affinity

def paths_intersecting_func(vut, challenger):
    if (vut.left_side_line().distance(challenger.left_side_line()) == 0
        or vut.left_side_line().distance(challenger.right_side_line()) == 0
        or vut.right_side_line().distance(challenger.left_side_line()) == 0
        or vut.right_side_line().distance(challenger.right_side_line()) == 0
        or vut.path_polygon().distance(challenger.bbox) == 0
        or vut.path_polygon().distance(challenger.path_polygon()) == 0):
        return 1

    return 0

def facing_front_or_rear_func(vut, challenger):
    if ((vut.heading_vector().distance(challenger.front_bumper()[1]) == 0
        or vut.heading_vector().distance(challenger.rear_bumper()[1]) == 0) 
        and vut.path_polygon().distance(challenger.path_polygon()) != 0
        ):
        return 1
    
    return 0



# Get the difference in local longitude from the VUT to the challenger
def d_lon(vut, challenger):
        paths_intersecting = paths_intersecting_func(vut, challenger)
        facing_front_or_rear = facing_front_or_rear_func(vut, challenger)

        if (paths_intersecting == 1 and facing_front_or_rear == 0):
        #if (abs(vut_heading_offset - challenger_heading_offset) > 5):
            # Get the intersection points of all the side lines to determine d_lon
            intersection_points = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            d_lon = math.inf

            p1 = shapely.Point(0, 0)
            p2 = shapely.Point(0, 0)
            
            intersection_points[0] = vut.left_side_line().intersection(challenger.left_side_line())
            intersection_points[1] = vut.left_side_line().intersection(challenger.right_side_line())
            intersection_points[2] = vut.right_side_line().intersection(challenger.left_side_line())
            intersection_points[3] = vut.right_side_line().intersection(challenger.right_side_line())

            intersection_points[4] = vut.left_side_line().intersection(challenger.front_bumper()[1])
            intersection_points[5] = vut.left_side_line().intersection(challenger.rear_bumper()[1])
            intersection_points[6] = vut.right_side_line().intersection(challenger.front_bumper()[1])
            intersection_points[7] = vut.right_side_line().intersection(challenger.rear_bumper()[1])

            intersection_points[8] = vut.heading_vector().intersection(challenger.front_bumper()[1])
            intersection_points[9] = vut.heading_vector().intersection(challenger.rear_bumper()[1])
            intersection_points[10] = vut.heading_vector().intersection(challenger.left_side()[1])
            intersection_points[11] = vut.heading_vector().intersection(challenger.right_side()[1])

            for intersection in intersection_points:
                # Get the distance from the corners to the intersection points as this is more accurate than using the front bumper coordinate
                cornerlist = list(vut.bbox.exterior.coords)
                cornerlist.append((vut.front_bumper()[0].x, vut.front_bumper()[0].y))
                for corner in cornerlist:
                    corner = shapely.Point(corner[0], corner[1])
                    dist = corner.distance(intersection)
                    if dist < d_lon:
                        d_lon = dist
                        p1 = corner
                        p2 = intersection

            return ['intersection', d_lon, shapely.LineString([p1, p2])]
        
        # If the vehicle's trajectory does not cross the path of the challenger's trajectory, it's either same or opposite direction
        else:
            distance_to_front_bumper = vut.front_bumper()[1].distance(challenger.front_bumper()[1])
            distance_to_rear_bumper = vut.front_bumper()[1].distance(challenger.rear_bumper()[1])

            type = 'opposite'

            if (distance_to_front_bumper < distance_to_rear_bumper):
                c = distance_to_front_bumper
                a = vut.heading_vector().distance(challenger.front_bumper()[0])
                try:
                    b = math.sqrt(c ** 2 - a ** 2)
                except:
                    b = 0

                # # For drawing d_lon
                # d_x = b * math.sin(math.radians(vut.heading))
                # d_y = b * math.cos(math.radians(vut.heading))

                # end_point  =  shapely.Point(vut.front_bumper()[0].x + d_x, vut.front_bumper()[0].y + d_y)
                # return ['opposite', b, shapely.LineString([vut.front_bumper()[0], end_point])]

                


            # If the challenger's rear bumper is closer to the VUT, it's same direction
            else:
                c = distance_to_rear_bumper
                a = vut.heading_vector().distance(challenger.rear_bumper()[0])
                type = 'same'
                try:
                    b = math.sqrt(c ** 2 - a ** 2)
                except:
                    b = 0

                """ # For drawing d_lon
                d_x = b * math.sin(math.radians(vut.heading))
                d_y = b * math.cos(math.radians(vut.heading))

                end_point  =  shapely.Point(vut.front_bumper()[0].x + d_x, vut.front_bumper()[0].y + d_y)
                return ['same', b, shapely.LineString([vut.front_bumper()[0], end_point])] """
            
            end_point = shapely.Point(vut.front_bumper()[0].x + b, vut.front_bumper()[0].y)

            line = shapely.LineString([vut.front_bumper()[0], end_point])

            #print(type, b)

            return [type, b, affinity.rotate(line, vut.heading, origin=vut.front_bumper()[0])]
            
# Get the difference in local latitude from the VUT to the challenger
def d_lat(vut, challenger):
        # Is the challenger to the left or to the right?
        distance_from_left_to_left = vut.left_side()[1].distance(challenger.left_side()[1])
        distance_from_left_to_right = vut.left_side()[1].distance(challenger.right_side()[1])
        distance_from_right_to_left = vut.right_side()[1].distance(challenger.left_side()[1])
        distance_from_right_to_right = vut.right_side()[1].distance(challenger.right_side()[1])

        distance_from_front_to_chall = vut.front_bumper()[1].distance(challenger.bbox)
        distance_from_rear_to_chall = vut.rear_bumper()[1].distance(challenger.bbox)
        
        type = 'right'

        if (distance_from_right_to_left < distance_from_left_to_left and distance_from_right_to_left > 0.2 and distance_from_front_to_chall < distance_from_rear_to_chall):
            try:
                b = vut.heading_vector().distance(challenger.bbox) - 1.5
            except:
                b = 0

            # # For drawing d_lat
            # d_x = b * math.sin(math.radians(vut.heading) + math.pi/2)
            # d_y = b * math.cos(math.radians(vut.heading) + math.pi/2)

            # end_point  =  shapely.Point(vut.right_side()[0].x + d_x, vut.right_side()[0].y + d_y)
            # return ['right', b, shapely.LineString([vut.right_side()[0], end_point])]

            end_point = shapely.Point(vut.right_side()[0].x, vut.right_side()[0].y - b)

            line = shapely.LineString([vut.right_side()[0], end_point])

            return [type, b, affinity.rotate(line, vut.heading, origin=vut.right_side()[0])]
        
        elif (distance_from_left_to_right < distance_from_right_to_right and distance_from_left_to_right > 0.2 and distance_from_front_to_chall < distance_from_rear_to_chall):
            try:
                b = vut.heading_vector().distance(challenger.bbox) - 1.5
            except:
                b = 0

            type = 'left'

            end_point = shapely.Point(vut.left_side()[0].x, vut.left_side()[0].y + b)

            line = shapely.LineString([vut.left_side()[0], end_point])

            return [type, b, affinity.rotate(line, vut.heading, origin=vut.left_side()[0])]

            # # For drawing d_lat
            # d_x = b * math.sin(math.radians(vut.heading) - math.pi/2)
            # d_y = b * math.cos(math.radians(vut.heading) - math.pi/2)

            # end_point  =  shapely.Point(vut.left_side()[0].x + d_x, vut.left_side()[0].y + d_y)
            # return ['left', b, shapely.LineString([vut.left_side()[0], end_point])]
        else:
            b = 0

            type = 'none'

            end_point = shapely.Point(vut.left_side()[0].x, vut.left_side()[0].y + b)

            line = shapely.LineString([vut.left_side()[0], end_point])

            return [type, b, affinity.rotate(line, vut.heading, origin=vut.left_side()[0])]
            # # For drawing d_lat
            # d_x = b * math.sin(math.radians(vut.heading) + math.pi/2)
            # d_y = b * math.cos(math.radians(vut.heading) + math.pi/2)

            # end_point  =  shapely.Point(vut.left_side()[0].x + d_x, vut.left_side()[0].y + d_y)
            # return ['none', b, shapely.LineString([vut.left_side()[0], end_point])]
        
        

def calculate_ci(x, y):
    '''
    Collision Incident     
    '''
    if (x == 0 and y == 0):
        return 1
    else:
        return 0
    
def calculate_orientation(vut, challenger):
    vut_heading = math.radians(vut.heading)
    challenger_heading = math.radians(challenger.heading)

    if abs(vut_heading - challenger_heading) <= math.pi/4:
        return "same"
    elif abs(vut_heading - challenger_heading) <= 3 * math.pi/4:
        return "intersecting"
    else:
        return "opposite"
    
def calculation_relative_object_position(vut, challenger):
    # Returns the relative position of the VUT to the object, if it's "ahead" then the object is in front of the VUT
    dy = challenger.center.y - vut.center.y
    dx = challenger.center.x - vut.center.x

    relative_angle = math.atan2(dy, dx)

    if (abs(math.radians(vut.heading) - relative_angle) <= math.pi):
        print("ahead")
        return "ahead"
    else:
        print("behind")
        return "behind"



    
    
def calculate_sei(vut, challenger, v1_sp_lon, v1_rho, v1_max_accel_lon, v1_min_decel_lon, v2_sp_lon, v2_rho, v2_max_accel_lon, v2_min_decel_lon, v2_max_decel_lon,
                  mu, left_sp_lat, left_rho, left_max_accel_lat, left_min_decel_lat, right_sp_lat, right_rho, right_max_accel_lat, right_min_decel_lat):
    
    d_lon_var = d_lon(vut, challenger)
    d_lon_min = 0

    d_lat_var = d_lat(vut, challenger)
    d_lat_min = 0

    lon_violation = 0
    lat_violation = 0

    # paths_intersecting = paths_intersecting_func(vut, challenger)
    # facing_front_or_rear = facing_front_or_rear_func(vut, challenger)

    # if (paths_intersecting == 1 and facing_front_or_rear == 0):
    #     case = 'intersecting'
    # else:
    #     distance_to_front_bumper = vut.front_bumper()[1].distance(challenger.front_bumper()[1])
    #     distance_to_rear_bumper = vut.front_bumper()[1].distance(challenger.rear_bumper()[1])
    #     if ((vut_heading_offset - challenger_heading_offset) >= 0 and distance_to_front_bumper < distance_to_rear_bumper):
    #         if (distance_to_front_bumper < distance_to_rear_bumper):
    #             case = 'opposite'
    #         else:
    #             case = 'same'
    
    # #case = 'opposite'

    case = calculate_orientation(vut, challenger)

    if case == 'intersecting':
        print(d_lon_var[1])

    

    

    d_lon_min = calculate_d_lon_min(case, v1_sp_lon, v1_rho, v1_max_accel_lon, v1_min_decel_lon, v2_sp_lon, v2_rho, v2_max_accel_lon, v2_min_decel_lon, v2_max_decel_lon)
    d_lat_min = calculate_d_lat_min(mu, left_sp_lat, left_rho, left_max_accel_lat, left_min_decel_lat, right_sp_lat, right_rho, right_max_accel_lat, right_min_decel_lat)

    # relative_object_position = calculation_relative_object_position(vut, challenger)
    # if relative_object_position == 'behind':
    #     d_lon_min = math.inf

    if d_lon_var[1] < d_lon_min:
        lon_violation = 1
    else:
        lon_violation = 0

    if d_lat_var[1] < d_lat_min:
        lat_violation = 1
    else:
        lat_violation = 0

    # print(case, vut_heading_offset, challenger_heading_offset)
    # print(vut.left_side_line().distance(challenger.left_side_line()), vut.left_side_line().distance(challenger.right_side_line()), vut.right_side_line().distance(challenger.left_side_line()), vut.right_side_line().distance(challenger.right_side_line()))
    # print('Lon Violation:', lon_violation, 'Lat Violation:', lat_violation)
    #print('D Lon:', d_lon_var[1], 'D Lon Min:', d_lon_min)
    # print('D Lat:', d_lat[1], 'D Lat Min:', d_lat_min)
    # print(v1_sp_lon)

    if (case == 'intersecting' and lon_violation == 1):
        #print('SEV: 1')
        violation = 1
    elif (case == 'opposite' and lon_violation == 1 and lat_violation == 1):
        #print('SEV: 1')
        violation = 1
    elif (case == 'same' and lon_violation == 1 and lat_violation == 1):
        #print('SEV: 1')
        violation = 1
    else:
        #print('SEV: 0')
        violation = 0



    return [violation, lon_violation, lat_violation, d_lon_min, d_lat_min, case]
        

def calculate_sei_ttc(vut, challenger):
    if paths_intersecting_func(vut=vut, challenger=challenger):
        # VUT's distance to collision point
        vut_d = d_lon(vut=vut, challenger=challenger)[1]

        # Challenger's distance to collision point
        challenger_d = d_lon(vut=challenger, challenger=vut)[1]

        # VUT's time to the collision point
        vut_t = vut_d / vut.speed

        # Challenger's time to the collision point
        challenger_t = challenger_d / challenger.speed

        # If they both have the same time to the collision point, then a collision will occur
        if vut_t == challenger_t:
            if vut_t < 5:
                # [SEI_TTC violation, time to collision]
                return [1, vut_t]
            else:
                return [0, vut_t]
        else:
            return [0, 100]
    else:
        return [0, 100]


    a = 1

def calculate_sei_mm(vut, challenger):
    if shapely.intersects(vut.mm_bbox, challenger.mm_bbox):
        return 1
    else:
        return 0


def calculate_sei_rss_ped(vut, challenger):
    if shapely.intersects(vut.rss_bbox, challenger.ped_bbox):
        return 1
    else:
        return 0
    




def calculate_d_lon_min(case, v1_sp_lon, v1_rho, v1_max_accel_lon, v1_min_decel_lon, v2_sp_lon, v2_rho, v2_max_accel_lon, v2_min_decel_lon, v2_max_decel_lon):
    # Same Direction
    # v1 = rear, v2 = front
    #
    # rear sp lon
    # rear rho
    # rear max accel lon
    # rear min decel lon
    # front sp lon
    # front max decel lon

    if (case == 'same'):
        first_term = v1_sp_lon * v1_rho
        second_term = 0.5 * v1_max_accel_lon * v1_rho ** 2
        third_term = ((v1_sp_lon + v1_rho * v1_max_accel_lon) ** 2)/(2 * v1_min_decel_lon)
        fourth_term = ((v2_sp_lon) ** 2)/(2 * v2_max_decel_lon)

        return max(0, (first_term + second_term + third_term - fourth_term))



    # Opposite Direction
    # v1 = vut, v2 = challenger
    #
    # vut sp lon
    # vut rho
    # vut max accel lon
    # vut min decel lon
    # challenger sp lon
    # challenger rho
    # challenger max accel lon
    # challenger min decel lon

    elif (case == 'opposite'):
        first_term = ((2 * v1_sp_lon + v1_rho * v1_max_accel_lon)/2) * v1_rho
        second_term = ((v1_sp_lon + v1_rho * v1_max_accel_lon) ** 2)/(2 * v1_min_decel_lon)
        third_term = ((2 * abs(v2_sp_lon) + v2_rho * v2_max_accel_lon)/2) * v2_rho
        fourth_term = ((abs(v2_sp_lon) + v2_rho * v2_max_accel_lon) ** 2)/(2 * v2_min_decel_lon)

        return (first_term + second_term + third_term + fourth_term)



    # Intersecting Paths
    # v2 = challenger
    #
    # challenger sp lon
    # challenger max accel lon
    # challenger min decel lon

    elif (case == 'intersecting'):
        first_term = v2_sp_lon * v2_rho
        second_term = 0.5 * v2_max_accel_lon * (v2_rho ** 2)
        third_term = ((v2_sp_lon + v2_rho * v2_max_accel_lon) ** 2)/(2 * v2_min_decel_lon)

        return (first_term + second_term + third_term)



def calculate_d_lat_min(mu, left_sp_lat, left_rho, left_max_accel_lat, left_min_decel_lat, right_sp_lat, right_rho, right_max_accel_lat, right_min_decel_lat):
    # Traveling adjacent to each other
    # mu
    # left sp lat
    # left rho
    # left max accel lat
    # left min decel lat
    # right sp lat
    # right rho
    # right max accel lat
    # right min decel lat
    # mu

    first_term = ((2 * left_sp_lat + left_rho * left_max_accel_lat) / 2) * left_rho
    second_term = ((left_sp_lat + left_rho * left_max_accel_lat) ** 2)/(2 * left_min_decel_lat)
    third_term = ((2 * right_sp_lat - right_rho * right_max_accel_lat) / 2) * right_rho
    fourth_term = ((right_sp_lat - right_rho * right_max_accel_lat) ** 2)/(2 * right_min_decel_lat)

    d_lat_min = mu + max((first_term + second_term - (third_term - fourth_term)), 0)

    return d_lat_min

# Used for SEI
def calculate_mdsei(mdse_lon_v, mdse_lat_v):
    if (mdse_lon_v and mdse_lat_v):
        return 1
    else:
        return 0

# Used for SEV
def calculate_mdsev(msdv_lon, msdv_lat, b_lon_max, a_lat_max, other_lon_acc, other_lat_acc):
    '''
    Minimum Safe Distance Violation 
    
    Happens when both, the longitudinal and lateral msd are unsafe
    '''
    ### MSDV' if both directions are unsafe
    dangerous_situation = msdv_lon & msdv_lat

    ### if other vehicle did not brake harder than b_max, then, the ego vehicle may have caused the dangerous situation 
    other_brake_less_than_b_max = other_lon_acc <= b_lon_max
    
    ### if other vehicle did not steer faster a_lat_max, then, the ego vehicle may have caused the dangerous situation 
    other_acc_less_than_a_lat_max = abs(other_lat_acc) <= abs(a_lat_max)
    
    other_within_assumptions = other_acc_less_than_a_lat_max & other_brake_less_than_b_max
    
    msdv = int(dangerous_situation & other_within_assumptions)

    #print(dangerous_situation, other_lon_acc, b_lon_max, other_lat_acc, a_lat_max, msdv)
    return msdv

# Used for SER
def calculate_mdser_lon(d_lon_min, d_lon):
    if d_lon_min > 0:
        return d_lon / d_lon_min
    else:
        return math.inf
    
def calculate_mdser_lat(d_lat_min, d_lat):
    if d_lat_min > 0:
        return d_lat / d_lat_min
    else:
        return math.inf
    
def calculate_mdser(d_lon_min, d_lon, d_lat_min, d_lat):
    if d_lon_min > 0 and d_lat_min > 0:
        return math.sqrt((d_lon/d_lon_min) ** 2 + (d_lat/d_lat_min) ** 2)
    else:
        return math.inf
    
def calculate_emi(lon_acc, lon_acc_limit, lat_acc, lat_acc_lim):

    if lon_acc > lon_acc_limit or lat_acc > lat_acc_lim:
        return 1
    else:
        return 0
    
def calculate_mdse():
    # in meters
    d_lon = 0
    d_lat = 0

    # in meters per second
    v_lon_object = 0
    v_lat_object = 0

    v_lon_subject = 0
    v_lat_subject = 0

    # in seconds, subject vehicle response time
    subject_vrt = 0
    object_vrt = 0

    # in meters per second squared
    a_lon_max_accel_subject = 0

    a_lat_min_decel_subject = 0
    a_lat_max_accel_subject = 0

    a_lon_min_decel_subject = 0
    a_lon_max_decel_subject = 0
    
    a_lon_max_decel_object = 0
    a_lon_max_accel_object = 0

    a_lon_min_decel_object = 0

    a_lat_max_accel_object = 0
    a_lat_min_decel_object = 0

    mu = 0

    #Minimum longitudinal distance between two vehicles traveling in the same lon direction
    d_lon_min_same  =   ( (v_lon_subject * subject_vrt) 
                        + (0.5 * a_lon_max_accel_subject * subject_vrt ^ 2)
                        + ((v_lon_subject + subject_vrt*a_lon_max_accel_subject)^2 
                        / (2 * a_lon_min_decel_subject))
                        - ((v_lon_object)^2
                        / (2 * a_lon_max_decel_object))
                        )
    
    d_lon_min_opp   =   ( (2 * v_lon_subject + subject_vrt * a_lon_max_accel_subject) / 2 * subject_vrt
                        + ((v_lon_subject + subject_vrt * a_lon_max_accel_subject)^2 / (2 * a_lon_min_decel_subject))
                        + ((2 * abs(v_lon_object) + object_vrt * a_lon_max_accel_object) / (2 * object_vrt))
                        + ((abs(v_lon_object) + object_vrt * a_lon_max_accel_object)^2 / (2 * a_lon_min_decel_object))
                        )
    
    d_lat_min       = ( mu
                        + (2 * (v_lat_subject + subject_vrt * a_lat_max_accel_subject)/2 * subject_vrt)
                        + ((v_lat_subject + subject_vrt * a_lat_max_accel_subject)^2 / 2 * a_lat_min_decel_subject)
                        - ((2 * v_lat_object - object_vrt * a_lat_max_accel_object) / 2 * object_vrt
                        - (v_lat_object - object_vrt * a_lat_max_accel_object) ^ 2 / (2 * a_lat_min_decel_object)) 
                        )
    
    d_lon_min_intersect =   ( v_lon_subject * subject_vrt
                            + (1/2 * a_lon_max_accel_subject * subject_vrt ^ 2)
                            + ((v_lon_subject + subject_vrt * a_lon_max_accel_subject) ^ 2) / (2 * a_lon_min_decel_subject)
                            )

def calculate_ttc(delta_pos, delta_vel, ttc_max = 10):
    '''
    Time To Collision [s]
    '''
    ttc = ttc_max

    # if delta_vel <= 0:
    #     ttc = ttc_max
    # else:
    ttc = delta_pos/delta_vel
    ttc = min(ttc_max, ttc)
    # if ttc < 0:
    #     ttc = ttc_max

    return ttc

def calculate_mttc(delta_pos, delta_vel, delta_acc, mttc_max = 10):
    '''
    Modified Time To Collision [s]
    '''
    mttc = mttc_max

    v = delta_vel
    a = delta_acc
    d = delta_pos
    
    if a == 0 and  v > 0:
        mttc = min(d / v, mttc_max)

    if a == 0 and v <= 0:
        mttc = mttc_max

    if (v**2 + 2*a*d) < 0 :
        mttc = mttc_max
    elif a != 0:
        try:
            t_1 = (-v -(v**2 + 2*a*d)**0.5)/a
            t_2 = (-v +(v**2 + 2*a*d)**0.5)/a
            
            if t_1 > 0 and t_2 > 0:
                if t_1 >= t_2:
                    mttc = t_2
                elif t_1 < t_2:
                    mttc = t_1
            elif t_1 > 0 and t_2 <= 0:
                mttc = t_1
            elif t_1 <= 0 and t_2 > 0:
                mttc = t_2

        ### exception for 'ValueError: negative number cannot be raised to a fractional power'
        ### exception for 'TypeError: '>' not supported between instances of 'complex' and 'int'
        except (ValueError, TypeError) as e:
            # print(repr(e))
            mttc = mttc_max
        
    mttc = min(mttc, mttc_max)

    return mttc

def calculate_pet_curve(df, ego_center_x, ego_center_y, ego_yaw, ego_length, other_center_x, other_center_y, other_yaw, other_length, timestamp, pet_max = np.nan):
    '''
    Post Encroachment Time Curve [s] (postprocessing metric)
    '''
    df_length = len(timestamp)
    
    ego_front_bumper_x = ego_center_x + ego_yaw.apply(cos)*ego_length/2
    ego_front_bumper_y = ego_center_y + ego_yaw.apply(sin)*ego_length/2

    other_rear_bumper_x = other_center_x - other_yaw.apply(cos)*other_length/2
    other_rear_bumper_y = other_center_y - other_yaw.apply(sin)*other_length/2

    diff_arr = np.zeros(df_length)
    min_PET = np.array([])


    for n in range(df_length):
        diff_arr = np.zeros(df_length)
        local_front_bumper_x = ego_front_bumper_x.loc[n]
        local_front_bumper_y = ego_front_bumper_y.loc[n]
        timestamp_n = timestamp.loc[n]
        
        for i in range(df_length):
            diff_arr[i] = sqrt(pow(local_front_bumper_x - other_rear_bumper_x.loc[i], 2) + pow(local_front_bumper_y - other_rear_bumper_y.loc[i], 2))

        conflict_point_list = list(timestamp[(diff_arr > -1) & (diff_arr < 1)].index)
        
        if len(conflict_point_list) != 0:
            PET_list = np.zeros(len(conflict_point_list))
            
            list_index_count = 0
            
            for c in conflict_point_list:
                PET_list[list_index_count] = timestamp_n - timestamp.loc[c]
                PET_list = abs(PET_list)
                list_index_count += 1
                
            min_PET = np.append(min_PET, min(PET_list))
        
        else:
            min_PET = np.append(min_PET, np.nan)  # Replace np.nan with any other default value for continuous visualization
        
    return min(min_PET)

def calculate_thw(distance, speed, thw_max = 10):
    '''
    Time Headway [s]
    '''
    if speed > 0 :
        thw = (distance / speed)
    else:
        thw = thw_max
    thw = min (thw, thw_max)

    return thw

def calculate_lsv(waypoints, current_yaw):
    waypoint_delta_x = waypoints[1][0] - waypoints[0][0]
    waypoint_delta_y = waypoints[1][1] - waypoints[0][1]
    waypoint_heading = np.arctan(waypoint_delta_y/waypoint_delta_x)
    heading_error_mod = divmod((waypoint_heading - current_yaw), np.pi)[1]

    if heading_error_mod > np.pi/2 and heading_error_mod < np.pi:
        heading_error_mod -= np.pi
        
    return heading_error_mod

def calculate_mrd(v1_sp_lon, d_lon_min_same, v2_sp_lon, v2_a_lon_max_decel, n):
    # n is a percentage applied to the lead vehicle deceleration indicating a proportion of the maximum assumed deceleration for a given scenario (from 0 to 100%)
    mrd = (v1_sp_lon ** 2) / (2 * d_lon_min_same + ((v2_sp_lon ** 2) / (2 * n * v2_a_lon_max_decel)))

    return mrd


# msev severity car following
def calculate_msev_mag_cf(v1_sp_lon, d_lon_min_same, v2_sp_lon, v2_a_lon_max_decel, n, v1_a_lon_max_decel):
    mrd = calculate_mrd(v1_sp_lon, d_lon_min_same, v2_sp_lon, v2_a_lon_max_decel, n)

    mag = mrd/v1_a_lon_max_decel

    if (mag > 1):
        return 1
    elif (mag < 0):
        return 0
    else:
        return mag
    
def calculate_msev_mag_int(v2_sp_lon, v1_d_lon_min, v2_d_lon_min, v1_a_lon_max_decel):
    mag = (v2_sp_lon / (2 * max(v1_d_lon_min, v2_d_lon_min)))/v1_a_lon_max_decel
    
    if (mag > 1):
        return 1
    elif (mag < 0):
        return 0
    else:
        return mag

def calculate_msev_mag(vut, challenger, v1_d_lon_min, v2_d_lon_min, v1_sp_lon, v2_sp_lon, v2_a_lon_max_decel, n, v1_a_lon_max_decel):
    vut_heading_offset = min(vut.heading, 360 - vut.heading)
    challenger_heading_offset = min(challenger.heading, 360 - challenger.heading)

    paths_intersecting = paths_intersecting_func(vut, challenger)
    facing_front_or_rear = facing_front_or_rear_func(vut, challenger)
    

    # if (paths_intersecting == 1 and facing_front_or_rear == 0):
    #     case = 'intersecting'

    #     return calculate_msev_mag_int(v2_sp_lon, v1_d_lon_min, v2_d_lon_min, v1_a_lon_max_decel)

    # else:
    #     distance_to_front_bumper = vut.front_bumper()[1].distance(challenger.front_bumper()[1])
    #     distance_to_rear_bumper = vut.front_bumper()[1].distance(challenger.rear_bumper()[1])
    #     if ((vut_heading_offset - challenger_heading_offset) >= 0 and distance_to_front_bumper < distance_to_rear_bumper):
    #         case = 'opposite'

    #         return 1
    #     else:
    #         case = 'same'

    #         d_lon_min_same = max(v1_d_lon_min, v2_d_lon_min)

    #         return calculate_msev_mag_cf(v1_sp_lon, d_lon_min_same, v2_sp_lon, v2_a_lon_max_decel, n, v1_a_lon_max_decel)

    case = calculate_orientation(vut, challenger)

    if case == 'intersecting':
        return calculate_msev_mag_int(v2_sp_lon, v1_d_lon_min, v2_d_lon_min, v1_a_lon_max_decel)
    else:
        if case == 'opposite':
            return 1
        else:
            d_lon_min_same = max(v1_d_lon_min, v2_d_lon_min)
            return calculate_msev_mag_cf(v1_sp_lon, d_lon_min_same, v2_sp_lon, v2_a_lon_max_decel, n, v1_a_lon_max_decel)


def calculate_ci_mag(delta_v, ci, vut, challenger):

    distance_to_l_side = vut.front_bumper()[1].distance(challenger.left_side()[1])
    distance_to_r_side = vut.front_bumper()[1].distance(challenger.right_side()[1])
    distance_to_rear = vut.front_bumper()[1].distance(challenger.rear_bumper()[1])
    distance_to_front = vut.front_bumper()[1].distance(challenger.front_bumper()[1])

    case = min(distance_to_l_side, distance_to_r_side, distance_to_rear, distance_to_front)

    if (case == distance_to_l_side or case == distance_to_r_side):
        ci_mag_side = 0.1548 * math.e ** (0.1784 * delta_v)

        return ci_mag_side
    elif (case == distance_to_rear):
        ci_mag_rear = 0.0137 * math.e ** (0.1733 * delta_v)

        return ci_mag_rear
    elif (case == distance_to_front):
        ci_mag_front = 0.0458 * math.e ** (0.165 * delta_v)

        return ci_mag_front
    
def calculate_sertv_mag(sert):
    return max(min((sert - 5)/2, 1), 0)

def calculate_ortv_mag(ort):
    # Change to 4 seconds
    return max(min((ort - 1)/3, 1), 0)

def calculate_emi_mag(emi):
    if (emi == 1):
        return 1
    else:
        return 0
    
def calculate_aav(vut, lon_acc):
    # Accelerating
    if lon_acc >= 0:
        if abs(vut.acceleration) > 1.8:
            return 1
        else:
            return 0
    else:
        # Braking
        if abs(vut.acceleration) > 4.51:
            return 1
        else:
            return 0

    
def calculate_aav_mag(vut, lon_acc):
    if lon_acc >= 0:
        # linear from 0 to 1, lower bound = 1.8m/s^2,upper bound = 3.7m/s^2

        aa = abs(vut.acceleration) - 1.8
        diff = (3.7 - 1.8)
        return max(min((aa)/diff, 1), 0)
    else:
        # linear from 0 to 1, lower bound = 0.46g (4.51m/s^2),upper bound = 0.8g (7.84532m/s^2)

        aa = abs(vut.acceleration) - 4.51
        diff = (7.84532 - 4.51)
        return max(min((aa)/diff, 1), 0)