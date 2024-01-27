import os
import pandas as pd
import random
from parseLib.CustomDemoParser import CustomDemoParser
from parseLib.GlobalMatchContext import GlobalMatchContext
from parseLib.PlayerMatchContext import PlayerMatchContext
from parseLib.Fight import Fight
from parseLib.Logger import log

class SingleFileParser:
    def __init__(self, fileName = "test.dem"):
        dirname = os.path.dirname(__file__)
        self.fileName = fileName
        self.file = os.path.join(dirname, f'DemoFiles\\Demos\\{fileName}')
        self.parser = CustomDemoParser(targetFile = self.file)
        result = self.parser.parseFile()
        self.globalMatchContextObj: GlobalMatchContext = GlobalMatchContext(self.parser)
        self.globalMatchContextObj.loadContextData()

        if not result:
            print(f"Cannot Parse : {self.file}")
            raise Exception


    def start(self):
        dfRows = []
        completedCount = 0
        label = True
        
        for playerSteamId in self.parser.players:
            playerTeam: str = self.parser.allPlayersTeams[playerSteamId]
            playerMatchContextObj: PlayerMatchContext = PlayerMatchContext(self.parser, playerSteamId)
            playerMatchContextObj.generateWeaponFireTicks()

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

        columns = Fight.features
        mainDf:pd.DataFrame = pd.DataFrame(data=dfRows, columns=columns)
        savePath = os.path.join(os.path.dirname(__file__), f'DemoFiles\\csv\\{self.fileName[:-4]}-{random.randint(99999, 999999)}.csv')
        log("Saved file CSV Output to:", savePath)
        mainDf.to_csv(savePath, index= False)