#!/usr/bin/env python

################################################
## DA Score Calculation for UMich Scenarios
## 
## Code by Shujauddin Rahimi
## Supplemented by code by Maria S. Elli
################################################

# -- Begin imports

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

# -- End imports


# -- Begin global variables
log = 'mm'

columns_dict = {
    'SEI':      [],         # Safety Envelope Infringement

    'SEV':      [],         # Safety Envelope Violation
    'SEVM':     [],         # Safety Envelope Violation Magnitude

    'SERTV':    [],         # Safety Envelope Restoration Time Violation
    'SERTVM':   [],         # Safety Envelope Restoration Time Violation Magnitude

    'EMI':      [],         # Emergency Maneuver Incident
    'EMIM':     [],         # Emergency Maneuver Incident Magnitude

    'CI':       [],         # Collision Incident
    'CIM':      [],         # Collision Incident Magnitude

    'ORTV':     [],         # OEDR Response Time Violation
    'ORTVM':    [],         # OEDR Response Time Violation Magnitude

    # 'SERV':     [],         # Safety Envelope Ratio Violation
    'DA Score': [],         # Driving Assessment Score
    
    #-------------------------------------------------------------------------#
    # For debugging # Not being used at the moment    
    # 'SER':      [],         # Safety Envelope Ratio
    # 'SER LON':  [],         # Safety Envelope Ratio Longitude
    # 'SER LAT':  [],         # Safety Envelope Ratio Latitude
    
    # 'SERV LON': [],         # Safety Envelope Ratio Longitude
    # 'SERV LAT': [],         # Safety Envelope Ratio Latitude
    # 'SEI LON':  [],         # Safety Envelope Infringement - Longitudinal
    # 'SEI LAT':  [],         # Safety Envelope Infringement - Latitudinal
    'VUT Accel': [],
    'VUT Speed': [],
    'Distance to SO': [],
    'Safety Envelope Distance': []
    
    #-------------------------------------------------------------------------#
    # To be implemented
#   'LDV':      [],         # Lane Departure Violation
#   'TLV':      [],         # Traffic Law Violation
#   'CERHTCD':  [],         # Compliance Error Rate to Human Traffic Controller Directions 
}

da_score_dict = {
    'Scenario Number': 0,
    
    'DA Score': 0,
    
    'SEI':      0,         # Safety Envelope Infringement
    'SEVM':     0,         # Safety Envelope Violation Magnitude
    'SEIC':     0,         # Safety Envelope Infringement Count

    'SEVC':     0,         # Safety Envelope Violation Count

    'SERTV':    0,         # Safety Envelope Restoration Time Violation
    'SERTVM':   0,         # Safety Envelope Restoration Time Violation Magnitude
    'SERTVC':   0,         # Safety Envelope Restoration Time Violation Count

    'EMI':      0,         # Emergency Maneuver Incident
    'EMIM':     0,         # Emergency Maneuver Incident Magnitude
    'EMIC':     0,         # Emergency Maneuver Incident Count

    'CI':       0,         # Collision Incident
    'CIM':      0,         # Collision Incident Magnitude

    'ORTV':     0,         # OEDR Response Time Violation
    'ORTVM':    0,         # OEDR Response Time Violation Magnitude
    'ORTVC':    0          # OEDR Response Time Violation Count
}

columns_to_remove = [
                        'SER LON',
                        'SER LAT',
                        'SER',
                        'SERV LON',
                        'SERV LAT',
                        'SEI LON',
                        'SEI LAT',
                        # 'Distance to SO',
                        # 'Safety Envelope Distance'
                    ]

# End global variables

# Begin class definitions

