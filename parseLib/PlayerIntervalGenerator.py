import pandas as pd

class PlayerIntervalGenerator:
    def __init__(self, hurtEvents: list, parsedDf: pd.DataFrame, playerSteamId: int, label: bool) -> None:
        self.delta = 128
        self.separation_marker: pd.DataFrame = pd.DataFrame([[]])
        self.hurtEvents = hurtEvents
        self.parsedDf = parsedDf
        self.playerSteamId = playerSteamId
        self.label = label


    def generateIntervals(self) -> list:
        intervals: list = []
        for event in self.hurtEvents:
            if event['attacker_steamid'] != self.playerSteamId:
                continue
            interval = [event['tick'] - self.delta, event['tick']]
            intervals.append(interval)

        if(len(intervals) == 0):
            # No hurt event for this player registered
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

        mergedIntervalsFilled: list = []
        for interval in mergedIntervals:
            tmpDf = self.getIntervalData(interval)
            mergedIntervalsFilled.append(tmpDf)

        return mergedIntervalsFilled
    

    def getIntervalData(self, interval: list) -> pd.DataFrame:
        requiredTicks = list(range(interval[0], interval[1] + 1))
        intervalDf: pd.DataFrame = self.parsedDf.loc[(self.parsedDf['tick'].isin(requiredTicks)) & \
                                                (self.parsedDf['steamid'] == self.playerSteamId)]\
                                                .copy()
        intervalDf = pd.concat([intervalDf, self.separation_marker], ignore_index=True)
        intervalDf['label'] = self.label
        return intervalDf