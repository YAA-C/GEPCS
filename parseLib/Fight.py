import pandas as pd
from .CustomMath import eularDistance
from .GlobalMatchContext import GlobalMatchContext
from .PlayerMatchContext import PlayerMatchContext
from .CustomDemoParser import CustomDemoParser
from .Filters import Filters

class Fight:
    features: list = [
        "currentTick", 
        "playerId",
        "X", "Y", "Z",
        "deltaX", "deltaY", "deltaZ",  
        "yaw", "pitch", 
        "deltaYaw", "deltaPitch",
        "deltaAimArc",
        "isFlashed",
        "isCrouching",
        "isJumping",
        "utilityDmgDone", 
        "supportUtilityUsed", 
        "KDR", 
        "isFiring",

        "targetId",
        "targetX", "targetY", "targetZ",
        "targetDeltaX", "targetDeltaY", "targetDeltaZ",
        "dmgDone", 
        "distToTarget", 
        "targetHitArea", 
        "penetratedObject", 
        "weaponUsed",
        "weaponCategory",
        "isScoping",
        "isTargetBlind", 
        "isTargetInSmoke", 
        "targetReturnedDmg", 
        "Label"
    ]

    def __init__(
                self, 
                intervalStartTick: int, 
                intervalEndTick: int, 
                parser: CustomDemoParser, 
                globalMatchContextObj: GlobalMatchContext,
                playerMatchContextObj: PlayerMatchContext, 
                playerSteamId: int,
                targetSteamId: int,
                label: bool,
                dfRows: list
            ) -> None:
        self.intervalStartTick: int = intervalStartTick
        self.intervalEndTick: int = intervalEndTick
        self.parser: CustomDemoParser = parser
        self.globalMatchContext: GlobalMatchContext = globalMatchContextObj
        self.playerMatchContextObj: PlayerMatchContext = playerMatchContextObj
        self.playerSteamId: int = playerSteamId
        self.targetSteamId: int = targetSteamId
        self.label: bool = label
        self.dfRows: list = dfRows
        self.featureNameToIndex: dict = dict()
        for i, featureName in enumerate(Fight.features):
            self.featureNameToIndex[featureName] = i
        self.minTick: int = -1
        self.prevValueDict: dict = dict()

    
    def getByIndex(self, df: pd.DataFrame, index: tuple[int]) -> pd.DataFrame:
        if index in df.index:
            return df.loc[index]
        return pd.DataFrame()

    
    def convertViewAngleToLinearDelta(self, circularAngle: float, angleName: str):
        linearAngleDelta = 0

        if angleName == 'prevPitch':
            if angleName in self.prevValueDict:
                linearAngleDelta = circularAngle - self.prevValueDict[angleName]
                
        elif angleName == 'prevYaw':
            if angleName in self.prevValueDict:
                distance = abs(circularAngle - self.prevValueDict[angleName])
                circularDistance = 360 - distance
                if(distance < circularDistance):
                    linearAngleDelta = circularAngle - self.prevValueDict[angleName]
                else:
                    linearAngleDelta = circularDistance if (circularAngle < self.prevValueDict[angleName]) else -circularDistance
        
        self.prevValueDict[angleName] = circularAngle
        return linearAngleDelta
    

    def getPlayerLocation(self, playerTickData: pd.Series) -> tuple:
        X = playerTickData['X']
        Y = playerTickData['Y']
        Z = playerTickData['Z']
        crouchState: int = self.getPlayerCrouched(playerTickData= playerTickData)
        if crouchState == 1:    # In crouching animation
            Z = Z + 62.0
        elif crouchState == 2:  # Crouched completely
            Z = Z + 52.0
        else:   # Standing
            Z = Z + 72.0
        return (X, Y, Z)
    

    def getLocationDeltas(self, playerTickData: pd.Series) -> tuple:
        X, Y, Z = self.getPlayerLocation(playerTickData= playerTickData)
        deltaX, deltaY, deltaZ = 0, 0, 0

        if('prevX' in self.prevValueDict):
            deltaX = X - self.prevValueDict['prevX']
            deltaY = Y - self.prevValueDict['prevY']
            deltaZ = Z - self.prevValueDict['prevZ']
            
        self.prevValueDict['prevX'] = X
        self.prevValueDict['prevY'] = Y
        self.prevValueDict['prevZ'] = Z
        return (deltaX, deltaY, deltaZ)


    def getPlayerViewAngles(self, playerTickData: pd.Series) -> tuple:
        yaw = playerTickData['m_angEyeAngles[1]']
        pitch = playerTickData['m_angEyeAngles[0]']
        pitch = pitch - 360 if (pitch > 100) else pitch
        assert yaw >=0 and yaw <= 360, "Wrong yaw values"
        assert pitch <= 90 and pitch >= -90, "Wrong pitch Values"
        return (yaw, pitch)
    

    def getViewAngleDeltas(self, playerTickData: pd.Series) -> tuple:
        yaw, pitch = self.getPlayerViewAngles(playerTickData= playerTickData)
        deltaYaw = self.convertViewAngleToLinearDelta(circularAngle= yaw, angleName= 'prevYaw')
        deltaPitch = self.convertViewAngleToLinearDelta(circularAngle= pitch, angleName= 'prevPitch')
        return (deltaYaw, deltaPitch)


    def getPlayerCrouched(self, playerTickData: pd.Series) -> int:
        inDucking: bool = bool(playerTickData['m_bDucking'])
        completelyDucked: bool = bool(playerTickData['m_bDucked'])
        if completelyDucked:
            return 2
        elif inDucking:
            return 1
        return 0


    #NOT IMPLEMENTED
    def getPlayerJumped(self, playerTickData: pd.Series) -> bool:
        return False
    

    def getPlayerFiring(self, tick: int) -> bool:
        return tick in self.playerMatchContextObj.fireTicks


    def getTargetTotalDamage(self, targetHurtEvent: dict) -> float:
        return int(targetHurtEvent['dmg_health']) + int(targetHurtEvent['dmg_armor']) * 2
    

    def getDistanceToTarget(self, X: list, Y: list) -> float:
        return eularDistance(X= X, Y= Y)


    def getTargetHitSpot(self, targetHurtEvent: dict) -> int:
        assert targetHurtEvent["hitgroup"] >= 0 and targetHurtEvent["hitgroup"] <= 8, f"Bad Hitgroup {targetHurtEvent}"
        return int(targetHurtEvent["hitgroup"])


    #NOT IMPLEMENTED
    def getShotPenetrated(self) -> int:
        return 0


    def getUsedWeapon(self, targetHurtEvent: dict) -> str:
        return targetHurtEvent["weapon"]


    def getWeaponCategory(self, weaponName: str) -> str:
        return Filters().getWeaponCategory(weaponName= weaponName)


    def getPlayerScoping(self, playerTickData: pd.Series) -> bool:
        return bool(playerTickData["m_bIsScoped"])


    def getPlayerBlind(self, playerSteamId:int, tick: int) -> bool:
        return self.globalMatchContext.getPlayerBlindness(playerSteamId= playerSteamId, tick= tick)


    #NOT IMPLEMENTED
    def getSmokeInVision(self) -> bool:
        return False


    #NOT IMPLEMENTED
    def getReturnedDamge(self) -> float:
        return 0
    

    def getUtilityDamageDone(self, tick: int) -> int:
        return self.globalMatchContext.getPlayerDamageDoneTillTick(playerSteamId= self.playerSteamId, tick= tick)


    def getSupportUtilityUsed(self, tick: int) -> int:
        return self.globalMatchContext.getPlayerSupportDoneTillTick(playerSteamId= self.playerSteamId, tick= tick)


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
        rowData = [""] * len(Fight.features)
        playerTickData = self.getByIndex(self.parser.parsedDf, (tick, self.playerSteamId))
        if(len(playerTickData) == 0):
            return list()   # Skipped tick
        else:
            if self.minTick == -1:
                self.minTick = tick
            playerTickData: pd.Series = playerTickData.iloc[0, :]

        # currentTick = tick
        currentTick = tick - self.minTick
        X, Y, Z = self.getPlayerLocation(playerTickData= playerTickData)
        deltaX, deltaY, deltaZ = self.getLocationDeltas(playerTickData= playerTickData)
        yaw, pitch = self.getPlayerViewAngles(playerTickData= playerTickData)
        deltaYaw, deltaPitch = self.getViewAngleDeltas(playerTickData= playerTickData)
        utilityDmgDone = self.getUtilityDamageDone(tick= tick)
        supportUtilityUsed = self.getSupportUtilityUsed(tick= tick)
        kdr = self.getPlayerKDR()
        isFlashed = self.getPlayerBlind(playerSteamId= self.playerSteamId, tick= tick)
        isCrouched = self.getPlayerCrouched(playerTickData= playerTickData)
        isJumping = self.getPlayerJumped(playerTickData= playerTickData)
        isFiring = self.getPlayerFiring(tick= tick)
        
        self.setFeatures(rowData= rowData, featureName= "currentTick", featureValue= currentTick)
        # self.setFeatures(rowData= rowData, featureName= "playerId", featureValue= f"{self.playerSteamId} {playerTickData['name']}")
        self.setFeatures(rowData= rowData, featureName= "playerId", featureValue= self.playerSteamId)
        self.setFeatures(rowData= rowData, featureName= ("X", "Y", "Z"), featureValue= (X, Y, Z))
        self.setFeatures(rowData= rowData, featureName= ("deltaX", "deltaY", "deltaZ"), featureValue= (deltaX, deltaY, deltaZ))
        self.setFeatures(rowData= rowData, featureName= ("yaw", "pitch"), featureValue= (yaw, pitch))
        self.setFeatures(rowData= rowData, featureName= ("deltaYaw", "deltaPitch"), featureValue= (deltaYaw, deltaPitch))
        self.setFeatures(rowData= rowData, featureName= "deltaAimArc", featureValue= 0)
        self.setFeatures(rowData= rowData, featureName= "isFlashed", featureValue= isFlashed)
        self.setFeatures(rowData= rowData, featureName= "isCrouching", featureValue= isCrouched)
        self.setFeatures(rowData= rowData, featureName= "isJumping", featureValue= isJumping)
        self.setFeatures(rowData= rowData, featureName= "utilityDmgDone", featureValue= utilityDmgDone)
        self.setFeatures(rowData= rowData, featureName= "supportUtilityUsed", featureValue= supportUtilityUsed)
        self.setFeatures(rowData= rowData, featureName= "KDR", featureValue= kdr)
        self.setFeatures(rowData= rowData, featureName= "isFiring", featureValue= isFiring)

        if(tick in self.playerMatchContextObj.hurtTicks):
            targetHurtEvent = self.playerMatchContextObj.hurtTicks[tick]
            targetTickData = self.getByIndex(self.parser.parsedDf, (tick, targetHurtEvent["player_steamid"])).iloc[0, :] 

            targetX, targetY, targetZ = self.getPlayerLocation(playerTickData= targetTickData)
            targetDeltaX, targetDeltaY, targetDeltaZ = self.getLocationDeltas(playerTickData= targetTickData)
            dmgDone = self.getTargetTotalDamage(targetHurtEvent= targetHurtEvent)
            distToTarget = self.getDistanceToTarget((targetX, targetY, targetZ), (X, Y, Z))
            targetHitArea = self.getTargetHitSpot(targetHurtEvent= targetHurtEvent)
            penetrated = self.getShotPenetrated()
            weaponUsed = self.getUsedWeapon(targetHurtEvent= targetHurtEvent)
            weaponCategory = self.getWeaponCategory(weaponName= weaponUsed)
            isScoping = self.getPlayerScoping(playerTickData= playerTickData)
            targetBlind = self.getPlayerBlind(playerSteamId= self.targetSteamId, tick= tick)
            targetInSmoke = self.getSmokeInVision()
            targetReturnedDmg = self.getReturnedDamge()

            self.setFeatures(rowData= rowData, featureName= "targetId", featureValue= self.targetSteamId)
            self.setFeatures(rowData= rowData, featureName= ("targetX", "targetY", "targetZ"), featureValue= (targetX, targetY, targetZ))
            self.setFeatures(rowData= rowData, featureName= ("targetDeltaX", "targetDeltaY", "targetDeltaZ"), featureValue= (targetDeltaX, targetDeltaY, targetDeltaZ))
            self.setFeatures(rowData= rowData, featureName= "dmgDone", featureValue= dmgDone)
            self.setFeatures(rowData= rowData, featureName= "distToTarget", featureValue= distToTarget)
            self.setFeatures(rowData= rowData, featureName= "targetHitArea", featureValue= targetHitArea)
            self.setFeatures(rowData= rowData, featureName= "penetratedObject", featureValue= penetrated)
            self.setFeatures(rowData= rowData, featureName= "weaponUsed", featureValue= weaponUsed)
            self.setFeatures(rowData= rowData, featureName= "weaponCategory", featureValue= weaponCategory)
            self.setFeatures(rowData= rowData, featureName= "isScoping", featureValue= isScoping)
            self.setFeatures(rowData= rowData, featureName= "isTargetBlind", featureValue= targetBlind)
            self.setFeatures(rowData= rowData, featureName= "isTargetInSmoke", featureValue= targetInSmoke)
            self.setFeatures(rowData= rowData, featureName= "targetReturnedDmg", featureValue= targetReturnedDmg)
        
        self.setFeatures(rowData= rowData, featureName= "Label", featureValue= str(self.label))
        return rowData
    

    def buildFight(self) -> None:
        for tick in range(self.intervalStartTick, self.intervalEndTick + 1):
            rowData: list = self.buildFightTick(tick= tick)
            if len(rowData) != 0:
                self.dfRows.append(rowData)

        self.dfRows.append([""] * len(Fight.features))