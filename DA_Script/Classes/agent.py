import shapely

# This class will serve to define the Agents in a scenario, such as a vehicle or pedestrian.

class Agent:
    def __init__(self, agentType: str, id: int, length: float, width: float, height: float,
                 center: shapely.Point, heading: float, lonSpeed: float, latSpeed: float, speed: float, lonAccel: float, latAccel: float, accel: float, longitude: float, latitude: float):
        
        self.agentType = agentType
        self.id = id
        self.length = length
        self.width = width
        self.height = height

        # -- Kinematics --
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

    def getKinematics(self):
        return 0
    
    def getMetrics(self, metrics):
        return 0
    
    def setAgentType(self, agentType: str):
        self.agentType = agentType

    def setId(self, id: int):
        self.id = id

    def setLength(self, length: float):
        self.length = length

    def setWidth(self, width: float):
        self.width = width

    def setHeight(self, height: float):
        self.height = height

    # -- Kinematics --
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