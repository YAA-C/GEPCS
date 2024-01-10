from .Filters import Filters
from .CustomDemoParser import CustomDemoParser
from .CustomMath import BezierCurve

class PlayerMatchContext:
    def __init__(self, parser: CustomDemoParser, playerSteamId: int) -> None:
        self.tickDelta = 128
        self.allHurtEvents: list = parser.hurtEvents
        self.fireEvents = Filters().filterPlayerFireEvents(fireEvents= parser.fireEvents, playerSteamId= playerSteamId)
        self.blindEvents = Filters().filterPlayerBlindEvents(blindEvents= parser.blindEvents, playerSteamId= playerSteamId)
        self.playerSteamId = playerSteamId
        self.fireTicks = set()
        self.blindTicks = dict()
        self.flashbangFXControlPoints = (
            (0, 1),
            (0.77, 1),
            (0.27, 1),
            (0.75, 0.03),
            (0.35, 0.03),
            (1, 0),
        )
        self.blindBezierCurve: BezierCurve = BezierCurve(controlPoints= self.flashbangFXControlPoints)


    def updateTarget(self, targetSteamId: int) -> None:
        self.hurtTicks = dict()
        self.hurtIntervals = []
        self.hurtEvents = Filters().filterPlayerHurtEvents(hurtEvents= self.allHurtEvents, playerSteamId= self.playerSteamId, targetSteamId= targetSteamId)
        self.generatePlayerHurtIntervals()


    def generatePlayerHurtIntervals(self) -> None:
        intervals: list = []
        for event in self.hurtEvents:
            self.hurtTicks[event['tick']] = event
            interval = (event['tick'] - self.tickDelta, event['tick'])
            intervals.append(interval)

        self.hurtIntervals = self.mergeOverlappingIntervals(intervals= intervals)


    def generateWeaponFireTicks(self) -> None:
        self.fireTicks = set([event['tick'] for event in self.fireEvents])


    def generatePlayerJumpIntervals(self) -> None:
        pass


    def generatePlayerCrouchIntervals(self) -> None:
        pass


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


    def mergeOverlappingIntervals(self, intervals: list) -> list:
        if len(intervals) == 0:
            return []
        
        intervals = sorted(intervals)
        mergedIntervals = []
        start = intervals[0][0]
        end = intervals[0][1]
        for i in range(1, len(intervals)):
            if intervals[i][0] > end:
                mergedIntervals.append([start, end])
                start = intervals[i][0]
                end = intervals[i][1]
            else:
                end = max(end, intervals[i][1])
        mergedIntervals.append([start, end])
        return mergedIntervals