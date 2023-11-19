import os
import pandas as pd
from parseLib.CustomDemoParser import CustomDemoParser
from parseLib.PlayerIntervalGenerator import PlayerIntervalGenerator

dirname = os.path.dirname(__file__)
file = os.path.join(dirname, 'DemoFiles\\test.dem')

parser = CustomDemoParser(targetFile= file)
result = parser.parseFile()

if not result:
    print(f"Cannot Parse : {file}")
    exit(1)

hurtEvents = parser.parsePlayerHurt()
print(len(hurtEvents))

steamIds = parser.parsedDf['steamid'].unique().tolist()

hurtEventsMerged = []

label = False
for player in steamIds:
    intervalGenerator = PlayerIntervalGenerator(hurtEvents, parser.parsedDf, player, label)
    playerIntervalsMerged = intervalGenerator.generateIntervals()
    hurtEventsMerged.extend(playerIntervalsMerged)

print(len(hurtEventsMerged))
mainDf:pd.DataFrame = pd.concat(hurtEventsMerged)
mainDf.to_csv("test.csv", index= False)

    
# for x in hurtEventsMerged:
#     print(x)