class vehicle:
    # Given an x, y, heading, and dimensions, a vehicle is constructed
    def __init__(self, x: float, y: float, heading: float, dimensions: [float]):
        self.center = shapely.Point(x, y)

        # UMich heading has been given as compass angle
        self.heading = heading
        
        # dimensions = [length, width]
        self.dimensions = dimensions

        # speed = m/s
        self.speed = 0

    def get_bbox(self):
        length = self.dimensions[1]
        width = self.dimensions[0]

        # Convert angle from compass to regular
        #angle = (450 - self.heading) % 360
        angle = self.heading

        # Top right corner
        tr_x = self.center.x + width/2
        tr_y = self.center.y + length/2
        tr = shapely.Point(tr_x, tr_y)

        # Top left corner
        tl_x = self.center.x - width/2
        tl_y = self.center.y + length/2
        tl = shapely.Point(tl_x, tl_y)

        # Bottom left corner
        bl_x = self.center.x - width/2
        bl_y = self.center.y - length/2
        bl = shapely.Point(bl_x, bl_y)

        # Bottom right corner
        br_x = self.center.x + width/2
        br_y = self.center.y - length/2
        br = shapely.Point(br_x, br_y)

        rect = shapely.Polygon([bl, tl, tr, br])

        # Rotate to match the heading angle
        return affinity.rotate(rect, angle, 'centroid')
    
        #############
        #           #
        #   --F--   #
        #   |   |   #
        #   LS  RS  #
        #   |   |   #
        #   --R--   #
        #           #
        #############
    """ def front_bumper(self):
        
        length = self.dimensions[0]
        width = self.dimensions[1]

        d_l_x = length/2 * math.sin(math.radians(self.heading))
        d_l_y = length/2 * math.cos(math.radians(self.heading))

        fb = shapely.Point(self.center.x + d_l_x, self.center.y + d_l_y)

        d_w_x = width/2 * math.sin(math.radians(self.heading) - math.pi/2)
        d_w_y = width/2 * math.cos(math.radians(self.heading) - math.pi/2)

        end_point1 = shapely.Point(fb.x + d_w_x, fb.y + d_w_y)
        end_point2 = shapely.Point(fb.x - d_w_x, fb.y - d_w_y)

        return [fb, shapely.LineString([[end_point1.x, end_point1.y], [end_point2.x, end_point2.y]])] """
    
    def front_bumper(self):
        length = self.dimensions[0]
        width = self.dimensions[1]

        fb = shapely.Point(self.center.x + length/2, self.center.y)

        end_point1 = shapely.Point(fb.x, fb.y + width/2)
        end_point2 = shapely.Point(fb.x, fb.y - width/2)

        fbr = affinity.rotate(geom=fb, angle=self.heading, origin=self.center)

        fbl = shapely.LineString([[end_point1.x, end_point1.y], [end_point2.x, end_point2.y]])

        fblr = affinity.rotate(geom=fbl, angle=self.heading, origin=self.center)

        return [fbr, fblr]
    
    # def rear_bumper(self):
    #     #############
    #     #           #
    #     #   -----   #
    #     #   |   |   #
    #     #   |   |   #
    #     #   |   |   #
    #     #   --0--   #
    #     #           #
    #     #############
    #     length = self.dimensions[0]
    #     width = self.dimensions[1]

    #     d_l_x = length/2 * math.sin(math.radians(self.heading))
    #     d_l_y = length/2 * math.cos(math.radians(self.heading))

    #     rb = shapely.Point(self.center.x - d_l_x, self.center.y - d_l_y)

    #     d_w_x = width/2 * math.sin(math.radians(self.heading) - math.pi/2)
    #     d_w_y = width/2 * math.cos(math.radians(self.heading) - math.pi/2)

    #     end_point1 = shapely.Point(rb.x + d_w_x, rb.y + d_w_y)
    #     end_point2 = shapely.Point(rb.x - d_w_x, rb.y - d_w_y)

    #     return [rb, shapely.LineString([[end_point1.x, end_point1.y], [end_point2.x, end_point2.y]])]
    
    def rear_bumper(self):
        length = self.dimensions[0]
        width = self.dimensions[1]

        rb = shapely.Point(self.center.x - length/2, self.center.y)

        end_point1 = shapely.Point(rb.x, rb.y + width/2)
        end_point2 = shapely.Point(rb.x, rb.y - width/2)

        rbr = affinity.rotate(geom=rb, angle=self.heading, origin=self.center)

        rbl = shapely.LineString([[end_point1.x, end_point1.y], [end_point2.x, end_point2.y]])

        rblr = affinity.rotate(geom=rbl, angle=self.heading, origin=self.center)

        return [rbr, rblr]
    
    # def left_side(self):
    #     #############
    #     #           #
    #     #   -----   #
    #     #   |   |   #
    #     #   0   |   #
    #     #   |   |   #
    #     #   -----   #
    #     #           #
    #     #############
    #     length = self.dimensions[0]
    #     width = self.dimensions[1]

    #     d_w_x = width/2 * math.sin(math.radians(self.heading) - math.pi/2)
    #     d_w_y = width/2 * math.cos(math.radians(self.heading) - math.pi/2)

    #     ls = shapely.Point(self.center.x + d_w_x, self.center.y + d_w_y)

    #     d_l_x = length/2 * math.sin(math.radians(self.heading))
    #     d_l_y = length/2 * math.cos(math.radians(self.heading))

    #     end_point1 = shapely.Point(ls.x + d_l_x, ls.y + d_l_y)
    #     end_point2 = shapely.Point(ls.x - d_l_x, ls.y - d_l_y)

    #     return [ls, shapely.LineString([[end_point1.x, end_point1.y], [end_point2.x, end_point2.y]])]
    
    def left_side(self):
        length = self.dimensions[0]
        width = self.dimensions[1]

        ls = shapely.Point(self.center.x, self.center.y + width/2)

        end_point1 = shapely.Point(ls.x + length/2, ls.y)
        end_point2 = shapely.Point(ls.x - length/2, ls.y)

        lsr = affinity.rotate(geom=ls, angle=self.heading, origin=self.center)

        lsl = shapely.LineString([[end_point1.x, end_point1.y], [end_point2.x, end_point2.y]])

        lslr = affinity.rotate(geom=lsl, angle=self.heading, origin=self.center)

        return [lsr, lslr]


    # def right_side(self):
    #     #############
    #     #           #
    #     #   -----   #
    #     #   |   |   #
    #     #   |   0   #
    #     #   |   |   #
    #     #   -----   #
    #     #           #
    #     #############
    #     # length = self.dimensions[0]
    #     # d_x = length/2 * math.sin(math.radians(self.heading) - math.pi/2)
    #     # d_y = length/2 * math.cos(math.radians(self.heading) - math.pi/2)

    #     # rs = shapely.Point(self.center.x - d_x, self.center.y - d_y)

    #     # end_point1 = shapely.Point(rs.x + d_x, rs.y + d_y)
    #     # end_point2 = shapely.Point(rs.x - d_x, rs.y - d_y)

    #     # return [rs, shapely.LineString([[end_point1.x, end_point1.y], [end_point2.x, end_point2.y]])]
    
    #     length = self.dimensions[0]
    #     width = self.dimensions[1]

    #     d_w_x = width/2 * math.sin(math.radians(self.heading) - math.pi/2)
    #     d_w_y = width/2 * math.cos(math.radians(self.heading) - math.pi/2)

    #     rs = shapely.Point(self.center.x - d_w_x, self.center.y - d_w_y)

    #     d_l_x = length/2 * math.sin(math.radians(self.heading))
    #     d_l_y = length/2 * math.cos(math.radians(self.heading))

    #     end_point1 = shapely.Point(rs.x + d_l_x, rs.y + d_l_y)
    #     end_point2 = shapely.Point(rs.x - d_l_x, rs.y - d_l_y)

    #     return [rs, shapely.LineString([[end_point1.x, end_point1.y], [end_point2.x, end_point2.y]])]

    def right_side(self):
        length = self.dimensions[0]
        width = self.dimensions[1]

        rs = shapely.Point(self.center.x, self.center.y - width/2)

        end_point1 = shapely.Point(rs.x + length/2, rs.y)
        end_point2 = shapely.Point(rs.x - length/2, rs.y)

        rsr = affinity.rotate(geom=rs, angle=self.heading, origin=self.center)

        rsl = shapely.LineString([[end_point1.x, end_point1.y], [end_point2.x, end_point2.y]])

        rslr = affinity.rotate(geom=rsl, angle=self.heading, origin=self.center)

        return [rsr, rslr]
    
    def rotate_point(x, y, angle, length):
        xr = (x * math.cos(angle)) - (y * math.sin(angle))
        xy = (x * math.sin(angle)) + (y * math.cos(angle)) + length

    def heading_vector(self):
        #############
        #     |     #
        #     |     #
        #     |     #
        #     ▮     #
        #############
        length = 1000
        #d_x = length/2 * math.sin(math.radians(self.heading))
        #d_y = length/2 * math.cos(math.radians(self.heading))

        end_point = shapely.Point(self.center.x + length, self.center.y)

        line = shapely.LineString([[self.center.x, self.center.y], [end_point.x, end_point.y]])

        return affinity.rotate(line, self.heading, origin=self.center)

        return shapely.LineString([[self.center.x, self.center.y], [end_point.x, end_point.y]])
    
    # def front_bumper_line(self):
    #     #############
    #     #           #
    #     #<----F---->#
    #     #   |   |   #
    #     #   |   |   #
    #     #   |   |   #
    #     #   --R--   #
    #     #           #
    #     #############
    #     width = 1000
    #     d_x = width/2 * math.sin(math.radians(self.heading) - math.pi/2)
    #     d_y = width/2 * math.cos(math.radians(self.heading) - math.pi/2)

    #     end_point1 = shapely.Point(self.front_bumper()[0].x + d_x, self.front_bumper()[0].y + d_y)
    #     end_point2 = shapely.Point(self.front_bumper()[0].x - d_x, self.front_bumper()[0].y - d_y)

    #     return shapely.LineString([[end_point1.x, end_point1.y], [end_point2.x, end_point2.y]])

    def front_bumper_line(self):
        length = 1000
        end_point1 = shapely.Point(self.front_bumper()[0].x, self.front_bumper()[0].y + length/2)
        end_point2 = shapely.Point(self.front_bumper()[0].x, self.front_bumper()[0].y - length/2)

        line = shapely.LineString([end_point1, end_point2])

        return affinity.rotate(line, self.heading, origin=self.front_bumper()[0])
    
    # def rear_bumper_line(self):
    #     #############
    #     #           #
    #     #   --F--   #
    #     #   |   |   #
    #     #   |   |   #
    #     #   |   |   #
    #     #<----R---->#
    #     #           #
    #     #############
    #     width = 1000
    #     d_x = width/2 * math.sin(math.radians(self.heading) - math.pi/2)
    #     d_y = width/2 * math.cos(math.radians(self.heading) - math.pi/2)

    #     end_point1 = shapely.Point(self.rear_bumper()[0].x + d_x, self.rear_bumper()[0].y + d_y)
    #     end_point2 = shapely.Point(self.rear_bumper()[0].x - d_x, self.rear_bumper()[0].y - d_y)

    #     return shapely.LineString([[end_point1.x, end_point1.y], [end_point2.x, end_point2.y]])
    
    def rear_bumper_line(self):
        length = 1000
        end_point1 = shapely.Point(self.rear_bumper()[0].x, self.rear_bumper()[0].y + length/2)
        end_point2 = shapely.Point(self.rear_bumper()[0].x, self.rear_bumper()[0].y - length/2)

        line = shapely.LineString([end_point1, end_point2])

        return affinity.rotate(line, self.heading, origin=self.rear_bumper()[0])
    
    # def left_side_line(self):
    #     #############
    #     #   |       #
    #     #   |----   #
    #     #   |   |   #
    #     #   L   |   #
    #     #   |   |   #
    #     #   |----   #
    #     #           #
    #     #############
    #     length = self.dimensions[0] * 30
    #     d_x1 = length/2 * math.sin(math.radians(self.heading))
    #     d_y1 = length/2 * math.cos(math.radians(self.heading))

    #     length = self.dimensions[0]

    #     d_x2 = length/2 * math.sin(math.radians(self.heading))
    #     d_y2 = length/2 * math.cos(math.radians(self.heading))

    #     end_point1 = shapely.Point(self.left_side()[0].x + d_x1, self.left_side()[0].y + d_y1)
    #     end_point2 = shapely.Point(self.left_side()[0].x - d_x2, self.left_side()[0].y - d_y2)

    #     return shapely.LineString([[end_point1.x, end_point1.y], [end_point2.x, end_point2.y]])
    
    def left_side_line(self):
        length = self.dimensions[0] * 30
        end_point1 = shapely.Point(self.left_side()[0].x + length, self.left_side()[0].y)
        end_point2 = shapely.Point(self.left_side()[0].x - self.dimensions[0]/2, self.left_side()[0].y)

        line = shapely.LineString([end_point1, end_point2])

        return affinity.rotate(line, self.heading, origin=self.left_side()[0])
    
    # def right_side_line(self):
    #     #############
    #     #       |   #
    #     #   ----|   #
    #     #   |   |   #
    #     #   |   R   #
    #     #   |   |   #
    #     #   ----|   #
    #     #           #
    #     #############
    #     length = self.dimensions[0] * 30
    #     d_x1 = length/2 * math.sin(math.radians(self.heading))
    #     d_y1 = length/2 * math.cos(math.radians(self.heading))
        
    #     length = self.dimensions[0]

    #     d_x2 = length/2 * math.sin(math.radians(self.heading))
    #     d_y2 = length/2 * math.cos(math.radians(self.heading))

    #     end_point1 = shapely.Point(self.right_side()[0].x + d_x1, self.right_side()[0].y + d_y1)
    #     end_point2 = shapely.Point(self.right_side()[0].x - d_x2, self.right_side()[0].y - d_y2)

    #     return shapely.LineString([[end_point1.x, end_point1.y], [end_point2.x, end_point2.y]])
    
    def right_side_line(self):
        length = self.dimensions[0] * 30
        end_point1 = shapely.Point(self.right_side()[0].x + length, self.right_side()[0].y)
        end_point2 = shapely.Point(self.right_side()[0].x - self.dimensions[0]/2, self.right_side()[0].y)

        line = shapely.LineString([end_point1, end_point2])

        return affinity.rotate(line, self.heading, origin=self.right_side()[0])
    
