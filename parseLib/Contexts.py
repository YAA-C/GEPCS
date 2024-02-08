from .CustomDemoParser import CustomDemoParser


class PrefixRoundContext:
    def __init__(self, parser: CustomDemoParser) -> None:
        self.roundTicks: list = parser.roundTicks
        self.roundData: list = []
        for _ in range(len(self.roundTicks)):
            self.roundData.append(list())


    def findRoundIndex(self, tick: int) -> int:        
        left: int = 0 
        right: int = len(self.roundTicks) - 1
        roundIndex: int = -1
        while left <= right:
            mid: int = (left + right) // 2
            if self.roundTicks[mid] <= int(tick):
                roundIndex = mid
                left = mid + 1
            else:
                right = mid - 1

        assert roundIndex != -1, "Round Index can't be negative"
        return roundIndex


    def appendDataAtTick(self, tick: int, data: int) -> None:
        roundIndex: int = self.findRoundIndex(tick= tick)
        self.roundData[roundIndex].append([tick, data])


    def getDataTillTick(self, tick: int) -> int:
        roundIndex: int = self.findRoundIndex(tick= tick)
        left: int = 0
        right: int = len(self.roundData[roundIndex]) - 1
        data: int = 0
        while left <= right:
            mid: int = (left + right) // 2
            if(self.roundData[roundIndex][mid][0] <= int(tick)):
                data = self.roundData[roundIndex][mid][1]
                left = mid + 1
            else:
                right = mid - 1

        return data


    def calculatePrefixSum(self) -> None:
        for i in range(len(self.roundData)):
            for j in range(1, len(self.roundData[i])):
                self.roundData[i][j][1] += self.roundData[i][j - 1][1]



class PrefixMatchContext:
    def __init__(self) -> None:
        self.matchData: list = list()


    def appendDataAtTick(self, tick: int, data: int) -> None:
        self.matchData.append([tick, data])


    def getDataTillTick(self, tick: int) -> int:
        left: int = 0
        right: int = len(self.matchData) - 1
        data: int = 0
        while left <= right:
            mid: int = (left + right) // 2
            if(self.matchData[mid][0] <= int(tick)):
                data = self.matchData[mid][1]
                left = mid + 1
            else:
                right = mid - 1

        return data


    def calculatePrefixSum(self) -> None:
        for i in range(1, len(self.matchData)):
            self.matchData[i][1] += self.matchData[i - 1][1]


class StoreRoundContext:
    def __init__(self, parser: CustomDemoParser) -> None:
        self.roundTicks: list = parser.roundTicks
        self.roundData: list = []
        for _ in range(len(self.roundTicks)):
            self.roundData.append(list())


    def findRoundIndex(self, tick: int) -> int:        
        left: int = 0 
        right: int = len(self.roundTicks) - 1
        roundIndex: int = -1
        while left <= right:
            mid: int = (left + right) // 2
            if self.roundTicks[mid] <= int(tick):
                roundIndex = mid
                left = mid + 1
            else:
                right = mid - 1

        assert roundIndex != -1, "Round Index can't be negative"
        return roundIndex


    def appendDataAtTick(self, tick: int, data: tuple) -> None:
        roundIndex: int = self.findRoundIndex(tick= tick)
        self.roundData[roundIndex].append([tick, data])


    def getDataOfRoundWithTick(self, tick: int) -> list:
        roundIndex: int = self.findRoundIndex(tick= tick)
        '''
        # Premature Optimization
        startIndex, endIndex = 0, len(self.roundData[roundIndex]) - 1
        left: int = 0
        right: int = len(self.roundData[roundIndex]) - 1

        # find index of first smoke which is not expired
        while left <= right:
            mid: int = (left + right) // 2
            if self.roundData[roundIndex][mid][1][0] >= tick:
                startIndex = mid
                right = mid - 1
            else:
                left = mid + 1

        left: int = 0
        right: int = len(self.roundData[roundIndex]) - 1
        
        # find index of first smoke which is not yet thrown
        while left <= right:
            mid: int = (left + right) // 2
            if self.roundData[roundIndex][mid][0] > tick:
                endIndex = mid
                right = mid - 1
            else:
                left = mid + 1

        allData: list = []
        for i in range(startIndex, endIndex):
            allData.append(self.roundData[roundIndex][i])

        return allData()
        '''
        return [data for data in self.roundData[roundIndex] if (data[0] <= tick and data[1][0] >= tick)]