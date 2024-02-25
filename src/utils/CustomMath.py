import math
from functools import cache
    

class BezierCurve:
    def __init__(self, controlPoints) -> None:
        assert len(controlPoints) == 6, "This is a 6th degree bezier curve"
        self.controlPoints = controlPoints


    @cache
    def curvePoints(self, t: float) -> tuple:
        x0, y0 = self.controlPoints[0][0], self.controlPoints[0][1]
        x1, y1 = self.controlPoints[1][0], self.controlPoints[1][1]
        x2, y2 = self.controlPoints[2][0], self.controlPoints[2][1]
        x3, y3 = self.controlPoints[3][0], self.controlPoints[3][1]
        x4, y4 = self.controlPoints[4][0], self.controlPoints[4][1]
        x5, y5 = self.controlPoints[5][0], self.controlPoints[5][1]

        firstXTerm = ((1 - t) ** 5) * x0
        secondXTerm = 5 * ((1 - t) ** 4) * t * x1
        thirdXTerm = 10 * ((1 - t) ** 3) * (t ** 2) * x2
        forthXTerm = 10 * ((1 - t) ** 2) * (t ** 3) * x3
        fifthXTerm = 5 * ((1 - t) ** 1) * (t ** 4) * x4
        sixthXTerm = (t ** 5) * x5
        
        firstYTerm = ((1 - t) ** 5) * y0
        secondYTerm = 5 * ((1 - t) ** 4) * t * y1
        thirdYTerm = 10 * ((1 - t) ** 3) * (t ** 2) * y2
        forthYTerm = 10 * ((1 - t) ** 2) * (t ** 3) * y3
        fifthYTerm = 5 * ((1 - t) ** 1) * (t ** 4) * y4
        sixthYTerm = (t ** 5) * y5

        X = firstXTerm + secondXTerm + thirdXTerm + forthXTerm + fifthXTerm + sixthXTerm
        Y = firstYTerm + secondYTerm + thirdYTerm + forthYTerm + fifthYTerm + sixthYTerm
        return (X, Y)


    @cache
    def solveBezierCurveY(self, X: float) -> float:
        precision:float = 0.0001
        left: float = 0.00
        right: float = 1.00
        while (left < right) and ((right - left) > precision):
            mid: float = (left + right) / 2
            midPoint: tuple = self.curvePoints(mid)
            if midPoint[0] < X:
                left = mid + precision
            else:
                right = mid
        return left


class UnitVector:
    def __init__(self, **kwargs) -> None:
        if ('yaw' in kwargs) and ('pitch' in kwargs):
            # using for yaw and pitch
            yaw: float = kwargs['yaw']
            pitch: float = kwargs['pitch']
            self.createFromSphericalAngles(yaw, pitch)
        elif ('fromVector' in kwargs) and ('toVector' in kwargs):
            # using for creating vector from a vector to different vector
            fromVector: list = kwargs['fromVector']
            toVector: list = kwargs['toVector']
            self.createFromCartesianCoordinates(fromVector, toVector)
        else:
            raise Exception("Please give appropriate arguments for constructing vector")


    def createFromSphericalAngles(self, yaw: float, pitch: float):
        assert (yaw >= 0 and yaw <= 360), "Yaw should be between 0 and 360 degrees"
        assert (pitch >= 0 and pitch <= 180), "Pitch should be between 0 and 180 degrees"
        yaw = math.radians(yaw)
        pitch = math.radians(pitch)
        x: float = math.sin(pitch) * math.cos(yaw)
        y: float = math.sin(pitch) * math.sin(yaw)
        z: float = math.cos(pitch)
        self.vector: list = [x, y, z]


    def createFromCartesianCoordinates(self, fromVector: list, toVector: list):
        assert (len(fromVector) == len(toVector)), f"Both vectors should be of same length, provided {len(fromVector)}, {len(toVector)}"
        vector = [x - y for x, y in zip(toVector, fromVector)]
        self.vectorLength = eularDistance(vector, [0] * len(vector))
        self.vector = [data / self.vectorLength for data in vector]


    def getLength(self) -> float:
        return 1.0
    

    def __repr__(self) -> str:
        return f"[{self.vector[0]} {self.vector[1]} {self.vector[2]}]"


    @staticmethod
    def getDotProduct(A: 'UnitVector', B: 'UnitVector') -> float:
        dotProduct: float = 0.0
        for i in range(len(A.vector)):
            dotProduct += (A.vector[i] * B.vector[i])
        return dotProduct


    @staticmethod
    def getAngleInRadians(A: 'UnitVector', B: 'UnitVector') -> float:
        dotProduct: float = clamp(UnitVector.getDotProduct(A, B), -1.0, +1.0)
        lengthProduct: float = A.getLength() * B.getLength()
        angle: float = math.acos(dotProduct / lengthProduct)
        assert (angle >= 0 and angle <= math.pi), f"angle {angle} is not in between 0 and 180 degrees"
        return angle


    @staticmethod
    def getAngleInDegrees(A: 'UnitVector', B: 'UnitVector') -> float:
        angle: float = UnitVector.getAngleInRadians(A, B)
        return math.degrees(angle)


def getArcLength(r: float, A: UnitVector, B: UnitVector) -> float:
    angle = UnitVector.getAngleInRadians(A, B)
    return r * angle


def eularDistance(X: tuple, Y: tuple) -> float:
    distance = 0
    for i in range(len(X)):
        distance += ((X[i] - Y[i]) ** 2)
    return math.sqrt(distance)


def clamp(value: float, minValue: float, maxValue: float) -> float:
    return min(max(value, minValue), maxValue)


def interpolate(distanceFromA: float, totalDistance: float, positionA: tuple, positionB: float) -> float:
    assert len(positionA) == len(positionB), f"Wrong sized vectors A: {len(positionA)} B: {len(positionB)}"
    t: float = (distanceFromA / totalDistance)
    return ((t * dimensionA + (1.00 - t) * dimentionB) for dimensionA, dimentionB in zip(positionA, positionB))


def heronsArea(sideA: float, sideB: float, sideC: float) -> float:
    perimeterHalf: float = (sideA + sideB + sideC) / 2.00
    area: float = math.sqrt(perimeterHalf * (perimeterHalf - sideA) * (perimeterHalf - sideB) * (perimeterHalf - sideC))
    return area


def heightOfTriangle(sideA: float, sideB: float, baseSide: float) -> float:
    area: float = heronsArea(sideA, sideB, baseSide)
    height: float = (area * 2.00) / baseSide
    return height