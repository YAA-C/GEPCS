import os
import pandas as pd
import random
from parseLib.CustomDemoParser import CustomDemoParser
from parseLib.PlayerIntervalGenerator import PlayerIntervalGenerator

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


    def getByIndex(self, df: pd.DataFrame, index: tuple) -> pd.DataFrame:
        if index in df.index:
            return df.loc[index]
        return pd.DataFrame()


    def euclideanDist(self, pointX, pointY):
        dist = 0
        for i in range(len(pointX)):
            dist += ((pointX[i] - pointY[i]) ** 2)
        return dist


    def start(self):
        steamIds = self.parser.players
        intervalGeneratorObjs = dict()

        label = False
        for player in steamIds:
            intervalGenerator = PlayerIntervalGenerator(self.parser.hurtEvents, player)
            intervalGenerator.generateIntervals()
            intervalGeneratorObjs[player] = intervalGenerator

        dfRows = []
        totalColumns = 35
        for player in intervalGeneratorObjs.keys():
            # print(player)
            tickIntervals = intervalGeneratorObjs[player].hurtIntervals
            if(len(tickIntervals) == 0):
                continue

            for singleInterval in tickIntervals:
                intervalStart = singleInterval[0]
                intervalEnd = singleInterval[1]

                for tick in range(intervalStart, intervalEnd + 1):
                    rowData = [""] * totalColumns
                    playerTickData = self.getByIndex(self.parser.parsedDf, (tick, player))
                    if(len(playerTickData) == 0):
                        # Skipped tick
                        continue
                    
                    playerTickData = playerTickData.iloc[0, :]
                    X = playerTickData['X']
                    Y = playerTickData['Y']
                    Z = playerTickData['Z']
                    velocityX = playerTickData['m_vecVelocity[0]']
                    velocityY = playerTickData['m_vecVelocity[1]']
                    velocityZ = playerTickData['m_vecVelocity[2]']
                    yaw = playerTickData['m_angEyeAngles[1]']
                    pitch = playerTickData['m_angEyeAngles[0]']
                    isCrouched = playerTickData['m_bDucked'] | playerTickData['m_bDucking']
                    isJumping = ""
                    isFiring = ""
                    for i, val in enumerate([tick, X, Y, Z, velocityX, velocityY, velocityZ, yaw, pitch, isCrouched, isJumping, isFiring]):
                        rowData[i] = val

                    if(tick in intervalGeneratorObjs[player].hurtTicks):
                        targetHurtEvent = intervalGeneratorObjs[player].hurtTicks
                        self.parser.parsedDf.loc[(tick, player)]
                        targetTickData = self.getByIndex(self.parser.parsedDf, (tick, targetHurtEvent[tick]["player_steamid"])).iloc[0, :] 
                        targetX = targetTickData["X"]
                        targetY = targetTickData["Y"]
                        targetZ = targetTickData["Z"]
                        targetVelocityX = targetTickData["m_vecVelocity[0]"]
                        targetVelocityY = targetTickData["m_vecVelocity[1]"]
                        targetVelocityZ = targetTickData["m_vecVelocity[2]"]
                        tagetYaw = targetTickData['m_angEyeAngles[1]']
                        targetPitch = targetTickData['m_angEyeAngles[0]']
                        dmgDone = targetHurtEvent[tick]["dmg_health"] + targetHurtEvent[tick]["dmg_armor"]
                        noOfShot = ""
                        distToTarget = self.euclideanDist([targetX, targetY, targetZ], [X, Y, Z])
                        targetHitArea = targetHurtEvent[tick]["hitgroup"]
                        penetrated = ""
                        weaponUsed = targetHurtEvent[tick]["weapon"]
                        accuracy = ""
                        targetBlind = ""
                        targetInSmoke = ""
                        targetReturnedDmg = ""

                        for i, val in enumerate([dmgDone, noOfShot, distToTarget, targetX, targetY, targetZ, targetVelocityX, targetVelocityY, targetVelocityZ, tagetYaw, targetPitch, targetHitArea, penetrated, weaponUsed, accuracy, targetBlind, targetInSmoke, targetReturnedDmg]):
                            rowData[i + 12] = val
                        
                    utilityDmgDone = ""
                    supportUtilityUsed = ""
                    kdr = ""
                    audioClue = ""

                    rowData[-5] = utilityDmgDone
                    rowData[-4] = supportUtilityUsed
                    rowData[-3] = kdr
                    rowData[-2] = audioClue
                    rowData[-1] = label
                    dfRows.append(rowData)
                dfRows.append([""] * totalColumns)


        # print("Completed parsing...")
        # print(len(hurtEventsMerged))
        columns = ["currentTick", "X", "Y", "Z", "velocityX", "velocityY", "velocityZ", "yaw", "pitch", "isCrouched", "isJumping", "isFiring", "dmgDone", "noOfShot", "distToTarget", "targetX", "targetY", "targetZ", "targetVelocityX", "targetVelocityY", "targetVelocityZ", "tagetYaw", "targetPitch", "targetHitArea", "penetrated", "weaponUsed", "accuracy", "targetBlind", "targetInSmoke", "targetReturnedDmg", "utilityDmgDone", "supportUtilityUsed", "kdr", "audioClue", "Label"]
        mainDf:pd.DataFrame = pd.DataFrame(data=dfRows, columns=columns)
        savePath = os.path.join(os.path.dirname(__file__), f'DemoFiles\\csv\\{self.fileName[:-4]}-{random.randint(99999, 999999)}.csv')
        mainDf.to_csv(savePath, index= False)

    
# for x in hurtEventsMerged:
#     print(x)