class RssParameters():
    def __init__(self, alphaLon_accelMax = 1.8, alphaLon_brakeMax = 6.1, alphaLon_brakeMin = 3.6, responseTime = 0.2, alphaLat_accelMin = 5.88, alphaLat_accelMax = 8.83):
        self.alphaLon_accelMax = alphaLon_accelMax
        self.alphaLon_brakeMax = alphaLon_brakeMax
        self.alphaLon_brakeMin = alphaLon_brakeMin
        self.responseTime = responseTime
        # 0.6g = 5.88 m/s^2
        self.alphaLat_accelMin = alphaLat_accelMin
        # 0.9g = 8.83 m/s^2
        self.alphaLat_accelMax = alphaLat_accelMax

# End class definitions



# Begin helper methods

def clear_metric_values():
    global columns_dict
    columns_dict = {key: [] for key in columns_dict}

    global da_score_dict
    da_score_dict = {key: 0 for key in da_score_dict}


def tangent_line(vut, point):
    length = 10000
    d_x = length/2 * math.sin(math.radians(vut.heading))
    d_y = length/2 * math.cos(math.radians(vut.heading))

    end_point1 = shapely.Point(point.x + d_x, point.y + d_y)
    end_point2 = shapely.Point(point.x - d_x, point.y - d_y)

    return shapely.LineString([[end_point1.x, end_point1.y], [end_point2.x, end_point2.y]])

