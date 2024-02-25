import os
import pandas as pd
import random
from src.CustomDemoParser import CustomDemoParser
from src.GlobalMatchContext import GlobalMatchContext
from src.PlayerMatchContext import PlayerMatchContext
from src.Fight import Fight
from src.utils.Logger import log


class SingleFileParser:
    def __init__(self, fileName: str = "test.dem", fileVerdict: bool | None = None):
        self.fileName: str = fileName
        self.fileVerdict: str = fileVerdict
        dirname: str = os.path.dirname(__file__)
        self.file: str = os.path.join(dirname, f'DemoFiles\\Demos\\{fileName}')
        self.parser: CustomDemoParser = CustomDemoParser(targetFile = self.file)
        success: bool = self.parser.parseFile()
        self.globalMatchContextObj: GlobalMatchContext = GlobalMatchContext(self.parser)
        self.globalMatchContextObj.loadContextData()

        if not success:
            print(f"Cannot Parse : {self.file}")
            raise Exception


    def start(self):
        dfRows = []
        completedCount = 0
        label = self.fileVerdict
        
        for playerSteamId in self.parser.players:
            playerTeam: str = self.parser.allPlayersTeams[playerSteamId]
            playerMatchContextObj: PlayerMatchContext = PlayerMatchContext(self.parser, playerSteamId)

            for targetSteamId in self.parser.allPlayers:
                targetTeam: str = self.parser.allPlayersTeams[targetSteamId]
                if (playerSteamId == targetSteamId) or (playerTeam == targetTeam):
                    continue

                playerMatchContextObj.updateTarget(targetSteamId= targetSteamId)
                tickIntervals = playerMatchContextObj.hurtIntervals

                if(len(tickIntervals) == 0):
                    continue

                for singleInterval in tickIntervals:
                    intervalStart = singleInterval[0]
                    intervalEnd = singleInterval[1]
                    completedCount += 1
                    
                    Fight(
                        intervalStartTick= intervalStart, 
                        intervalEndTick= intervalEnd, 
                        parser= self.parser, 
                        globalMatchContextObj= self.globalMatchContextObj,
                        playerMatchContextObj= playerMatchContextObj,
                        playerSteamId= playerSteamId,
                        targetSteamId= targetSteamId,
                        label= label,
                        dfRows= dfRows
                    ).buildFight()

        log(f"Parsed Fights:", completedCount)

        columns = Fight.getColumns(label= self.fileVerdict)
        mainDf:pd.DataFrame = pd.DataFrame(data=dfRows, columns=columns)
        savePath = os.path.join(os.path.dirname(__file__), f'DemoFiles\\csv\\{self.fileName[:-4]}-{random.randint(99999, 999999)}.csv')
        mainDf.to_csv(savePath, index= False)
        
        log("Saved file CSV Output to:", savePath)