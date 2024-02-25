from .CustomDemoParser import CustomDemoParser
from .Filters import Filters
from .utils.CustomMath import BezierCurve, eularDistance, heightOfTriangle, UnitVector
from .Contexts import StoreRoundContext

class GlobalMatchContext:
    def __init__(self, parser: CustomDemoParser) -> None:
        self.parser: CustomDemoParser = parser
        self.playerBlindObjMap: dict[int, PlayerBlindContext] = dict()
        self.matchSmokeObj: MatchSmokeContext = MatchSmokeContext(parser= parser)


    def loadContextData(self) -> None:
        for playerSteamId in self.parser.allPlayers:
            # Every precomputation about flashbangs
            playerBlindObj: PlayerBlindContext = PlayerBlindContext(parser= self.parser, playerSteamId= playerSteamId)
            playerBlindObj.generatePlayerFlashedIntervals()
            self.playerBlindObjMap[playerSteamId] = playerBlindObj
        self.matchSmokeObj.loadContextData()


    def getPlayerBlindness(self, playerSteamId: int, tick: int) -> float:
        playerBlindObj: PlayerBlindContext = self.playerBlindObjMap[playerSteamId]
        return playerBlindObj.getPlayerBlindness(tick= tick)


    def getIsSmokeBetweenPlayers(self, tick: int, playerLocationA: tuple, playerLocationB: tuple) -> bool:
        return self.matchSmokeObj.getPlayerSmokeVisibility(tick, playerLocationA, playerLocationB)


class PlayerBlindContext:
    def __init__(self, parser: CustomDemoParser, playerSteamId: int) -> None:
        self.blindEvents: list = Filters().filterPlayerBlindEvents(blindEvents= parser.blindEvents, playerSteamId= playerSteamId)
        self.blindTicks: dict = dict()
        self.flashbangFXControlPoints = (
            (0, 1),
            (0.77, 1),
            (0.27, 1),
            (0.75, 0.03),
            (0.35, 0.03),
            (1, 0),
        )
        self.blindBezierCurve: BezierCurve = BezierCurve(controlPoints= self.flashbangFXControlPoints)


    def generatePlayerFlashedIntervals(self) -> None:
        for event in self.blindEvents:
            intervalStart: int = int(event['tick'])
            intervalEnd: int = int(intervalStart + float(event['blind_duration']) * 128.00)
            interval = (intervalStart, intervalEnd)

            start, end = interval[0], interval[1]
            for tick in range(start, end + 1):
                if tick not in self.blindTicks:
                    self.blindTicks[tick] = 0

                timeRatio: float = float(tick - start) / float(end - start)
                bezierT = self.blindBezierCurve.solveBezierCurveY(X= timeRatio)
                _, Y = self.blindBezierCurve.curvePoints(t= bezierT)
                self.blindTicks[tick] = max(self.blindTicks[tick], Y)


    def getPlayerBlindness(self, tick: int) -> float:
        if tick not in self.blindTicks:
            # Player not blinded at all
            return 0.00
        return self.blindTicks[tick]
    

class MatchSmokeContext:
    def __init__(self, parser: CustomDemoParser) -> None:
        self.smokeEvents: list = parser.smokeEvents
        self.smokeContext: StoreRoundContext = StoreRoundContext(parser= parser)
        

    def loadContextData(self) -> None:
        for event in self.smokeEvents:
            smokeStart: int = int(event['tick'])
            smokeEnd: int = int(smokeStart + 128.0 * 18.0)
            data = (smokeEnd, event['x'], event['y'], event['z'])
            self.smokeContext.appendDataAtTick(smokeStart, data)


    # optimizations of getPlayerSmokeVisibility() done with height of triangle in 3D space
    # TC: O(smokes * c)
    def getPlayerSmokeVisibility(self, tick: int, playerLocation: tuple, targetPlayerLocation: tuple) -> bool:
        possibleSmokes: list = self.smokeContext.getDataOfRoundWithTick(tick)
        smokeRadius: float = 144.00

        baseDistance: float = eularDistance(playerLocation, targetPlayerLocation)
        playerToTargetVector: UnitVector = UnitVector(fromVector= playerLocation, toVector= targetPlayerLocation)
        targetToPlayerVector: UnitVector = UnitVector(fromVector= targetPlayerLocation, toVector= playerLocation)

        for smokeData in possibleSmokes:
            smokeLocation = (smokeData[1][1], smokeData[1][2], smokeData[1][3])
            
            playerToSmokeDistance: float = eularDistance(playerLocation, smokeLocation)
            targetPlayerToSmokeDistance: float = eularDistance(targetPlayerLocation, smokeLocation)

            playerToSmokeVector: UnitVector = UnitVector(fromVector= playerLocation, toVector= smokeLocation)
            targetToSmokeVector: UnitVector = UnitVector(fromVector= targetPlayerLocation, toVector= smokeLocation)

            if UnitVector.getAngleInDegrees(playerToTargetVector, playerToSmokeVector) > 90.00:
                if(playerToSmokeDistance <= smokeRadius):
                    return True
            elif UnitVector.getAngleInDegrees(targetToPlayerVector, targetToSmokeVector) > 90.00:
                if(targetPlayerToSmokeDistance <= smokeRadius):
                    return True
            else:
                distanceToSmoke: float = heightOfTriangle(playerToSmokeDistance, targetPlayerToSmokeDistance, baseDistance)
                if distanceToSmoke <= smokeRadius:
                    return True
                
        return False
    

    # TC: O(smokes * log(distance betweeen target and player))
    # def getPlayerSmokeVisibility(self, tick: int, playerLocation: tuple, targetPlayerLocation: tuple) -> bool:
    #     possibleSmokes: list = self.smokeContext.getDataOfRoundWithTick(tick)

    #     for smokeData in possibleSmokes:
    #         smokeX, smokeY, smokeZ = smokeData[1][1], smokeData[1][2], smokeData[1][3]
            
    #         totalDistance: int = int(ceil(eularDistance(playerLocation, targetPlayerLocation)))
    #         left: int = 0
    #         right: int = totalDistance

    #         while left < right:
    #             midLeft: int = (left + right) // 2
    #             midX, midY, midZ = interpolate(midLeft, totalDistance, playerLocation, targetPlayerLocation)
    #             distanceToSmoke1: float = eularDistance((midX, midY, midZ), (smokeX, smokeY, smokeZ))
                
    #             midRight: int = (midLeft + 1)
    #             midX, midY, midZ = interpolate(midRight, totalDistance, playerLocation, targetPlayerLocation)
    #             distanceToSmoke2: float = eularDistance((midX, midY, midZ), (smokeX, smokeY, smokeZ))

    #             if distanceToSmoke1 <= 144.00 or distanceToSmoke2 <= 144.00:
    #                 return True
                
    #             if distanceToSmoke1 <= distanceToSmoke2:
    #                 right = midLeft
    #             else:
    #                 left = midLeft + 1
    #     return False