def calculate_delta_vel_lon(data_df):
    '''
    calculate delta in velocity
    delta_v = v_fol - v_lead
    '''

    delta_vel = data_df['VUT sp'] - data_df['challenger sp']
    data_df['delta_vel_lon'] = delta_vel

# Get the difference in accelerations of the two vehicles
def calculate_delta_acc_lon(data_df):
    '''
    calculate delta in acceleration
    delta_acc_lon = a_fol - a_lead
    '''

    delta_acc = data_df['VUT lon acc'] - data_df['challenger lon acc']
    data_df['delta_acc_lon'] = delta_acc



def draw_scenario(timestamp, vut, challenger, x_lim_min, x_lim_max, y_lim_min, y_lim_max):
    # Plot the scenario 

    # Plotting options: 1: minimal, 2: d_lon_min + d_lat_min, 3: full
    plot_option = 3

    # Viewing options: 1: step-by-step, 2: automatic
    view_option = 1

    # Bboxes
    x1,y1 = vut.bbox.exterior.xy
    x2,y2 = challenger.bbox.exterior.xy

    plt.plot(x1, y1)
    plt.plot(x2, y2)

    # Front Bumpers
    plt.plot(vut.front_bumper()[0].x, vut.front_bumper()[0].y, 'b.')
    plt.plot(challenger.front_bumper()[0].x, challenger.front_bumper()[0].y, 'r.')

    x1,y1 = vut.front_bumper()[1].xy
    x2,y2 = challenger.front_bumper()[1].xy
    plt.plot(x1, y1)
    plt.plot(x2, y2)

    if (plot_option > 2):
        # Heading Vectors
        x1,y1 = vut.heading_vector().xy
        x2,y2 = challenger.heading_vector().xy
        plt.plot(x1, y1)
        plt.plot(x2, y2)

        # Front Bumper Lines
        x1,y1 = vut.front_bumper_line().xy
        x2,y2 = challenger.front_bumper_line().xy
        plt.plot(x1, y1)
        plt.plot(x2, y2)

        # Rear Bumper Lines
        x1,y1 = vut.rear_bumper_line().xy
        x2,y2 = challenger.rear_bumper_line().xy
        plt.plot(x1, y1)
        plt.plot(x2, y2)

        # Left Side Lines
        x1,y1 = vut.left_side_line().xy
        x2,y2 = challenger.left_side_line().xy
        plt.plot(x1, y1)
        plt.plot(x2, y2)

        # Right Side Lines
        x1,y1 = vut.right_side_line().xy
        x2,y2 = challenger.right_side_line().xy
        plt.plot(x1, y1)
        plt.plot(x2, y2)

    if (plot_option > 1):
        # Rear Bumpers
        # plt.plot(vut.rear_bumper().x, vut.rear_bumper().y, 'y.')
        # plt.plot(challenger.rear_bumper().x, challenger.rear_bumper().y, 'y.')

        x1,y1 = vut.rear_bumper()[1].xy
        x2,y2 = challenger.rear_bumper()[1].xy
        plt.plot(x1, y1)
        plt.plot(x2, y2)

        # # Left Sides
        # plt.plot(vut.left_side().x, vut.left_side().y, 'm.')
        # plt.plot(challenger.left_side().x, challenger.left_side().y, 'm.')

        x1,y1 = vut.left_side()[1].xy
        x2,y2 = challenger.left_side()[1].xy
        plt.plot(x1, y1)
        plt.plot(x2, y2)

        # # Right Sides
        # plt.plot(vut.right_side().x, vut.right_side().y, 'c.')
        # plt.plot(challenger.right_side().x, challenger.right_side().y, 'c.')

        x1,y1 = vut.right_side()[1].xy
        x2,y2 = challenger.right_side()[1].xy
        plt.plot(x1, y1)
        plt.plot(x2, y2)

        # Centers
        plt.plot(vut.center.x, vut.center.y, 'g.')
        plt.plot(challenger.center.x, challenger.center.y, 'g.')

        # d_lon
        x1,y1 = sm.d_lon(vut, challenger)[2].xy
        #x1,y1 = vut.d_lon(challenger)[2].xy
        plt.plot(x1,y1, 'r')
        
        # d_lat
        x1,y1 = sm.d_lat(vut, challenger)[2].xy
        #x1,y1 = vut.d_lat(challenger)[2].xy
        plt.plot(x1,y1, 'r')

        # for point in sm.d_lat(vut, challenger)[2].boundary.geoms:
        #     line = tangent_line(vut, point)

        #     x1, y1 = line.xy
        #     plt.plot(x1, y1, 'y')

    

    # Plot parameters
    plt.xlim(x_lim_min - 20, x_lim_max + 20)
    plt.ylim(y_lim_min - 20, y_lim_max + 20)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.legend([timestamp])

    plt.show(block=False)

    if (view_option == 1):
        plt.waitforbuttonpress()

    plt.pause(0.00000000000001)
    plt.clf()

