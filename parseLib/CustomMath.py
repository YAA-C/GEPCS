from math import sqrt

class BezierCurve:
    def __init__(self, controlPoints) -> None:
        assert len(controlPoints) == 6, "This is a 6th degree bezier curve"
        self.controlPoints = controlPoints


    def curvePoints(self, t: float):
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


    def solveBezierCurveY(self, X: float):
        precision:float = 0.0001
        left: float = 0.00
        right: float = 1.00
        while (left <= right) and ((right - left) > precision):
            mid: float = (left + right) / 2
            midPoint: tuple = self.curvePoints(mid)
            print(mid, midPoint)
            if midPoint[0] < X:
                left = mid + precision
            else:
                right = mid
        return left
    

def eularDistance(X: tuple, Y: tuple) -> float:
    distance = 0
    for i in range(len(X)):
        distance += ((X[i] - Y[i]) ** 2)
    return sqrt(distance)