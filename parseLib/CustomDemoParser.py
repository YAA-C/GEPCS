from demoparser import DemoParser
import pandas as pd
import traceback
from .Logger import log, logp
from .Filters import Filters

class CustomDemoParser:
    def __init__(self, targetFile: str) -> None:
        self.props = [
            "X", "Y", "Z",
            "m_angEyeAngles[0]", "m_angEyeAngles[1]", 
            "m_vecVelocity[0]", "m_vecVelocity[1]", "m_vecVelocity[2]",
            "m_bDucked", "m_bDucking", "m_bIsScoped"
        ]
        self.targetFile = targetFile
        self.parsedDf: pd.DataFrame
        self.allPlayers: list = []
        self.allPlayersTeams: dict = dict()
        self.players: list = []
        self.hurtEvents: list = []
        self.fireEvents: list = []
        self.deathEvents: list = []
        self.blindEvents: list = []
        self.roundTicks: list = ()
        self.damageUtilityEvents: list = []
        self.supportUtilityEvents: list = []


    def parseFile(self) -> bool:
        try:
            self.parser = DemoParser(self.targetFile)
            self.parsedDf: pd.DataFrame = self.parser.parse_ticks(self.props)

            self.checkDemoConstraints()
            self.parsePlayerSteamIds()
            self.parsePlayerTeams()
            self.parseRoundTicks()
            self.parsePlayerHurtEvents()
            self.parsePlayerFireEvents()
            self.fixHurtEventWeaponNames()
            self.parsePlayerBlindEvents()
            self.parsePlayerDeathEvents()
            
            self.parsedDf.set_index(['tick','steamid'], inplace=True)
            self.parsedDf.sort_index(inplace= True) 
        except Exception as e:
            log(traceback.format_exc(), tag="ERROR")
            return False
        return True


    def checkDemoConstraints(self) -> None:
        headerData: dict = self.parser.parse_header()
        totalTicks: int = int(headerData["protoplayback_tickscol"])
        totalSeconds: float = float(headerData["playback_time"])
        tickrate: float = totalTicks / totalSeconds
        
        averageSnapshotRate: float = 0
        ticks = self.parsedDf['tick'].unique()
        ticks.sort()
        for i in range(1, len(ticks)):
            deltaTick = abs(ticks[i] - ticks[i - 1])
            if deltaTick == 0:
                # Double tick (round start bug)
                continue
            currentTickRate = 128.00 / deltaTick
            averageSnapshotRate += currentTickRate
        averageSnapshotRate = averageSnapshotRate / (len(ticks) - 1)

        tickratePercentage: float = tickrate * 100.00 / 128.00
        snapshotRatePercentage: float = averageSnapshotRate * 100.00 / 128.00
        
        log(f"TickRate {tickrate:.3f} --> {tickratePercentage:.3f} %")
        log(f"Average SnapshopRate {averageSnapshotRate:.3f} --> {snapshotRatePercentage:.3f} %")

        assert (tickratePercentage >= 80.00 and tickratePercentage <= 110.00), "Tickrate is not proper"
        assert (snapshotRatePercentage >= 80.00 and snapshotRatePercentage <= 110.00), "Snapshotrate is not proper"


    def parsePlayerSteamIds(self) -> None:
        self.allPlayers = self.parsedDf['steamid'].unique().tolist()
        self.players = Filters().filterHumanPlayers(self.allPlayers)
        self.allPlayers = sorted(self.allPlayers)
        self.players = sorted(self.players)
        x = []
        for i in self.allPlayers:
            tmp = self.parsedDf.loc[self.parsedDf['steamid'] == i]
            x.append({f'id_{i}': tmp.iloc[0, len(self.props) + 2]})
        logp(x)
        log("After filtering : ", self.players)


    def parsePlayerTeams(self) -> None:
        for playerData in self.parser.parse_players():
            self.allPlayersTeams[playerData["steamid"]] = playerData["starting_side"]


    def parsePlayerHurtEvents(self) -> None:
        hurtEvents = self.parser.parse_events("player_hurt")
        hurtEvents = sorted(hurtEvents, key=lambda x: x['tick'])
        damageUtilityEvents = Filters().filterDamageUtilityEvents(hurtEvents= hurtEvents)
        self.damageUtilityEvents = sorted(damageUtilityEvents, key=lambda x: x['tick'])
        self.hurtEvents = Filters().filterWeaponHurtEvents(hurtEvents= hurtEvents)


    def parsePlayerFireEvents(self) -> None:
        fireEvents = self.parser.parse_events("weapon_fire")
        self.fireEvents = sorted(fireEvents, key=lambda x: x['tick'])
        supportUtilityEvents = Filters().filterSupportUtilityEvents(fireEvents= fireEvents)
        self.supportUtilityEvents = sorted(supportUtilityEvents, key=lambda x: x['tick'])
        self.fireEvents = Filters().filterWeaponFireEvents(fireEvents= fireEvents)

    
    def fixHurtEventWeaponNames(self) -> None:
        playerFireEvents = dict()
        for player in self.parsedDf['steamid'].unique().tolist():
            playerFireEvents[player] = [x for x in self.fireEvents if x['player_steamid'] == player]
    
        for player in playerFireEvents.keys():
            hurtEventIndex = 0
            for _, playerFireEvent in enumerate(playerFireEvents[player]):
                # player has not fired but hurtEvents are registered on target 
                while(hurtEventIndex < len(self.hurtEvents) and playerFireEvent['tick'] > self.hurtEvents[hurtEventIndex]['tick']):
                    hurtEventIndex += 1
                # This is some last shot of match which never registered.
                if hurtEventIndex == len(self.hurtEvents):
                    break
                while(hurtEventIndex < len(self.hurtEvents) and playerFireEvent['tick'] == self.hurtEvents[hurtEventIndex]['tick']):
                    # hurtEvent is of other player
                    if self.hurtEvents[hurtEventIndex]['attacker_steamid'] != playerFireEvent['player_steamid']:
                        hurtEventIndex += 1
                        continue
                    # player has fired and shot has hit target
                    self.hurtEvents[hurtEventIndex]['weapon'] = playerFireEvent['weapon']
                    hurtEventIndex += 1

        burstWeapons: dict = {
            'glock' : 'weapon_glock',
            'famas' : 'weapon_famas'
        }

        for event in self.hurtEvents:
            if event['weapon'] in burstWeapons:
                event['weapon'] = burstWeapons[event['weapon']]
            assert event['weapon'].startswith('weapon_'), f"wrong weapon name in hurt event {event}"

    
    def parsePlayerBlindEvents(self) -> None:
        playerBlindEvents: list = self.parser.parse_events("player_blind")
        self.blindEvents = sorted(playerBlindEvents, key=lambda x: x['tick'])


    def parseRoundTicks(self) -> None:
        roundTicks: list = [0]
        roundTicks.extend([int(round["tick"]) for round in self.parser.parse_events("round_freeze_end")])
        self.roundTicks = sorted(roundTicks)
        

    def parsePlayerDeathEvents(self) -> None:
        playerDeathEvents: list = self.parser.parse_events("player_death")
        self.deathEvents = sorted(playerDeathEvents, key=lambda x: x['tick'])