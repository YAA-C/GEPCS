from .Filters import Filters
from .CustomDemoParser import CustomDemoParser

class PlayerMatchContext:
    def __init__(self, parser: CustomDemoParser, playerSteamId: int) -> None:
        self.tickDelta = 128
        self.allHurtEvents: list = parser.hurtEvents
        self.fireEvents = Filters().filterPlayerFireEvents(fireEvents= parser.fireEvents, playerSteamId= playerSteamId)
        self.playerSteamId = playerSteamId
        self.fireTicks = set()


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