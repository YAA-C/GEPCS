import pandas as pd
from math import sqrt
from .PlayerIntervalGenerator import PlayerIntervalGenerator
from .CustomDemoParser import CustomDemoParser


class Fight:
    def __init__(
                self, 
                intervalStartTick: int, 
                intervalEndTick: int, 
                parser: CustomDemoParser, 
                intervalGeneratorObj: PlayerIntervalGenerator, 
                playerSteamId: int,
                targetSteamId: int,
                label: bool,
                dfRows: list
            ) -> None:
        self.intervalStartTick: int = intervalStartTick
        self.intervalEndTick: int = intervalEndTick
        self.parser: CustomDemoParser = parser
        self.intervalGeneratorObj: PlayerIntervalGenerator = intervalGeneratorObj
        self.playerSteamId: int = playerSteamId
        self.targetSteamId: int = targetSteamId
        self.label: bool = label
        self.dfRows: list = dfRows
        self.columnLabels: list = ["currentTick", "X", "Y", "Z", "velocityX", "velocityY", "velocityZ", "yaw", "pitch", "utilityDmgDone", "supportUtilityUsed", "kdr", "isCrouched", "isJumping", "isFiring", "targetX", "targetY", "targetZ", "targetVelocityX", "targetVelocityY", "targetVelocityZ", "tagetYaw", "targetPitch", "dmgDone", "distToTarget", "targetHitArea", "penetrated", "weaponUsed", "targetBlind", "targetInSmoke", "targetReturnedDmg", "Label"]
        self.featureNameToIndex: dict = dict()
        for i in range(len(self.columnLabels)):
            self.featureNameToIndex[self.columnLabels[i]] = i


    def getByIndex(self, df: pd.DataFrame, index: tuple[int]) -> pd.DataFrame:
        if index in df.index:
            return df.loc[index]
        return pd.DataFrame()


    def getPlayerLocation(self, playerTickData: pd.Series) -> tuple:
        X = playerTickData['X']
        Y = playerTickData['Y']
        Z = playerTickData['Z']
        return (X, Y, Z)
    
    
    def getPlayerVelocity(self, playerTickData: pd.Series) -> tuple:
        velocityX = playerTickData['m_vecVelocity[0]']
        velocityY = playerTickData['m_vecVelocity[1]']
        velocityZ = playerTickData['m_vecVelocity[2]']
        return (velocityX, velocityY, velocityZ)


    def getPlayerViewAngles(self, playerTickData: pd.Series) -> tuple:
        yaw = playerTickData['m_angEyeAngles[1]']
        pitch = playerTickData['m_angEyeAngles[0]']
        return (yaw, pitch)
    

    def getPlayerCrouched(self, playerTickData: pd.Series) -> bool:
        return playerTickData['m_bDucked'] | playerTickData['m_bDucking']


    #NOT IMPLEMENTED
    def getPlayerJumped(self, playerTickData: pd.Series) -> bool:
        return False
    

    #NOT IMPLEMENTED
    def getPlayerFiring(self, playerTickData: pd.Series) -> bool:
        return False


    def getTargetTotalDamage(self, targetHurtEvent: dict) -> float:
        return targetHurtEvent["dmg_health"] + targetHurtEvent["dmg_armor"]
    

    def getDistanceToTarget(self, X: list, Y: list) -> float:
        dist = 0
        for i in range(len(X)):
            dist += ((X[i] - Y[i]) ** 2)
        return sqrt(dist)


    def getTargetHitSpot(self, targetHurtEvent: dict) -> int:
        return targetHurtEvent["hitgroup"]


    #NOT IMPLEMENTED
    def getShotPenetrated(self) -> int:
        return 0


    def getUsedWeapon(self, targetHurtEvent: dict) -> str:
        return targetHurtEvent["weapon"]


    #NOT IMPLEMENTED
    def getPlayerBlind(self) -> bool:
        return False


    #NOT IMPLEMENTED
    def getSmokeInVision(self) -> bool:
        return False


    #NOT IMPLEMENTED
    def getReturnedDamge(self) -> float:
        return 0
    

    #NOT IMPLEMENTED
    def getUtilityDamageDone(self) -> int:
        return 0


    #NOT IMPLEMENTED
    def getSupportUtilityUsed(self) -> int:
        return 0


    #NOT IMPLEMENTED
    def getPlayerKDR(self) -> float:
        return 0


    def setFeatures(self, rowData: list, featureName: object, featureValue: object) -> None:
        if type(featureName) == list or type(featureName) == tuple:
            assert len(featureName) == len(featureValue), "names and value should be of same length"
            for i in range(len(featureName)):
                rowData[self.featureNameToIndex[featureName[i]]] = featureValue[i]
        else:
            rowData[self.featureNameToIndex[featureName]] = featureValue


    def buildFightTick(self, tick: int) -> list:
        rowData = [""] * len(self.columnLabels)
        playerTickData = self.getByIndex(self.parser.parsedDf, (tick, self.playerSteamId))
        if(len(playerTickData) == 0):
            return list()   # Skipped tick
        else:
            playerTickData: pd.Series = playerTickData.iloc[0, :]

        X, Y, Z = self.getPlayerLocation(playerTickData= playerTickData)
        velocityX, velocityY, velocityZ = self.getPlayerVelocity(playerTickData= playerTickData)
        yaw, pitch = self.getPlayerViewAngles(playerTickData= playerTickData)
        utilityDmgDone = self.getUtilityDamageDone()
        supportUtilityUsed = self.getSupportUtilityUsed()
        kdr = self.getPlayerKDR()
        isCrouched = self.getPlayerCrouched(playerTickData= playerTickData)
        isJumping = self.getPlayerJumped(playerTickData= playerTickData)
        isFiring = self.getPlayerFiring(playerTickData= playerTickData)

        self.setFeatures(rowData= rowData, featureName= "currentTick", featureValue= tick)
        self.setFeatures(rowData= rowData, featureName= ("X", "Y", "Z"), featureValue= (X, Y, Z))
        self.setFeatures(rowData= rowData, featureName= ("velocityX", "velocityY", "velocityZ"), featureValue= (velocityX, velocityY, velocityZ))
        self.setFeatures(rowData= rowData, featureName= ("yaw", "pitch"), featureValue= (yaw, pitch))
        self.setFeatures(rowData= rowData, featureName= "utilityDmgDone", featureValue= utilityDmgDone)
        self.setFeatures(rowData= rowData, featureName= "supportUtilityUsed", featureValue= supportUtilityUsed)
        self.setFeatures(rowData= rowData, featureName= "kdr", featureValue= kdr)
        self.setFeatures(rowData= rowData, featureName= "isCrouched", featureValue= isCrouched)
        self.setFeatures(rowData= rowData, featureName= "isJumping", featureValue= isJumping)
        self.setFeatures(rowData= rowData, featureName= "isFiring", featureValue= isFiring)

        if(tick in self.intervalGeneratorObj.hurtTicks):
            targetHurtEvent = self.intervalGeneratorObj.hurtTicks[tick]
            targetTickData = self.getByIndex(self.parser.parsedDf, (tick, targetHurtEvent["player_steamid"])).iloc[0, :] 
            
            targetX, targetY, targetZ = self.getPlayerLocation(playerTickData= targetTickData)
            targetVelocityX, targetVelocityY, targetVelocityZ = self.getPlayerVelocity(playerTickData= targetTickData)
            tagetYaw, targetPitch = self.getPlayerViewAngles(playerTickData= targetTickData)
            dmgDone = self.getTargetTotalDamage(targetHurtEvent= targetHurtEvent)
            distToTarget = self.getDistanceToTarget([targetX, targetY, targetZ], [X, Y, Z])
            targetHitArea = self.getTargetHitSpot(targetHurtEvent= targetHurtEvent)
            penetrated = self.getShotPenetrated()
            weaponUsed = self.getUsedWeapon(targetHurtEvent= targetHurtEvent)
            targetBlind = self.getPlayerBlind()
            targetInSmoke = self.getSmokeInVision()
            targetReturnedDmg = self.getReturnedDamge()

            self.setFeatures(rowData= rowData, featureName= ("targetX", "targetY", "targetZ"), featureValue= (targetX, targetY, targetZ))
            self.setFeatures(rowData= rowData, featureName= ("targetVelocityX", "targetVelocityY", "targetVelocityZ"), featureValue= (targetVelocityX, targetVelocityY, targetVelocityZ))
            self.setFeatures(rowData= rowData, featureName= ("tagetYaw", "targetPitch"), featureValue= (tagetYaw, targetPitch))
            self.setFeatures(rowData= rowData, featureName= "dmgDone", featureValue= dmgDone)
            self.setFeatures(rowData= rowData, featureName= "distToTarget", featureValue= distToTarget)
            self.setFeatures(rowData= rowData, featureName= "targetHitArea", featureValue= targetHitArea)
            self.setFeatures(rowData= rowData, featureName= "penetrated", featureValue= penetrated)
            self.setFeatures(rowData= rowData, featureName= "weaponUsed", featureValue= weaponUsed)
            self.setFeatures(rowData= rowData, featureName= "targetBlind", featureValue= targetBlind)
            self.setFeatures(rowData= rowData, featureName= "targetInSmoke", featureValue= targetInSmoke)
            self.setFeatures(rowData= rowData, featureName= "targetReturnedDmg", featureValue= targetReturnedDmg)
        self.setFeatures(rowData= rowData, featureName= "Label", featureValue= str(self.label))

        return rowData
    

    def buildFight(self) -> None:
        for tick in range(self.intervalStartTick, self.intervalEndTick + 1):
            rowData: list = self.buildFightTick(tick= tick)
            if len(rowData) != 0:
                self.dfRows.append(rowData)

        self.dfRows.append([""] * len(self.columnLabels))