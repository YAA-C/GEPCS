from demoparser import DemoParser
import pandas as pd

class CustomDemoParser:
    def __init__(self, targetFile: str) -> None:
        self.props = ['X','Y','Z','weapon_name','velocity_X','velocity_Y','velocity_Z','viewangle_yaw','viewangle_pitch','ducked','scoped','health','flash_duration','armor','headshots_this_round','has_helmet','is_walking','last_made_noise_time','spotted','team_num','vec_view_offset0','vec_view_offset1','jump_time_msecs','duck_time_msecs','in_duck_jump','is_ducking','round','is_freeze_period','is_match_started','is_warmup_period']
        self.targetFile = targetFile
        self.parsedDf: pd.DataFrame

    def parseFile(self) -> bool:
        try:
            self.parser = DemoParser(self.targetFile)
            self.parsedDf = self.parser.parse_ticks(self.props)
        except Exception as e:
            print(e)
            return False
        return True
    
    def parsePlayerHurt(self) -> list:
        return self.parser.parse_events("player_hurt")