def process_log(data_df):
    # start_elapsed_time = time.time()

    calculate_delta_vel_lon(data_df)
    calculate_delta_acc_lon(data_df)

    ## Collision Incident Check Begin ##
    ci_occurs = 0

    # If a collision occurs, remove the last row as it doesn't have useful info
    if (data_df.loc[len(data_df.index) - 1]['timestamp'] == 0):
        ci_occurs = 1
        data_df = data_df.drop(index = [len(data_df.index) - 1])

    ## Collision Incident Check End ##

    # Legacy, not sure if necessary 
    # rss_cits = RssParameters(alphaLon_accelMax = 1.8, alphaLon_brakeMax = 6.1, alphaLon_brakeMin = 3.6, responseTime = 0.2 )
    # rss_aggressive = RssParameters(alphaLon_accelMax = 4.1, alphaLon_brakeMax = 8, alphaLon_brakeMin = 4.6, responseTime = 0.5 )
    # rss_conservative = RssParameters(alphaLon_accelMax = 5.9, alphaLon_brakeMax = 9.5, alphaLon_brakeMin = 4.1, responseTime = 1.9)
    rss_average = RssParameters(alphaLon_accelMax = 2.69, alphaLon_brakeMax = 3.09, alphaLon_brakeMin = 1.78, responseTime = 0.75, alphaLat_accelMin = 5.88, alphaLat_accelMax = 8.83)
    # Assuming a person's max speed of 8mph, and an acceleration time of 5s
    # Assuming a person's
    rss_pedestrian = RssParameters(alphaLon_accelMax = 0.7153, alphaLon_brakeMax = 1.192, alphaLon_brakeMin = 0.2682, responseTime = 0.75, alphaLat_accelMin = 0.134, alphaLat_accelMax = 0.2682)
    #rss_pedestrian = rss_average
    ## Vehicle information
    vut = vehicle(0, 0, 0, [5.1816, 2.0066])
    challenger = vehicle(0, 0, 0, [0.4, 0.7])
    initiate_violation_response = False
    violation_occurrence = False
    sei_happening = False
    sev_happening = False

    # Iterate through each row in the dataframe
    for index, row in data_df.iterrows():
        # Set VUT information
        vut.center = shapely.Point(row['VUT x'], row['VUT y'])
        # MM provides the heading as radians
        vut.heading = math.degrees(row['VUT heading']) 
        vut.bbox = vut.get_bbox()
        vut.speed = row['VUT sp']

        # Set challenger information
        challenger.center = shapely.Point(row['challenger x'], row['challenger y'])
        challenger.heading = math.degrees(row['challenger heading']) 
        challenger.bbox = challenger.get_bbox()
        challenger.speed = row['challenger sp']

        # For setting the vehicle graph size
        x_lim_min = min(data_df['VUT x'].min(), data_df['challenger x'].min())
        x_lim_max = max(data_df['VUT x'].max(), data_df['challenger x'].max())

        y_lim_min = min(data_df['VUT y'].min(), data_df['challenger y'].min())
        y_lim_max = max(data_df['VUT y'].max(), data_df['challenger y'].max())

        draw_scenario(row['timestamp'], vut, challenger, x_lim_min, x_lim_max, y_lim_min, y_lim_max)

        # Safety Envelope Infringement
        if (sm.d_lat(vut, challenger)[0] == 'left'):
            left_lat_sp = row['VUT lat sp']
            right_lat_sp = row['challenger lat sp']
        else:
            left_lat_sp = row['challenger lat sp']
            right_lat_sp = row['VUT lat sp']

        SEI = sm.calculate_sei(vut=vut,
                            challenger=challenger,
                            v1_sp_lon=row['VUT sp'],
                            v1_rho = rss_average.responseTime,
                            v1_max_accel_lon=rss_average.alphaLon_accelMax,
                            v1_min_decel_lon=rss_average.alphaLon_brakeMin,
                            v2_sp_lon=row['challenger sp'],
                            v2_rho=rss_pedestrian.responseTime,
                            v2_max_accel_lon=rss_pedestrian.alphaLon_accelMax,
                            v2_min_decel_lon=rss_pedestrian.alphaLon_brakeMin,
                            v2_max_decel_lon=rss_pedestrian.alphaLon_brakeMax,
                            mu=0.2,
                            left_sp_lat= left_lat_sp,
                            left_rho=rss_average.responseTime,
                            left_max_accel_lat=rss_average.alphaLat_accelMax,
                            left_min_decel_lat=rss_average.alphaLat_accelMin,
                            right_sp_lat= right_lat_sp,
                            right_rho=rss_pedestrian.responseTime,
                            right_max_accel_lat=rss_pedestrian.alphaLat_accelMax,
                            right_min_decel_lat=rss_pedestrian.alphaLat_accelMin,
                            )
        
        print(SEI[0], SEI[1], SEI[2], SEI[3], SEI[4], SEI[5])
        
        SEI_challenger = sm.calculate_sei(vut=challenger,
                            challenger=vut,
                            v1_sp_lon=row['challenger sp'],
                            v1_rho = rss_pedestrian.responseTime,
                            v1_max_accel_lon=rss_pedestrian.alphaLon_accelMax,
                            v1_min_decel_lon=rss_pedestrian.alphaLon_brakeMin,
                            v2_sp_lon=row['VUT sp'],
                            v2_rho=rss_average.responseTime,
                            v2_max_accel_lon=rss_average.alphaLon_accelMax,
                            v2_min_decel_lon=rss_average.alphaLon_brakeMin,
                            v2_max_decel_lon=rss_average.alphaLon_brakeMax,
                            mu=0.2,
                            left_sp_lat= right_lat_sp,
                            left_rho=rss_pedestrian.responseTime,
                            left_max_accel_lat=rss_pedestrian.alphaLat_accelMax,
                            left_min_decel_lat=rss_pedestrian.alphaLat_accelMin,
                            right_sp_lat= left_lat_sp,
                            right_rho=rss_average.responseTime,
                            right_max_accel_lat=rss_average.alphaLat_accelMax,
                            right_min_decel_lat=rss_average.alphaLat_accelMin,
                            )
        
        columns_dict['SEI'].append(SEI[0])    

        # Not being used at the moment    
        # columns_dict['SEI LON'].append(SEI[1])
        # columns_dict['SEI LAT'].append(SEI[2])

        # Safety Envelope Ratio - # Not being used at the moment    
        # SER_LON = sm.calculate_mdser_lon(SEI[3], sm.d_lon(vut, challenger)[1])
        # SER_LAT = sm.calculate_mdser_lat(SEI[4], sm.d_lat(vut, challenger)[1])

        # SER = sm.calculate_mdser(SEI[3], sm.d_lon(vut, challenger)[1], SEI[4], sm.d_lat(vut, challenger)[1])

        # columns_dict['SER LON'].append(SER_LON)
        # columns_dict['SER LAT'].append(SER_LAT)
        # columns_dict['SER'].append(SER)

        # # Safety Envelope Ratio Violation -- NOT BEING USED IN DA SCORE CALCULATION
        # SER_MIN = 1
        # SER_MAX = 1.5
        # # SER_MAX = math.inf

        # if SER_LON < SER_MAX and SER_LON > SER_MIN:
        #     SERV_LON = 0
        # else:
        #     SERV_LON = 1

        # if SER_LAT < SER_MAX and SER_LAT > SER_MIN:
        #     SERV_LAT = 0
        # else:
        #     SERV_LAT = 1

        # if SER < SER_MAX and SER > SER_MIN:
        #     SERV = 0
        # else:
        #     SERV = 1
        
        # columns_dict['SERV LON'].append(SERV_LON)
        # columns_dict['SERV LAT'].append(SERV_LAT)
        # columns_dict['SERV'].append(SERV)

        
        # Safety Envelope Violation
        

        SEV = sm.calculate_mdsev(SEI[1], SEI[2], rss_pedestrian.alphaLon_brakeMax, rss_pedestrian.alphaLat_accelMax, row['challenger lon acc'], row['challenger lat acc'])
        columns_dict['SEV'].append(SEV)

        # Safety Envelope Violation Magnitude
        if SEI[0] == 1:
            SEVM = sm.calculate_msev_mag(vut, challenger, SEI[3], SEI_challenger[3], row['VUT sp'], row['challenger sp'], rss_average.alphaLon_accelMax, 0.5, rss_average.alphaLon_accelMax)
        else:
            SEVM = 0
        
        columns_dict['SEVM'].append(SEVM)

        # Safety Envelope Restoration Time Violation
        SERTV = 0
        SERT = 0

        if (SEI[0] == 1 and violation_occurrence == False):
            violation_occurrence = True
            sert_start = row['timestamp']

        if violation_occurrence == True:
            if SEI[0] == 0:
                sert_end = row['timestamp']
                SERT = sert_end - sert_start
                
                violation_occurrence = False
                if SERT > 5:
                    SERTV = 1

        columns_dict['SERTV'].append(SERTV)

        # Safety Envelope Restoration Time Violation Magnitude
        SERTVM = sm.calculate_sertv_mag(SERT)
        columns_dict['SERTVM'].append(SERTVM)

        # Collision Incident
        if ci_occurs == 1 and index == len(data_df) - 1:
            CI = 1
        else:
            CI = 0
            
        columns_dict['CI'].append(CI)

        # Collision Incident Magnitude
        if CI == 1:
            CIM = sm.calculate_ci_mag(row['delta_vel_lon'], CI, vut, challenger)
        else:
            CIM = 0

        columns_dict['CIM'].append(CIM)

        # OEDR Response Time Violation
        ORTV = 0
        ORT = 0

        if (SEI[0] == 1 and initiate_violation_response == False):
            initiate_violation_response = True
            start_time = row['timestamp']
            print(start_time)

        if initiate_violation_response == True:
            if row['VUT acc'] < 0:
                end_time = row['timestamp']
                print(end_time)
                ORT = end_time - start_time
                print(ORT)
                initiate_violation_response = False
                if ORT > 1:
                    ORTV = 1

        columns_dict['ORTV'].append(ORTV)

        # OEDR Response Time Violation Magnitude
        ORTVM = sm.calculate_ortv_mag(ORT)
        columns_dict['ORTVM'].append(ORTVM)

        # Emergency Maneuver Incident
        EMI = sm.calculate_emi(row['VUT lon acc'], 4.51, row['VUT lat acc'], 1.3) & SEI[0]
        columns_dict['EMI'].append(EMI)

        # Emergency Maneuver Incident Magnitude
        EMIM = sm.calculate_emi_mag(EMI)
        columns_dict['EMIM'].append(EMIM)

        # Calculate counts

        if (SEI[0] == 1 and sei_happening == False):
            sei_happening = True
            da_score_dict['SEIC'] = da_score_dict['SEIC'] + 1
        elif (SEI[0] == 0 and sei_happening == True):
            sei_happening = False

        if (SEV == 1 and sev_happening == False):
            sev_happening = True
            da_score_dict['SEVC'] = da_score_dict['SEVC'] + 1
        elif (SEV == 0 and sev_happening == True):
            sev_happening = False

        if (ORTV == 1):
            da_score_dict['ORTVC'] = da_score_dict['ORTVC'] + 1

        if (EMI == 1):
            da_score_dict['EMIC'] = da_score_dict['EMIC'] + 1

        if (SERTV == 1):
            da_score_dict['SERTVC'] = da_score_dict['SERTVC'] + 1

        # Calculate DA Score
        if (SEVM > da_score_dict['SEVM']):
            da_score_dict['SEVM'] = SEVM
            da_score_dict['SEI'] = SEI[0]

        if (CIM > da_score_dict['CIM']):
            da_score_dict['CIM'] = CIM
            da_score_dict['CI'] = CI

        if (ORTVM > da_score_dict['ORTVM']):
            da_score_dict['ORTVM'] = ORTVM
            da_score_dict['ORTV'] = ORTV

        if (EMIM > da_score_dict['EMIM']):
            da_score_dict['EMIM'] = EMIM
            da_score_dict['EMI'] = EMI

        if (SERTVM > da_score_dict['SERTVM']):
            da_score_dict['SERTVM'] = SERTVM
            da_score_dict['SERTV'] = SERTV

        da_score = (max(1 - sum([SEI[0] * SEVM, 
                                 CI * CIM, 
                                 ORTV * ORTVM, 
                                 EMI * EMIM, 
                                 SERTV * SERTVM]), 0)) * 100
        columns_dict['DA Score'].append(da_score)

        # Extra # Not being used at the moment    
        columns_dict['Distance to SO'].append(vut.get_bbox().distance(challenger.get_bbox()))
        columns_dict['Safety Envelope Distance'].append(SEI[3])
        columns_dict['VUT Accel'].append(row['VUT lon acc'])
        columns_dict['VUT Speed'].append(row['VUT sp'])

    overall_da_score = (max(1 - sum([da_score_dict['SEI'] * da_score_dict['SEVM'], 
                                     da_score_dict['CI'] * da_score_dict['CIM'], 
                                     da_score_dict['ORTV'] * da_score_dict['ORTVM'], 
                                     da_score_dict['EMI'] * da_score_dict['EMIM'], 
                                     da_score_dict['SERTV'] * da_score_dict['SERTVM']]), 0)) * 100
    
    if da_score_dict['CI'] == 1:
        overall_da_score = 0
    

    for key, value in columns_dict.items():
        data_df[key] = value

    return [data_df, da_score_dict, overall_da_score]

