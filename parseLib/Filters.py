class Filters:
    def __init__(self):
        self.hurtEventAllowedWeapons = set(["deagle", "revolver", "elite", "fiveseven", "glock", "hkp2000", "usp_silencer", "p250", "cz75a", "tec9", "bizon", "mac10", "mp7", "mp5sd", "mp9", "p90", "ump45", "ak47", "aug", "famas", "galilar", "m4a1", "m4a1_silencer", "sg556", "m249", "negev", "awp", "g3sg1", "scar20", "ssg08", "mag7", "nova", "sawedoff", "xm1014"])
        self.fireEventAllowedWeapons = set(["weapon_deagle", "weapon_elite", "weapon_fiveseven", "weapon_glock", "weapon_hkp2000", "weapon_usp_silencer", "weapon_cz75a", "weapon_p250", "weapon_tec9", "weapon_bizon", "weapon_mac10", "weapon_mp5sd", "weapon_mp7", "weapon_mp9", "weapon_ump45", "weapon_p90", "weapon_ak47", "weapon_aug", "weapon_famas", "weapon_galilar", "weapon_m4a1_silencer", "weapon_m4a1", "weapon_sg556", "weapon_awp", "weapon_ssg08", "weapon_g3sg1", "weapon_scar20", "weapon_mag7", "weapon_nova", "weapon_xm1014", "weapon_m249", "weapon_negev", "weapon_sawedoff"])
        self.weaponNameToCategory = {
            "weapon_deagle": "weapon_category_pistol",
            "weapon_elite": "weapon_category_pistol",
            "weapon_fiveseven": "weapon_category_pistol",
            "weapon_glock": "weapon_category_pistol",
            "weapon_hkp2000": "weapon_category_pistol",
            "weapon_usp_silencer": "weapon_category_pistol",
            "weapon_cz75a": "weapon_category_pistol",
            "weapon_p250": "weapon_category_pistol",
            "weapon_tec9": "weapon_category_pistol",
            "weapon_bizon": "weapon_category_smg",
            "weapon_mac10": "weapon_category_smg",
            "weapon_mp5sd": "weapon_category_smg",
            "weapon_mp7": "weapon_category_smg",
            "weapon_mp9": "weapon_category_smg",
            "weapon_ump45": "weapon_category_smg",
            "weapon_p90": "weapon_category_smg",
            "weapon_ak47": "weapon_category_ar",
            "weapon_aug": "weapon_category_ar",
            "weapon_famas": "weapon_category_ar",
            "weapon_galilar": "weapon_category_ar",
            "weapon_m4a1_silencer": "weapon_category_ar",
            "weapon_m4a1": "weapon_category_ar",
            "weapon_sg556": "weapon_category_ar",
            "weapon_awp": "weapon_category_sniper",
            "weapon_ssg08": "weapon_category_sniper",
            "weapon_g3sg1": "weapon_category_sniper",
            "weapon_scar20": "weapon_category_sniper",
            "weapon_mag7": "weapon_category_shotgun",
            "weapon_nova": "weapon_category_shotgun",
            "weapon_xm1014": "weapon_category_shotgun",
            "weapon_sawedoff": "weapon_category_shotgun",
            "weapon_m249": "weapon_category_lmg",
            "weapon_negev": "weapon_category_lmg"
        }


    def filterWeaponHurtEvents(self, hurtEvents: list) -> list:
        return [event for event in hurtEvents if event['weapon'] in self.hurtEventAllowedWeapons]


    def filterWeaponFireEvents(self, fireEvents: list) -> list:
        return [event for event in fireEvents if event['weapon'] in self.fireEventAllowedWeapons]


    def filterHeGrenadeHurtEvents(self, hurtEvents: list) -> list:
        return [event for event in hurtEvents if event['weapon'] == 'hegrenade']


    def filterPlayerHurtEvents(self, hurtEvents: list, playerSteamId: int, targetSteamId: int) -> list:
        return [event for event in hurtEvents if (event['attacker_steamid'] == playerSteamId and event['player_steamid'] == targetSteamId)]
    
    
    def filterPlayerFireEvents(self, fireEvents: list, playerSteamId: int) -> list:
        return [event for event in fireEvents if event['player_steamid'] == playerSteamId]
    

    def filterPlayerBlindEvents(self, blindEvents: list, playerSteamId: int) -> list:
        return [event for event in blindEvents if event['player_steamid'] == playerSteamId]
    

    def getWeaponCategory(self, weaponName: str) -> str:
        return self.weaponNameToCategory[weaponName]
    

    def filterHumanPlayers(self, players: list):
        return [player for player in players if (player > 76500000000000000 and player < 76600000000000000)]