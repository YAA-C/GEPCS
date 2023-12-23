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


    def parseFile(self) -> bool:
        try:
            self.parser = DemoParser(self.targetFile)
            self.parsedDf = self.parser.parse_ticks(self.props)

            self.parsePlayerSteamIds()
            self.parsePlayerHurtEvents()
            self.parsePlayerFireEvents()
            
            self.parsedDf.set_index(['tick','steamid'], inplace=True)
            self.parsedDf = self.parsedDf.sort_index() 
        except Exception as e:
            print(e)
            return False
        return True
    

    def parsePlayerSteamIds(self) -> None:
        self.players = self.parsedDf['steamid'].unique().tolist()
        x = []
        for i in self.players:
            tmp = self.parsedDf.loc[self.parsedDf['steamid'] == i]
            x.append({f'id_{i}': tmp.iloc[0, 12]})
        from pprint import pprint
        pprint(x)
        self.players = [player for player in self.players if (player > 76500000000000000 and player < 76600000000000000)]
        print("After filtering : ", self.players)


    def parsePlayerHurtEvents(self) -> None:
        hurtEvents = self.parser.parse_events("player_hurt")
        hurtEvents = sorted(hurtEvents, key=lambda x: x['tick'])
        self.hurtEvents = Filters().filterWeaponHurtEvents(hurtEvents)


    def parsePlayerFireEvents(self) -> None:
        fireEvents = self.parser.parse_events("weapon_fire")
        self.fireEvents = sorted(fireEvents, key=lambda x: x['tick'])