import config
import collections
import math
import shapely
from shapely import affinity



class vehicle(object):
    Side = collections.namedtuple('Side', ['point', 'line'])

    def __init__(self, x: float = 0.0, y: float = 0.0, length: float = 0.0, width: float = 0.0, heading: float = 0.0, type: str = "", id: str = ""):
        self.center = shapely.Point(x, y)
        self.heading = heading
        
        self.length = length
        self.width = width

        self.speed = 0 # m/s
        self.speed_lon = 0 # m/s
        self.speed_lat = 0 # m/s

        self.acceleration = 0 # m/s^2
        self.acceleration_lon = 0 # m/s^2
        self.acceleration_lat = 0 # m/s^2

        self.safety_envelope_variables = {
            "lateral_fluctuation_margin": 0,
            "vehicle_response_time": 0,
            
            "lon_max_accel": 0,
            "lon_min_decel": 0,
            "lon_max_decel": 0,
            
            "lat_max_accel": 0,
            "lat_min_decel": 0,
            "lat_max_decel": 0
        }

        self.type = type
        self.id = id

    def set_center(self, x: float = 0.0, y: float = 0.0):
        self.center = shapely.Point(x, y)

    def set_heading(self, heading: float = 0.0):
        # Radians are used
        self.heading = heading

    def set_speed(self, speed: float = 0.0):
        self.speed = speed

    def set_speed_lon(self, speed_lon: float = 0.0):
        self.speed_lon = speed_lon

    def set_speed_lat(self, speed_lat: float = 0.0):
        self.speed_lat = speed_lat

    def set_acceleration(self, acceleration: float = 0.0):
        self.acceleration = acceleration

    def set_acceleration_lon(self, acceleration_lon: float = 0.0):
        self.acceleration_lon = acceleration_lon

    def set_acceleration_lat(self, acceleration_lat: float = 0.0):
        self.acceleration_lat = acceleration_lat

    def get_bbox(self):
        length = self.length
        width = self.width

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

        # The angle is corrected by adding pi/2, this is inconsequential but will be fixed in a future release.
        return affinity.rotate(rect, angle + math.pi/2, self.center, use_radians=True)

    def get_mm_bbox(self):
        length = self.length
        width = self.width

        angle = self.heading

        if self.type == 'vehicle':
            if self.speed_lon < 2:
                bbox_distance = 0.3
            else:
                bbox_distance = 0.046 * self.speed_lon + 0.131
        elif self.type == 'pedestrian':
            if self.speed_lon < 1.5:
                bbox_distance = 0.2
            else:
                bbox_distance = 0.188 * self.speed_lon - 0.076

        tr_x = self.center.x + width/2 + bbox_distance
        tr_y = self.center.y + length/2 + bbox_distance
        tr = shapely.Point(tr_x, tr_y)

        # Top left corner
        tl_x = self.center.x - width/2 - bbox_distance
        tl_y = self.center.y + length/2 + bbox_distance
        tl = shapely.Point(tl_x, tl_y)

        # Bottom left corner
        bl_x = self.center.x - width/2 - bbox_distance
        bl_y = self.center.y - length/2 - bbox_distance
        bl = shapely.Point(bl_x, bl_y)

        # Bottom right corner
        br_x = self.center.x + width/2 + bbox_distance
        br_y = self.center.y - length/2 - bbox_distance
        br = shapely.Point(br_x, br_y)

        rect = shapely.Polygon([bl, tl, tr, br])

        # Rotate to match the heading angle
        return affinity.rotate(rect.buffer(bbox_distance), angle, 'centroid', use_radians=True)

    def get_rss_ped_bbox(self):
        length = self.length
        width = self.width

        angle = self.heading

        if self.speed_lon > 0:
            p1_x = self.center.x
            p1_y = self.center.y
            p1 = shapely.Point(p1_x, p1_y)

            p2_x = self.center.x + width * 5
            p2_y = self.center.y + length * 4
            p2 = shapely.Point(p2_x, p2_y)

            p3_x = self.center.x + width * 4
            p3_y = self.center.y + length * 5
            p3 = shapely.Point(p3_x, p3_y)

            p4_x = self.center.x + width * 2
            p4_y = self.center.y + length * 6
            p4 = shapely.Point(p4_x, p4_y)

            p5_x = self.center.x + width * 0
            p5_y = self.center.y + length * 6.5
            p5 = shapely.Point(p5_x, p5_y)

            p6_x = self.center.x + width * -2
            p6_y = self.center.y + length * 6
            p6 = shapely.Point(p6_x, p6_y)

            p7_x = self.center.x + width * -4
            p7_y = self.center.y + length * 5
            p7 = shapely.Point(p7_x, p7_y)

            p8_x = self.center.x + width * -5
            p8_y = self.center.y + length * 4
            p8 = shapely.Point(p8_x, p8_y)

            bbox = shapely.Polygon([p1, p2, p3, p4, p5, p6, p7, p8])
        else:
            bbox = self.center.buffer(2.0)

        return affinity.rotate(bbox, angle, self.center, use_radians=True)

    def get_rss_vehicle_bbox(self):
        length = self.length
        width = self.width

        angle = self.heading

        p1_x = self.center.x
        p1_y = self.center.y
        p1 = shapely.Point(p1_x, p1_y)

        p2_x = self.center.x + width * 2
        p2_y = self.center.y + width * 2
        p2 = shapely.Point(p2_x, p2_y)

        p3_x = self.center.x + width * 3
        p3_y = self.center.y + width * 2.2
        p3 = shapely.Point(p3_x, p3_y)

        p4_x = self.center.x + width * 2.8
        p4_y = self.center.y + width * 4.5
        p4 = shapely.Point(p4_x, p4_y)

        p5_x = self.center.x + width * 3
        p5_y = self.center.y + width * 7
        p5 = shapely.Point(p5_x, p5_y)

        p6_x = self.center.x + width * 2
        p6_y = self.center.y + width * 8
        p6 = shapely.Point(p6_x, p6_y)

        p7_x = self.center.x + width * 0
        p7_y = self.center.y + width * 8.5
        p7 = shapely.Point(p7_x, p7_y)

        p8_x = self.center.x + width * -2
        p8_y = self.center.y + width * 8
        p8 = shapely.Point(p8_x, p8_y)

        p9_x = self.center.x + width * -3
        p9_y = self.center.y + width * 7
        p9 = shapely.Point(p9_x, p9_y)

        p10_x = self.center.x + width * -2.8
        p10_y = self.center.y + width * 4.5
        p10 = shapely.Point(p10_x, p10_y)

        p11_x = self.center.x + width * -3
        p11_y = self.center.y + width * 2.2
        p11 = shapely.Point(p11_x, p11_y)

        p12_x = self.center.x + width * -2
        p12_y = self.center.y + width * 2
        p12 = shapely.Point(p12_x, p12_y)

        bbox = shapely.Polygon([p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12])

        if self.speed_lon > 3:
            bbox = affinity.scale(bbox, xfact=self.speed_lon/20, yfact=self.speed_lon/20, origin=self.center)
        else:
            bbox = affinity.scale(bbox, xfact=3/20, yfact=3/20, origin=self.center)

        return affinity.rotate(bbox, angle, self.center, use_radians=True)
    
    def front_bumper(self):
        length = self.length
        width= self.width

        fb = shapely.Point(self.center.x + length/2, self.center.y)

        end_point1 = shapely.Point(fb.x, fb.y + width/2)
        end_point2 = shapely.Point(fb.x, fb.y - width/2)

        fbr = affinity.rotate(geom=fb, angle=self.heading, origin=self.center, use_radians=True)

        fbl = shapely.LineString([[end_point1.x, end_point1.y], [end_point2.x, end_point2.y]])

        fblr = affinity.rotate(geom=fbl, angle=self.heading, origin=self.center, use_radians=True)

        # fbr is the point and flbr is the length of the bumper as a line
        return self.Side(fbr, fblr)
    
    def rear_bumper(self):
        length = self.length
        width= self.width

        rb = shapely.Point(self.center.x - length/2, self.center.y)

        end_point1 = shapely.Point(rb.x, rb.y + width/2)
        end_point2 = shapely.Point(rb.x, rb.y - width/2)

        rbr = affinity.rotate(geom=rb, angle=self.heading, origin=self.center, use_radians=True)

        rbl = shapely.LineString([[end_point1.x, end_point1.y], [end_point2.x, end_point2.y]])

        rblr = affinity.rotate(geom=rbl, angle=self.heading, origin=self.center, use_radians=True)

        return self.Side(rbr, rblr)
    
    def left_side(self):
        length = self.length
        width= self.width

        ls = shapely.Point(self.center.x, self.center.y + width/2)

        end_point1 = shapely.Point(ls.x + length/2, ls.y)
        end_point2 = shapely.Point(ls.x - length/2, ls.y)

        lsr = affinity.rotate(geom=ls, angle=self.heading, origin=self.center, use_radians=True)

        lsl = shapely.LineString([[end_point1.x, end_point1.y], [end_point2.x, end_point2.y]])

        lslr = affinity.rotate(geom=lsl, angle=self.heading, origin=self.center, use_radians=True)

        return self.Side(lsr, lslr)

    def right_side(self):
        length = self.length
        width= self.width

        rs = shapely.Point(self.center.x, self.center.y - width/2)

        end_point1 = shapely.Point(rs.x + length/2, rs.y)
        end_point2 = shapely.Point(rs.x - length/2, rs.y)

        rsr = affinity.rotate(geom=rs, angle=self.heading, origin=self.center, use_radians=True)

        rsl = shapely.LineString([[end_point1.x, end_point1.y], [end_point2.x, end_point2.y]])

        rslr = affinity.rotate(geom=rsl, angle=self.heading, origin=self.center, use_radians=True)

        return self.Side(rsr, rslr)

    def heading_vector(self):
        #############
        #     |     #
        #     |     #
        #     |     #
        #     ▮     #
        #############
        length = config.heading_vector_length

        end_point = shapely.Point(self.center.x + length, self.center.y)

        line = shapely.LineString([[self.center.x, self.center.y], [end_point.x, end_point.y]])
        
        return affinity.rotate(line, self.heading, origin=self.center, use_radians=True)

    def front_bumper_line(self):
        length = config.bumper_line_length
        end_point1 = shapely.Point(self.front_bumper().point.x, self.front_bumper().point.y + length/2)
        end_point2 = shapely.Point(self.front_bumper().point.x, self.front_bumper().point.y - length/2)

        line = shapely.LineString([end_point1, end_point2])

        return affinity.rotate(line, self.heading, origin=self.front_bumper().point, use_radians=True)

    def rear_bumper_line(self):
        length = config.bumper_line_length
        end_point1 = shapely.Point(self.rear_bumper().point.x, self.rear_bumper().point.y + length/2)
        end_point2 = shapely.Point(self.rear_bumper().point.x, self.rear_bumper().point.y - length/2)

        line = shapely.LineString([end_point1, end_point2])

        return affinity.rotate(line, self.heading, origin=self.rear_bumper().point, use_radians=True)

    def left_side_line(self):
        length = config.side_line_length
        end_point1 = shapely.Point(self.left_side().point.x + length, self.left_side().point.y)
        end_point2 = shapely.Point(self.left_side().point.x - self.length/2, self.left_side().point.y)

        line = shapely.LineString([end_point1, end_point2])

        return affinity.rotate(line, self.heading, origin=self.left_side().point, use_radians=True)
  
    def right_side_line(self):
        length = config.side_line_length
        end_point1 = shapely.Point(self.right_side().point.x + length, self.right_side().point.y)
        end_point2 = shapely.Point(self.right_side().point.x - self.length/2, self.right_side().point.y)

        line = shapely.LineString([end_point1, end_point2])

        return affinity.rotate(line, self.heading, origin=self.right_side().point, use_radians=True)
    
    def path_polygon(self):
        return shapely.Polygon([*list(self.left_side_line().coords), *list(self.right_side_line().coords)[::-1]])