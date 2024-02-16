import pandas as pd
from .CustomMath import UnitVector, eularDistance, getArcLength
from .GlobalMatchContext import GlobalMatchContext
from .PlayerMatchContext import PlayerMatchContext
from .CustomDemoParser import CustomDemoParser
from .Filters import Filters
from .Logger import logp, log


class PlayerCache:
    def __init__(self) -> None:
        self.prevValueDict: dict = dict()
        self.curValueDict: dict = dict()

    def update(self) -> None:
        self.prevValueDict = self.curValueDict.copy()


class Fight:
    features: list = [
        "currentTick", 
        "playerId",
        "playerName",
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
        "targetName",
        "targetX", "targetY", "targetZ",
        "targetDeltaX", "targetDeltaY", "targetDeltaZ",
        "dmgDone", 
        "distToTarget", 
        "targetHitArea", 
        "weaponUsed",
        "weaponCategory",
        "isScoping",
        "isTargetBlind", 
        "shotTargetThroughSmoke", 
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
        self.playerDataCache: PlayerCache = PlayerCache()
        self.targteDataCache: PlayerCache = PlayerCache()
        self.generateDistances()
        self.currentDistanceIndex: int = 0
        

    def generateDistances(self) -> None:
        self.precomputedDistances: list = []
        for tick in range(self.intervalStartTick, self.intervalEndTick + 1):
            if tick not in self.playerMatchContextObj.hurtTicks:
                continue
            
            playerTickData: pd.Series = self.getByIndex(self.parser.parsedDf, (tick, self.playerSteamId))
            targetTickData: pd.Series = self.getByIndex(self.parser.parsedDf, (tick, self.targetSteamId))

            playerX, playerY, playerZ = self.getPlayerLocation(playerTickData= playerTickData)
            targetX, targetY, targetZ = self.getPlayerLocation(playerTickData= targetTickData)

            distance = eularDistance(X= (playerX, playerY, playerZ), Y= (targetX, targetY, targetZ))
            self.precomputedDistances.append({
                "tick": tick,
                "distance": distance
            })


    def getByIndex(self, df: pd.DataFrame, index: tuple[int, int]) -> pd.Series | None:
        if index in df.index:
            data: pd.Series | pd.DataFrame = df.loc[index]
            if type(data) == pd.Series:
                return data
            return data.iloc[0, :]
        return None

    
    def convertViewAngleToLinearDelta(self, circularAngle: float, angleName: str, playerCache: PlayerCache):
        linearAngleDelta = 0

        if angleName == 'Pitch':
            if angleName in playerCache.prevValueDict:
                linearAngleDelta = circularAngle - playerCache.prevValueDict[angleName]
                
        elif angleName == 'Yaw':
            if angleName in playerCache.prevValueDict:
                distance = abs(circularAngle - playerCache.prevValueDict[angleName])
                circularDistance = 360 - distance
                if(distance < circularDistance):
                    linearAngleDelta = circularAngle - playerCache.prevValueDict[angleName]
                else:
                    linearAngleDelta = circularDistance if (circularAngle < playerCache.prevValueDict[angleName]) else -circularDistance
        
        playerCache.curValueDict[angleName] = circularAngle
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
    

    def getLocationDeltas(self, playerLocation: tuple, playerCache: PlayerCache) -> tuple:
        X, Y, Z = playerLocation[0], playerLocation[1], playerLocation[2]
        deltaX, deltaY, deltaZ = 0.0, 0.0, 0.0

        if('X' in playerCache.prevValueDict):
            deltaX = X - playerCache.prevValueDict['X']
            deltaY = Y - playerCache.prevValueDict['Y']
            deltaZ = Z - playerCache.prevValueDict['Z']
            
        playerCache.curValueDict['X'] = X
        playerCache.curValueDict['Y'] = Y
        playerCache.curValueDict['Z'] = Z
        return (deltaX, deltaY, deltaZ)


    def getPlayerViewAngles(self, playerTickData: pd.Series) -> tuple:
        yaw = playerTickData['m_angEyeAngles[1]']
        pitch = playerTickData['m_angEyeAngles[0]']
        pitch = pitch - 360 if (pitch > 100) else pitch
        assert yaw >=0 and yaw <= 360, "Wrong yaw values"
        assert pitch <= 90 and pitch >= -90, "Wrong pitch Values"
        return (yaw, pitch)
    

    def getViewAngleDeltas(self, playerTickData: pd.Series, playerCache: PlayerCache) -> tuple:
        yaw, pitch = self.getPlayerViewAngles(playerTickData= playerTickData)
        deltaYaw = self.convertViewAngleToLinearDelta(circularAngle= yaw, angleName= 'Yaw', playerCache= playerCache)
        deltaPitch = self.convertViewAngleToLinearDelta(circularAngle= pitch, angleName= 'Pitch', playerCache= playerCache)
        return (deltaYaw, deltaPitch)


    def getViewAngleDeltaAimArc(self, playerTickData: pd.Series, tick: int, playerCache: PlayerCache) -> float:
        if 'Yaw' not in playerCache.prevValueDict:
            # First tick of fight
            return 0.0
        
        prevYaw: float = playerCache.prevValueDict['Yaw']
        prevPitch: float = playerCache.prevValueDict['Pitch'] + 90.0   #Pitch is in -90 to +90, we need it in 0 to 180
        yaw, pitch = self.getPlayerViewAngles(playerTickData= playerTickData)
        pitch += 90.0   #Pitch is in -90 to +90, we need it in 0 to 180
        distanceToTarget: float = self.precomputedDistances[self.currentDistanceIndex]["distance"]
        prevVector: UnitVector = UnitVector(yaw= prevYaw, pitch= prevPitch)
        curVector: UnitVector = UnitVector(yaw= yaw, pitch= pitch)
        if self.precomputedDistances[self.currentDistanceIndex]["tick"] == tick:
            # completed partial arc, goto next partial arc
            self.currentDistanceIndex += 1

        return getArcLength(distanceToTarget, prevVector, curVector)


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


    def getUsedWeapon(self, targetHurtEvent: dict) -> str:
        return targetHurtEvent["weapon"]


    def getWeaponCategory(self, weaponName: str) -> str:
        return Filters().getWeaponCategory(weaponName= weaponName)


    def getPlayerScoping(self, playerTickData: pd.Series) -> bool:
        return bool(playerTickData["m_bIsScoped"])


    def getPlayerBlind(self, playerSteamId:int, tick: int) -> float:
        return self.globalMatchContext.getPlayerBlindness(playerSteamId= playerSteamId, tick= tick)


    def getSmokeInVision(self, tick: int, playerLocationA: tuple, playerLocationB: tuple) -> bool:
        return self.globalMatchContext.getIsSmokeBetweenPlayers(tick, playerLocationA, playerLocationB)


    #NOT IMPLEMENTED
    def getReturnedDamge(self, tick) -> int:
        return self.playerMatchContextObj.getDamageToPlayerDoneTillTick(tick= tick)
    

    def getUtilityDamageDone(self, tick: int) -> int:
        return self.playerMatchContextObj.getDamageToTargetDoneTillTick(tick= tick)


    def getSupportUtilityUsed(self, tick: int) -> int:
        return self.playerMatchContextObj.getPlayerSupportDoneTillTick(tick= tick)


    def getPlayerKDR(self, tick: int) -> float:
        return self.playerMatchContextObj.getPlayerKDRTillTick(tick= tick)


    def setFeatures(self, rowData: list, featureName: object, featureValue: object) -> None:
        if type(featureName) == list or type(featureName) == tuple:
            assert len(featureName) == len(featureValue), "names and value should be of same length"
            for i in range(len(featureName)):
                rowData[self.featureNameToIndex[featureName[i]]] = featureValue[i]
        else:
            rowData[self.featureNameToIndex[featureName]] = featureValue


    def buildFightTick(self, tick: int) -> list | None:
        rowData = [""] * len(Fight.features)
        playerTickData: pd.Series | None = self.getByIndex(self.parser.parsedDf, (tick, self.playerSteamId))
        if(playerTickData is None):
            return None  # Skipped tick
        else:
            if self.minTick == -1:
                self.minTick = tick

        currentTick = tick
        # currentTick = tick - self.minTick
        X, Y, Z = self.getPlayerLocation(playerTickData= playerTickData)
        deltaX, deltaY, deltaZ = self.getLocationDeltas(playerLocation= (X, Y, Z), playerCache= self.playerDataCache)
        yaw, pitch = self.getPlayerViewAngles(playerTickData= playerTickData)
        deltaYaw, deltaPitch = self.getViewAngleDeltas(playerTickData= playerTickData, playerCache= self.playerDataCache)
        deltaAimArc = self.getViewAngleDeltaAimArc(playerTickData= playerTickData, tick= tick, playerCache= self.playerDataCache)
        utilityDmgDone = self.getUtilityDamageDone(tick= tick)
        supportUtilityUsed = self.getSupportUtilityUsed(tick= tick)
        kdr = self.getPlayerKDR(tick= tick)
        isFlashed = self.getPlayerBlind(playerSteamId= self.playerSteamId, tick= tick)
        isCrouched = self.getPlayerCrouched(playerTickData= playerTickData)
        isJumping = self.getPlayerJumped(playerTickData= playerTickData)
        isFiring = self.getPlayerFiring(tick= tick)
        
        self.setFeatures(rowData= rowData, featureName= "currentTick", featureValue= currentTick)
        self.setFeatures(rowData= rowData, featureName= "playerId", featureValue= self.playerSteamId)
        self.setFeatures(rowData= rowData, featureName= "playerName", featureValue= playerTickData["name"])
        self.setFeatures(rowData= rowData, featureName= ("X", "Y", "Z"), featureValue= (X, Y, Z))
        self.setFeatures(rowData= rowData, featureName= ("deltaX", "deltaY", "deltaZ"), featureValue= (deltaX, deltaY, deltaZ))
        self.setFeatures(rowData= rowData, featureName= ("yaw", "pitch"), featureValue= (yaw, pitch))
        self.setFeatures(rowData= rowData, featureName= ("deltaYaw", "deltaPitch"), featureValue= (deltaYaw, deltaPitch))
        self.setFeatures(rowData= rowData, featureName= "deltaAimArc", featureValue= deltaAimArc)
        self.setFeatures(rowData= rowData, featureName= "isFlashed", featureValue= isFlashed)
        self.setFeatures(rowData= rowData, featureName= "isCrouching", featureValue= isCrouched)
        self.setFeatures(rowData= rowData, featureName= "isJumping", featureValue= isJumping)
        self.setFeatures(rowData= rowData, featureName= "utilityDmgDone", featureValue= utilityDmgDone)
        self.setFeatures(rowData= rowData, featureName= "supportUtilityUsed", featureValue= supportUtilityUsed)
        self.setFeatures(rowData= rowData, featureName= "KDR", featureValue= kdr)
        self.setFeatures(rowData= rowData, featureName= "isFiring", featureValue= isFiring)

        if(tick in self.playerMatchContextObj.hurtTicks):
            targetHurtEvent = self.playerMatchContextObj.hurtTicks[tick]
            targetTickData: pd.Series = self.getByIndex(self.parser.parsedDf, (tick, targetHurtEvent["player_steamid"])) 

            targetX, targetY, targetZ = self.getPlayerLocation(playerTickData= targetTickData)
            targetDeltaX, targetDeltaY, targetDeltaZ = self.getLocationDeltas(playerLocation= (targetX, targetY, targetZ), playerCache= self.targteDataCache)
            dmgDone = self.getTargetTotalDamage(targetHurtEvent= targetHurtEvent)
            distToTarget = self.getDistanceToTarget((targetX, targetY, targetZ), (X, Y, Z))
            targetHitArea = self.getTargetHitSpot(targetHurtEvent= targetHurtEvent)
            weaponUsed = self.getUsedWeapon(targetHurtEvent= targetHurtEvent)
            weaponCategory = self.getWeaponCategory(weaponName= weaponUsed)
            isScoping = self.getPlayerScoping(playerTickData= playerTickData)
            targetBlind = self.getPlayerBlind(playerSteamId= self.targetSteamId, tick= tick)
            targetInSmoke = self.getSmokeInVision(tick= tick, playerLocationA= (X, Y, Z), playerLocationB=(targetX, targetY, targetZ))
            targetReturnedDmg = self.getReturnedDamge(tick= tick)

            self.setFeatures(rowData= rowData, featureName= "targetId", featureValue= self.targetSteamId)
            self.setFeatures(rowData= rowData, featureName= "targetName", featureValue= targetTickData["name"])
            self.setFeatures(rowData= rowData, featureName= ("targetX", "targetY", "targetZ"), featureValue= (targetX, targetY, targetZ))
            self.setFeatures(rowData= rowData, featureName= ("targetDeltaX", "targetDeltaY", "targetDeltaZ"), featureValue= (targetDeltaX, targetDeltaY, targetDeltaZ))
            self.setFeatures(rowData= rowData, featureName= "dmgDone", featureValue= dmgDone)
            self.setFeatures(rowData= rowData, featureName= "distToTarget", featureValue= distToTarget)
            self.setFeatures(rowData= rowData, featureName= "targetHitArea", featureValue= targetHitArea)
            self.setFeatures(rowData= rowData, featureName= "weaponUsed", featureValue= weaponUsed)
            self.setFeatures(rowData= rowData, featureName= "weaponCategory", featureValue= weaponCategory)
            self.setFeatures(rowData= rowData, featureName= "isScoping", featureValue= isScoping)
            self.setFeatures(rowData= rowData, featureName= "isTargetBlind", featureValue= targetBlind)
            self.setFeatures(rowData= rowData, featureName= "shotTargetThroughSmoke", featureValue= targetInSmoke)
            self.setFeatures(rowData= rowData, featureName= "targetReturnedDmg", featureValue= targetReturnedDmg)
        
        self.setFeatures(rowData= rowData, featureName= "Label", featureValue= str(self.label))
        
        # Make current values prevValues for next tick
        self.playerDataCache.update()
        self.targteDataCache.update()

        return rowData
    

    def buildFight(self) -> None:
        for tick in range(self.intervalStartTick, self.intervalEndTick + 1):
            rowData: list | None = self.buildFightTick(tick= tick)
            if rowData is not None:
                self.dfRows.append(rowData)

        self.dfRows.append([""] * len(Fight.features))