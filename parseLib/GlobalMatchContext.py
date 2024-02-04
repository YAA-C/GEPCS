from .CustomDemoParser import CustomDemoParser
from .Filters import Filters
from .CustomMath import BezierCurve
from .Contexts import StoreRoundContext
from math import ceil

class GlobalMatchContext:
    def __init__(self, parser: CustomDemoParser) -> None:
        self.parser: CustomDemoParser = parser
        self.playerBlindObjMap: dict(int, PlayerBlindContext) = dict()


    def loadContextData(self) -> None:
        for playerSteamId in self.parser.allPlayers:
            # Every precomputation about flashbangs
            playerBlindObj: PlayerBlindContext = PlayerBlindContext(parser= self.parser, playerSteamId= playerSteamId)
            playerBlindObj.generatePlayerFlashedIntervals()
            self.playerBlindObjMap[playerSteamId] = playerBlindObj


    def getPlayerBlindness(self, playerSteamId: int, tick: int) -> float:
        playerBlindObj: PlayerBlindContext = self.playerBlindObjMap[playerSteamId]
        return playerBlindObj.getPlayerBlindness(tick= tick)


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
            intervalEnd: int = int(intervalStart + ceil(float(event['blind_duration'])) * 128.00)
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
    

class PlayerSmokeContext:
    def __init__(self, parser: CustomDemoParser) -> None:
        self.smokeEvents: list = parser.smokeEvents
        self.smokeContext: StoreRoundContext = StoreRoundContext(parser= parser)
        

    def loadContextData(self) -> None:
        for event in self.smokeEvents:
            smokeStart: int = int(event['tick'])
            smokeEnd: int = int(smokeStart + 128.0 * 18.0)
            data = (smokeEnd, event['x'], event['y'], event['z'])
            self.smokeContext.appendDataAtTick(smokeStart, data)


    def getPlayerSmokeVisibility(self, tick: int, playerLocation: tuple) -> bool:
        possibleSmokes: list = self.smokeContext.getDataOfRoundWithTick(tick)
        # process smokes now :) (btw smoke bezier needed ?)