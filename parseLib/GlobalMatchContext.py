from .CustomDemoParser import CustomDemoParser
from .Filters import Filters
from .CustomMath import BezierCurve


class GlobalMatchContext:
    def __init__(self, parser: CustomDemoParser) -> None:
        self.parser: CustomDemoParser = parser
        self.playerBlindObjMap: dict(int, PlayerBlindContext) = dict()


    def loadContextData(self) -> None:
        for playerSteamId in self.parser.allPlayers:
            blindEvents = Filters().filterPlayerBlindEvents(blindEvents= self.parser.blindEvents, playerSteamId= playerSteamId)
            playerBlindObj: PlayerBlindContext = PlayerBlindContext(blindEvents= blindEvents)
            playerBlindObj.generatePlayerFlashedIntervals()
            self.playerBlindObjMap[playerSteamId] = playerBlindObj


    def getPlayerBlindness(self, playerSteamId: int, tick: int) -> float:
        playerBlindObj: PlayerBlindContext = self.playerBlindObjMap[playerSteamId]
        return playerBlindObj.getPlayerBlindness(tick= tick)


class PlayerBlindContext:
    def __init__(self, blindEvents: list) -> None:
        self.blindEvents: list = blindEvents
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