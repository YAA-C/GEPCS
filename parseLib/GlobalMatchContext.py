from .CustomDemoParser import CustomDemoParser
from .Filters import Filters
from .CustomMath import BezierCurve


class GlobalMatchContext:
    def __init__(self, parser: CustomDemoParser) -> None:
        self.parser: CustomDemoParser = parser
        self.playerBlindObjMap: dict(int, PlayerBlindContext) = dict()
        self.playerDamageUtilityMap: dict(int, PlayerDamageUtiltyContext) = dict()
        self.playerSupportUtilityMap: dict(int, PlayerSupportUtilityContext) = dict()


    def loadContextData(self) -> None:
        for playerSteamId in self.parser.allPlayers:
            # Every precomputation about flashbangs
            playerBlindObj: PlayerBlindContext = PlayerBlindContext(parser= self.parser, playerSteamId= playerSteamId)
            playerBlindObj.generatePlayerFlashedIntervals()
            self.playerBlindObjMap[playerSteamId] = playerBlindObj

            # Every precomputation about utility damage
            playerDamageUtilityObj: PlayerDamageUtiltyContext = PlayerDamageUtiltyContext(parser= self.parser, playerSteamId= playerSteamId)
            playerDamageUtilityObj.loadContextData()
            self.playerDamageUtilityMap[playerSteamId] = playerDamageUtilityObj

            # Every precomputation about utility support
            playerSupportUtilityObj: PlayerSupportUtilityContext = PlayerSupportUtilityContext(parser= self.parser, playerSteamId= playerSteamId)
            playerSupportUtilityObj.loadContextData()
            self.playerSupportUtilityMap[playerSteamId] = playerSupportUtilityObj


    def getPlayerBlindness(self, playerSteamId: int, tick: int) -> float:
        playerBlindObj: PlayerBlindContext = self.playerBlindObjMap[playerSteamId]
        return playerBlindObj.getPlayerBlindness(tick= tick)


    def getPlayerDamageDoneTillTick(self, playerSteamId: int, tick: int) -> int:
        playerDamageUtilityObj: PlayerDamageUtiltyContext = self.playerDamageUtilityMap[playerSteamId]
        return playerDamageUtilityObj.getDamageDoneTillTick(tick= tick)


    def getPlayerSupportDoneTillTick(self, playerSteamId: int, tick: int) -> int:
        playerSupportUtility: PlayerSupportUtilityContext = self.playerSupportUtilityMap[playerSteamId]
        return playerSupportUtility.getSupportDoneTillTick(tick= tick)


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
    

class RoundContext:
    def __init__(self, parser: CustomDemoParser) -> None:
        self.roundTicks: list = parser.roundTicks
        self.roundIntervals: list = []
        for _ in range(len(self.roundTicks)):
            self.roundIntervals.append(list())


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
        self.roundIntervals[roundIndex].append([tick, data])


    def getDataTillTick(self, tick: int) -> None:
        roundIndex: int = self.findRoundIndex(tick= tick)
        left: int = 0
        right: int = len(self.roundIntervals[roundIndex]) - 1
        data: int = 0
        while left <= right:
            mid: int = (left + right) // 2
            if(self.roundIntervals[roundIndex][mid][0] <= int(tick)):
                data = self.roundIntervals[roundIndex][mid][1]
                left = mid + 1
            else:
                right = mid - 1

        return data


    def calculatePrefixSum(self) -> None:
        for i in range(len(self.roundIntervals)):
            for j in range(1, len(self.roundIntervals[i])):
                self.roundIntervals[i][j][1] += self.roundIntervals[i][j - 1][1]


class PlayerDamageUtiltyContext:
    def __init__(self, parser: CustomDemoParser, playerSteamId: int) -> None:
        self.parser: CustomDemoParser = parser
        self.playerSteamId: int = playerSteamId
        self.roundContext: RoundContext = RoundContext(parser= parser)


    def loadContextData(self) -> None:
        damageUtilityEvents: list = Filters().filterDamageUtilityEvents(self.parser.damageUtilityEvents, forPlayerSteamId= self.playerSteamId)
        for event in damageUtilityEvents:
            damageDone = int(event['dmg_health']) + int(event['dmg_armor']) * 2
            self.roundContext.appendDataAtTick(tick= int(event["tick"]), data= damageDone)
        self.roundContext.calculatePrefixSum()
    
    
    def getDamageDoneTillTick(self, tick: int) -> int:
        return self.roundContext.getDataTillTick(tick= tick)
    

class PlayerSupportUtilityContext:
    def __init__(self, parser: CustomDemoParser, playerSteamId: int) -> None:
        self.parser: CustomDemoParser = parser
        self.playerSteamId: int = playerSteamId
        self.roundContext: RoundContext = RoundContext(parser= parser)


    def loadContextData(self) -> None:
        supportUtilityEvents: list = Filters().filterSupportUtilityEvents(self.parser.supportUtilityEvents, forPlayerSteamId= self.playerSteamId)
        for event in supportUtilityEvents:
            self.roundContext.appendDataAtTick(tick= int(event["tick"]), data= 1)
        self.roundContext.calculatePrefixSum()
    
    
    def getSupportDoneTillTick(self, tick: int) -> int:
        return self.roundContext.getDataTillTick(tick= tick)