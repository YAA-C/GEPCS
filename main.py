import multiprocessing
import os
import traceback
import cProfile
import pstats
import argparse
from datetime import datetime
from SingleFileParser import SingleFileParser
from src.utils import Logger
from src.utils.Logger import log


def run(filePath, fileVerdict) -> None:
    singleFileParser = SingleFileParser(filePath, fileVerdict)
    singleFileParser.start()


def startProfiler(fileData):
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


if __name__ == "__main__":
    argParser = argparse.ArgumentParser(description="Parse CSGO Demo (.dem) files.")
    argParser.add_argument("-v", "--verdict", type=int, help="Verdict for all players in the demo file/files. Either 1 (True) or 0 (False)")
    argParser.add_argument("-c", "--compile", action='store_true', help="compile all generate csv files into single csv file.")
    argParser.add_argument('--version', action='version', version='VERSION: 1.0', help='Show parser version')
    args = argParser.parse_args()

    Logger.setProcessName("DRIVER")

    verdict: bool | None = None
    if args.verdict is not None:
        # Verdict provided, check if verdict is illegal
        assert int(args.verdict) in (0, 1), "Unknown Verdict. Allowed values: Either 1 (True) or 0 (False)"
        verdict = False if int(args.verdict) == 0 else True

    fileData = [(file, verdict) for file in os.listdir("./DemoFiles/Demos/") if file[-4:] == '.dem']    
    startMultiprocessing(fileData)

    if args.compile:
        from src.utils.csvConcat import concatenate_csv_files

        print("Compiling CSV Files...")
        log("Compiling CSV Files...")
        
        # Get the current directory (should be 'GEPCS')
        current_dir: str = os.getcwd()

        # Construct the path to the './DemoFiles/csv' folder
        demo_files_dir = os.path.join(current_dir, 'DemoFiles', 'csv')

        log("Located CSV directory:", demo_files_dir)

        output_file = f"output-{datetime.now().strftime('%H-%M-%S')}.csv"
        concatenate_csv_files(demo_files_dir, output_file) 

    from src.utils.Logger import compileLogs

    # addition of [Driver process name, anything] 
    fileData.append(["DRIVER", None])
    compileLogs(fileData)