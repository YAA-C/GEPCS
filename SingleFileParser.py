import os
import pandas as pd
import random
from parseLib.CustomDemoParser import CustomDemoParser
from parseLib.PlayerIntervalGenerator import PlayerIntervalGenerator
from parseLib.Fight import Fight

class SingleFileParser:
    def __init__(self, fileName = "test.dem"):
        dirname = os.path.dirname(__file__)
        self.fileName = fileName
        self.file = os.path.join(dirname, f'DemoFiles\\Demos\\{fileName}')
        self.parser = CustomDemoParser(targetFile = self.file)
        result = self.parser.parseFile()

        if not result:
            print(f"Cannot Parse : {self.file}")
            raise Exception


    def start(self):
        dfRows = []
        completedCount = 0

        label = False
        for playerSteamId in self.parser.players:
            for targetSteamId in self.parser.allPlayers:
                if playerSteamId == targetSteamId:
                    continue

                intervalGenerator: PlayerIntervalGenerator = PlayerIntervalGenerator(self.parser.hurtEvents, playerSteamId, targetSteamId)
                intervalGenerator.generateIntervals()
                tickIntervals = intervalGenerator.hurtIntervals

                # print(player)
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
                        intervalGeneratorObj= intervalGenerator,
                        playerSteamId= playerSteamId,
                        targetSteamId= targetSteamId,
                        label= label,
                        dfRows= dfRows
                    ).buildFight()

        with open(f"./logs/logs.txt", '+a') as f:
            f.write(f"{completedCount}\n")

        columns = ["currentTick", "X", "Y", "Z", "velocityX", "velocityY", "velocityZ", "yaw", "pitch", "utilityDmgDone", "supportUtilityUsed", "kdr", "isCrouched", "isJumping", "isFiring", "targetX", "targetY", "targetZ", "targetVelocityX", "targetVelocityY", "targetVelocityZ", "tagetYaw", "targetPitch", "dmgDone", "distToTarget", "targetHitArea", "penetrated", "weaponUsed", "targetBlind", "targetInSmoke", "targetReturnedDmg", "Label"]
        mainDf:pd.DataFrame = pd.DataFrame(data=dfRows, columns=columns)
        savePath = os.path.join(os.path.dirname(__file__), f'DemoFiles\\csv\\{self.fileName[:-4]}-{random.randint(99999, 999999)}.csv')
        mainDf.to_csv(savePath, index= False)
