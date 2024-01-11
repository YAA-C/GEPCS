from .Filters import Filters
from .CustomDemoParser import CustomDemoParser
<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes

class PlayerMatchContext:
    def __init__(self, parser: CustomDemoParser, playerSteamId: int, targetSteamId: int) -> None:
        self.delta = 128
        self.hurtEvents = Filters().filterPlayerHurtEvents(hurtEvents= parser.hurtEvents, playerSteamId= playerSteamId, targetSteamId= targetSteamId)
        self.fireEvents = Filters().filterPlayerFireEvents(fireEvents= parser.fireEvents, playerSteamId= playerSteamId)
        self.playerSteamId = playerSteamId
<<<<<<< Updated upstream
        self.targetSteamId = targetSteamId
=======
        self.fireTicks = set()


    def updateTarget(self, targetSteamId: int) -> None:
>>>>>>> Stashed changes
        self.hurtTicks = dict()
        self.fireTicks = set()
        self.hurtIntervals = []


    def generatePlayerHurtIntervals(self) -> None:
        intervals: list = []
        for event in self.hurtEvents:
            self.hurtTicks[event['tick']] = event
            interval = [event['tick'] - self.delta, event['tick']]
            intervals.append(interval)

        if(len(intervals) == 0):
            # No hurt event for this player registered
            return
        self.hurtIntervals = self.mergeOverlappingIntervals(intervals= intervals)


    def generateWeaponFireTicks(self) -> None:
        self.fireTicks = set([event['tick'] for event in self.fireEvents])


    def generatePlayerJumpIntervals(self) -> None:
        pass


    def generatePlayerCrouchIntervals(self) -> None:
        pass


<<<<<<< Updated upstream
    def generatePlayerFlashedIntervals(self) -> None:
        pass


=======
>>>>>>> Stashed changes
    def mergeOverlappingIntervals(self, intervals: list) -> list:
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