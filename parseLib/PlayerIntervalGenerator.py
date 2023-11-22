import pandas as pd
from .Filters import Filters

class PlayerIntervalGenerator:
    def __init__(self, hurtEvents: list, playerSteamId: int) -> None:
        self.delta = 128
        self.hurtEvents = Filters().filterWeaponHurtEvents(hurtEvents)
        self.playerSteamId = playerSteamId
        self.hurtTicks = dict()
        self.hurtIntervals = []


    def generateIntervals(self) -> None:
        intervals: list = []
        for event in self.hurtEvents:
            if event['attacker_steamid'] != self.playerSteamId:
                continue
            self.hurtTicks[event['tick']] = event
            interval = [event['tick'] - self.delta, event['tick']]
            intervals.append(interval)

        if(len(intervals) == 0):
            # No hurt event for this player registered
            return
        
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

        self.hurtIntervals = mergedIntervals

        return