def create_visualizations(df, output_path, scenario_name):
    time_stamps = df['timestamp'].drop_duplicates()

    list_of_columns_to_plot = []
    
    for col in columns_dict.keys():
        if col not in columns_to_remove:
            list_of_columns_to_plot.append(col)

    # #Matplotlib graph # Not being used at the moment    
    # for col in list_of_columns_to_plot:
    #     c_max = df.groupby('timestamp')[col].max()
    #     c_mean = df.groupby('timestamp')[col].mean()
    #     c_min = df.groupby('timestamp')[col].min()

    #     plt.fill_between(time_stamps, c_min, c_max,
    #                     alpha=0.2)
        
    #     plt.plot(time_stamps, c_mean)

    # plt.legend(list_of_columns_to_plot, bbox_to_anchor = (1, 0.5), loc='center left')
    # plt.xlabel('Time (seconds)')
    # plt.ylabel('Value')
    # plt.suptitle(scenario_name + ' Data Visualization')
    # figure = plt.gcf().set_size_inches(25.6, 14.4)
    # try:
    #     plt.savefig(os.path.join(output_path, 'DV-' + scenario_name + '.png'), dpi = 100)
    #     print('Matplotlib plot was saved successfully.')
    # except:
    #     print('ERROR: Matplotlib plot could not be saved.')


    #Plotly graph
    boundary_colors = [
                'rgba(31, 119, 180, 0.075)',        # muted blue
                'rgba(255, 127, 14, 0.075)',        # safety orange
                'rgba(44, 160, 44, 0.075)',         # cooked asparagus green
                'rgba(214, 39, 40, 0.075)',         # brick red
                'rgba(148, 103, 189, 0.075)',       # muted purple
                'rgba(140, 86, 75, 0.075)',         # chestnut brown
                'rgba(227, 119, 194, 0.075)',       # raspberry yogurt pink
                'rgba(127, 127, 127, 0.075)',       # middle gray
                'rgba(188, 189, 34, 0.075)',        # curry yellow-green
                'rgba(23, 190, 207, 0.075)'         # blue-teal
            ]

    line_colors =  [
                'rgba(31, 119, 180, 1)',            # muted blue
                'rgba(255, 127, 14, 1)',            # safety orange
                'rgba(44, 160, 44, 1)',             # cooked asparagus green
                'rgba(214, 39, 40, 1)',             # brick red
                'rgba(148, 103, 189, 1)',           # muted purple
                'rgba(140, 86, 75, 1)',             # chestnut brown
                'rgba(227, 119, 194, 1)',           # raspberry yogurt pink
                'rgba(127, 127, 127, 1)',           # middle gray
                'rgba(188, 189, 34, 1)',            # curry yellow-green
                'rgba(23, 190, 207, 1)'             # blue-teal
            ]

    color_index = 0

    fig = go.Figure()

    for col in list_of_columns_to_plot:
        c_max = df.groupby('timestamp')[col].max()
        c_mean = df.groupby('timestamp')[col].mean()
        c_min = df.groupby('timestamp')[col].min()        

        # Adds MU bands
        # fig.add_trace(go.Scatter(x=time_stamps, y = c_max, fill = None, mode = 'lines', line_color = boundary_colors[color_index], legendgroup=col, legendgrouptitle_text=col, name=col + ' max'))
        # fig.add_trace(go.Scatter(x=time_stamps, y = c_min, fill='tonexty', mode = 'lines', line_color = boundary_colors[color_index], legendgroup=col, name = col + ' min and fill', fillcolor = boundary_colors[color_index]))

        fig.add_trace(go.Scatter(x=time_stamps, y = c_mean, fill = None, mode = 'lines', line_color = line_colors[color_index], legendgroup=col, name = col))# + ' average'))

        color_index = (color_index + 1) % 10

    fig.update_layout(title = scenario_name + ' Interactive Data Visualization', xaxis_title='Time (seconds)', yaxis_title='Value', legend_title='Legend')
    try:
        fig.write_html(os.path.join(output_path, 'Interactive_DV-' + scenario_name + '.html'))
        print('Plotly plot was saved successfully.')
    except:
        print('ERROR: Plotly plot was not saved successfully.')

