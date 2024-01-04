from demoparser import DemoParser
import pandas as pd
from .Filters import Filters

class CustomDemoParser:
    def __init__(self, targetFile: str) -> None:
        self.props = [
            "X", "Y", "Z",
            "m_angEyeAngles[0]", "m_angEyeAngles[1]", 
            "m_vecVelocity[0]", "m_vecVelocity[1]", "m_vecVelocity[2]",
            "m_bDucked", "m_bDucking",
        ]
        self.targetFile = targetFile
        self.parsedDf: pd.DataFrame
        self.players: list = []
        self.hurtEvents: list = []
        self.fireEvents: list = []


    def parseFile(self) -> bool:
        try:
            self.parser = DemoParser(self.targetFile)
            self.parsedDf = self.parser.parse_ticks(self.props)

            self.parsePlayerSteamIds()
            self.parsePlayerHurtEvents()
            self.parsePlayerFireEvents()
            self.fixHurtEventWeaponNames()
            
            self.parsedDf.set_index(['tick','steamid'], inplace=True)
            self.parsedDf = self.parsedDf.sort_index() 
        except Exception as e:
            print(e)
            return False
        return True
    

    def parsePlayerSteamIds(self) -> None:
        self.allPlayers = self.parsedDf['steamid'].unique().tolist()
        x = []
        for i in self.allPlayers:
            tmp = self.parsedDf.loc[self.parsedDf['steamid'] == i]
            x.append({f'id_{i}': tmp.iloc[0, 12]})
        from pprint import pprint
        pprint(x)
        self.players = Filters().filterHumanPlayers(self.allPlayers)
        print("After filtering : ", self.players)


    def parsePlayerHurtEvents(self) -> None:
        hurtEvents = self.parser.parse_events("player_hurt")
        hurtEvents = sorted(hurtEvents, key=lambda x: x['tick'])
        self.hurtEvents = Filters().filterWeaponHurtEvents(hurtEvents)


    def parsePlayerFireEvents(self) -> None:
        fireEvents = self.parser.parse_events("weapon_fire")
        self.fireEvents = sorted(fireEvents, key=lambda x: x['tick'])

    
    def fixHurtEventWeaponNames(self) -> None:
        playerFireEvents = dict()
        for player in self.parsedDf['steamid'].unique().tolist():
            playerFireEvents[player] = [x for x in self.fireEvents if x['player_steamid'] == player]
    
        for player in playerFireEvents.keys():
            hurtEventIndex = 0
            for i, playerFireEvent in enumerate(playerFireEvents[player]):
                # player has not fired but hurtEvents are registered on target 
                while(hurtEventIndex < len(self.hurtEvents) and playerFireEvent['tick'] > self.hurtEvents[hurtEventIndex]['tick']):
                    hurtEventIndex += 1
                # This is some last shot of match which never registered.
                if hurtEventIndex == len(self.hurtEvents):
                    break
                # hurtEvent is of other player
                while(hurtEventIndex < len(self.hurtEvents) and 
                        playerFireEvent['tick'] == self.hurtEvents[hurtEventIndex]['tick'] and 
                        self.hurtEvents[hurtEventIndex]['attacker_steamid'] != playerFireEvent['player_steamid']):
                    hurtEventIndex += 1
                # This is also some last shot of match which never registered.
                if hurtEventIndex == len(self.hurtEvents):
                    break
                # player has fired and shot has hit target
                if(playerFireEvent['tick'] == self.hurtEvents[hurtEventIndex]['tick']):
                    self.hurtEvents[hurtEventIndex]['weapon'] = playerFireEvent['weapon']
                    hurtEventIndex += 1