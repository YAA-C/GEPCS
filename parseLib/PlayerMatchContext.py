from .Filters import Filters
from .CustomDemoParser import CustomDemoParser
from .Contexts import PrefixRoundContext, PrefixMatchContext


class PlayerMatchContext:
    def __init__(self, parser: CustomDemoParser, playerSteamId: int) -> None:
        self.tickDeltaNegative: int = 128
        self.tickDeltaPositive: int = 0
        self.playerSteamId = playerSteamId
        self.allHurtEvents: list = parser.hurtEvents
        self.fireEvents = Filters().filterPlayerFireEvents(fireEvents= parser.fireEvents, playerSteamId= playerSteamId)
        self.generateWeaponFireTicks()
        self.generateDamageUtility(parser= parser)
        self.generateSupportUtility(parser= parser)
        self.generateKDR(parser= parser)
        

    def generateWeaponFireTicks(self) -> None:
        self.fireTicks = set([event['tick'] for event in self.fireEvents])


    def generateDamageUtility(self, parser: CustomDemoParser) -> None:
        # Every precomputation about utility damage
        self.playerDamageUtilityObj: PlayerDamageUtiltyContext = PlayerDamageUtiltyContext(parser= parser, playerSteamId= self.playerSteamId)
        self.playerDamageUtilityObj.loadContextData()
        

    def generateSupportUtility(self, parser: CustomDemoParser) -> None:
        # Every precomputation about utility support
        self.playerSupportUtilityObj: PlayerSupportUtilityContext = PlayerSupportUtilityContext(parser= parser, playerSteamId= self.playerSteamId)
        self.playerSupportUtilityObj.loadContextData()
        

    def generateKDR(self, parser: CustomDemoParser) -> None:
        # Every precomputation about KDR
        self.playerKillDeathObj: PlayerKillDeathContext = PlayerKillDeathContext(parser= parser, playerSteamId= self.playerSteamId)
        self.playerKillDeathObj.loadContextData()
        

    def generatePlayerJumpIntervals(self) -> None:
        pass


    def getPlayerDamageDoneTillTick(self, tick: int) -> int:
        return self.playerDamageUtilityObj.getDamageDoneTillTick(tick= tick)


    def getPlayerSupportDoneTillTick(self, tick: int) -> int:
        return self.playerSupportUtilityObj.getSupportDoneTillTick(tick= tick)
    

    def getPlayerKDRTillTick(self, tick: int) -> int:
        return self.playerKillDeathObj.getKDRTillTick(tick= tick)


    # Changes object data per target
    def updateTarget(self, targetSteamId: int) -> None:
        self.hurtTicks = dict()
        self.hurtIntervals = []
        self.generatePlayerHurtIntervals(targetSteamId)


    def generatePlayerHurtIntervals(self, targetSteamId: int) -> None:
        intervals: list = []
        currentHurtEvents: list = Filters().filterPlayerHurtEvents(hurtEvents= self.allHurtEvents, playerSteamId= self.playerSteamId, targetSteamId= targetSteamId)
        for event in currentHurtEvents:
            self.hurtTicks[event['tick']] = event
            interval = (event['tick'] - self.tickDeltaNegative, event['tick'] + self.tickDeltaPositive)
            intervals.append(interval)

        self.hurtIntervals = self.mergeOverlappingIntervals(intervals= intervals)


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
    

class PlayerDamageUtiltyContext:
    def __init__(self, parser: CustomDemoParser, playerSteamId: int) -> None:
        self.parser: CustomDemoParser = parser
        self.playerSteamId: int = playerSteamId
        self.roundContext: PrefixRoundContext = PrefixRoundContext(parser= parser)


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
        self.roundContext: PrefixRoundContext = PrefixRoundContext(parser= parser)


    def loadContextData(self) -> None:
        supportUtilityEvents: list = Filters().filterSupportUtilityEvents(self.parser.supportUtilityEvents, forPlayerSteamId= self.playerSteamId)
        for event in supportUtilityEvents:
            self.roundContext.appendDataAtTick(tick= int(event["tick"]), data= 1)
        self.roundContext.calculatePrefixSum()
    
    
    def getSupportDoneTillTick(self, tick: int) -> int:
        return self.roundContext.getDataTillTick(tick= tick)
    

class PlayerKillDeathContext:
    def __init__(self, parser: CustomDemoParser, playerSteamId: int) -> None:
        self.parser: CustomDemoParser = parser
        self.playerSteamId: int = playerSteamId
        self.matchKillContext: PrefixMatchContext = PrefixMatchContext()
        self.matchDeathContext: PrefixMatchContext = PrefixMatchContext()


    def loadContextData(self) -> None:
        killEvents: list = Filters().filterPlayerKillEvents(self.parser.deathEvents, playerSteamId= self.playerSteamId)
        deathEvents: list = Filters().filterPlayerDeathEvents(self.parser.deathEvents, playerSteamId= self.playerSteamId)
        for event in killEvents:
            self.matchKillContext.appendDataAtTick(tick= int(event["tick"]), data= 1)
        for event in deathEvents:
            self.matchDeathContext.appendDataAtTick(tick= int(event["tick"]), data= 1)
        self.matchKillContext.calculatePrefixSum()
        self.matchDeathContext.calculatePrefixSum()
    
    
    def getKDRTillTick(self, tick: int) -> float:
        kills: int = self.matchKillContext.getDataTillTick(tick= tick)
        deaths: int = self.matchDeathContext.getDataTillTick(tick= tick)
        if deaths == 0:
            return float(kills)
        return float(kills) / float(deaths)