def calculate_safety_metrics(data_path):
    da_score_list = []

    # For keeping track of how long calculation runs for
    start_elapsed_time = time.time()

    input_path = os.path.join(data_path + '/Input')
    output_path = os.path.join(data_path + '/Output')

    # Check to see if the experiment folder exists
    if not os.path.exists(data_path):
        print('Experiment Folder path does not exist. Creating path. Please place input data into the Input folder and re-run this script.')
        os.makedirs(data_path)
        os.makedirs(input_path)
        os.makedirs(output_path)
        exit()

    # Grab the input data
    if not os.path.exists(input_path):
        print('Input folder path not found. Please place input data into the Input folder and re-run this script.')
        os.makedirs(input_path)
        exit()

    input_files = sorted(glob.glob(input_path + '/*.csv'))

    # Check to see if there are any files to be processed
    if len(input_files) == 0:
        print('ERROR: No files found to be processed. Aborting.')
        exit()
    else:
        print('Files to be processed: {}'.format(input_files))

    # Create the output file path
    if not os.path.exists(output_path):
        print('Output folder path not found. Creating path...')
        os.makedirs(output_path)

    for file in input_files:
        # Clears the columns_dict dictionary
        clear_metric_values()

        #scenario_group = sma.get_scenario_group_from_filename(log_file)
        scenario_name = sma.get_scenario_name_from_filename(file)

        now = datetime.now()
        current_title = scenario_name + '---' + now.strftime('%d') + '-' + now.strftime('%m') + '-' + now.strftime('%Y') + '-' + now.strftime('%H%M%S')
        
        create_scenario_folders = True
        
        if create_scenario_folders:
            scen_folder_path = os.path.join(output_path, current_title)
            if not os.path.exists(scen_folder_path):
                print('Scenario folder path not found. Creating path...')
                os.makedirs(scen_folder_path)
        else:
            scen_folder_path = output_path

        print('Processing log file: {}'.format(scenario_name))

        #Get the dataframe for the current log being processed
        current_log_df = pd.read_csv(file, sep = r',', skipinitialspace= True)

        processed_df = process_log(current_log_df)
        print('Time taken to process: {}[min]'.format((time.time()-start_elapsed_time)/60.0))

        result_name = os.path.join(scen_folder_path, scenario_name + '-dsa_results.csv')

        create_visualizations(processed_df[0], scen_folder_path, scenario_name)
        print('Time taken to visualize: {}[min]'.format((time.time()-start_elapsed_time)/60.0))

        # Save the dataframe to a .csv
        processed_df[0].to_csv(result_name, index=False)

        # The DA Score DataFrame
        processed_df[1]['DA Score'] = processed_df[2]
        processed_df[1]['Scenario Number'] = scenario_name

        da_score_list.append(processed_df[1])

        
    end_elapsed_time = (time.time()-start_elapsed_time)
    print('Total elapsed time: {}[min]'.format(end_elapsed_time/60.0))


    pd.DataFrame(da_score_list).to_csv(os.path.join(output_path, now.strftime('%d') + '-' + now.strftime('%m') + '-' + now.strftime('%Y') + '-' + now.strftime('%H%M%S') + 'DA Scores.csv'))



if __name__ == '__main__':
    experiment_name = 'UMich'
    data_path = os.path.join(os.environ['SCENARIO_RUNNER_ROOT'], '../UMich/Data Processing', experiment_name)

    calculate_safety_metrics(data_path)