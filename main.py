import multiprocessing
import os
import traceback
import cProfile
import pstats
import argparse
from SingleFileParser import SingleFileParser


def run(filePath, fileVerdict) -> None:
    singleFileParser = SingleFileParser(filePath, fileVerdict)
    singleFileParser.start()


def startProfiler(fileData):
    from parseLib import Logger
    from parseLib.Logger import log

    filePath: str = fileData[0]
    fileVerdict: bool = fileData[1]

    Logger.setProcessName(filePath)
    print(f"Starting - {filePath}")
    try:
        with cProfile.Profile() as pr:
            run(filePath= filePath, fileVerdict= fileVerdict)
        stats = pstats.Stats(pr)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.dump_stats(filename= f"./logs/{filePath}.prof")
    except Exception:
        log(traceback.format_exc())
        print(traceback.format_exc())
    else:
        print(f"Completed - {filePath}")


def startMultiprocessing(fileData: list):
    with multiprocessing.Pool(processes=5) as pool:
        pool.map(startProfiler, fileData)
    from parseLib.Logger import compileLogs
    compileLogs(fileData)


if __name__ == "__main__":
    argParser = argparse.ArgumentParser(description="Parse CSGO Demo (.dem) files.")
    argParser.add_argument("-v", "--verdict", type=int, help="Verdict for all players in the demo file/files. Either 1 (True) or 0 (False)")
    argParser.add_argument("-c", "--compile", type=int, help="compile all generate csv files into single csv file.")
    argParser.add_argument('--version', action='version', version='VERSION: 1.0', help='Show parser version')
    args = argParser.parse_args()

    verdict: bool | None = None
    if args.verdict:
        # Verdict provided, check if verdict is illegal
        assert int(argParser.verdict) in (0, 1), "Unknown Verdict. Allowed values: Either 1 (True) or 0 (False)"
        verdict = False if int(argParser.verdict) == 0 else True

    fileData = [(file, verdict) for file in os.listdir("./DemoFiles/Demos/") if file[-4:] == '.dem']    
    startMultiprocessing(fileData)

    if args.compile:
        from datetime import datetime
        from utils.csvConcat import concatenate_csv_files
        
        # Get the current directory (should be 'GEPCS')
        current_dir: str = os.getcwd()

        # Construct the path to the './DemoFiles/csv' folder
        demo_files_dir = os.path.join(current_dir, 'DemoFiles', 'csv')

        print("Located CSV directory:", demo_files_dir)

        output_file = f"output-{datetime.now().strftime('%H:%M:%S')}.csv"
        concatenate_csv_files(demo_files_dir, output_file)