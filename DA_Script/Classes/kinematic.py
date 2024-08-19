import shapely

# The Kinematic class is used to store

class Kinematic:
    # Given an x, y, heading, and dimensions, a vehicle is constructed
    def __init__(self, center: shapely.Point, heading: float, lonSpeed: float, latSpeed: float, speed: float, lonAccel: float, latAccel: float, accel: float, longitude: float, latitude: float):
        self.center = center
        self.heading = heading 
        self.lonSpeed = lonSpeed
        self.latSpeed = latSpeed
        self.speed = speed
        self.lonAccel = lonAccel
        self.latAccel = latAccel
        self.accel = accel
        self.longitude = longitude
        self.latitude = latitude

    def setCenter(self, x: float, y: float):
        self.center = shapely.Point(x, y)

    def setHeading(self, heading: float):
        self.heading = heading

    def setLonSpeed(self, lonSpeed: float):
        self.lonSpeed = lonSpeed

    def setLatSpeed(self, latSpeed: float):
        self.latSpeed = latSpeed

    def setSpeed(self, speed: float):
        self.speed = speed

    def setLonAccel(self, lonAccel: float):
        self.lonAccel = lonAccel

    def setLatAccel(self, latAccel: float):
        self.latAccel = latAccel

    def setAccel(self, accel: float):
        self.accel = accel

    def setLongitude(self, longitude: float):
        self.longitude = longitude

    def setLatitude(self, latitude: float):
        self.latitude = latitude
