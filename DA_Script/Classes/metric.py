class Metric:
    # Given a name, violation, and magnitude, create a Metric
    def __init__(self, name: str, violation: bool, magnitude: float):
        self.name = name
        self.violation = violation
        self.magnitude = magnitude

    def setName(self, name: str):
        self.name = name

    def setWidth(self, violation: bool):
        self.violation = violation

    def setHeight(self, magnitude: float):
        self.magnitude = magnitude