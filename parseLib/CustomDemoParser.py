from demoparser import DemoParser
import pandas as pd

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
            self.hurtEvents = self.parser.parse_events("player_hurt")
            self.players = self.parsedDf['steamid'].unique().tolist()
            
            self.parsedDf.set_index(['tick','steamid'], inplace=True)
            self.parsedDf = self.parsedDf.sort_index() 
        except Exception as e:
            print(e)
            return False
        return True