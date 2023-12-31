class Filters:
    def __init__(self):
        pass    

    def filterWeaponHurtEvents(self, hurtEvents: list) -> list:
        weaponNames = ["deagle", "revolver", "elite", "fiveseven", "glock", "hkp2000", "usp_silencer", "p250", "cz75a", "tec9", "mag7", "nova", "sawedoff", "xm1014", "bizon", "mac10", "mp7", "mp5sd", "mp9", "p90", "ump45", "ak47", "aug", "famas", "galilar", "m4a1", "m4a1_silencer", "sg556", "m249", "negev", "awp", "g3sg1", "scar20", "ssg08"]
        return [event for event in hurtEvents if event['weapon'] in weaponNames]


    def filterHeGrenadeHurtEvents(self, hurtEvents: list) -> list:
        return [event for event in hurtEvents if event['weapon'] == 'hegrenade']


    def filterPlayerHurtEvents(self, hurtEvents: list, playerSteamId: int, targetSteamId: int) -> list:
        return [event for event in hurtEvents if (event['attacker_steamid'] == playerSteamId and event['player_steamid'] == targetSteamId)]
    
    
    def filterHumanPlayers(self, players: list):
        return [player for player in players if (player > 76500000000000000 and player < 76600000000000000)]