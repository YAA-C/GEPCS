from SingleFileParser import SingleFileParser
import multiprocessing
import os
import traceback
import cProfile
import pstats


def run(filePath) -> None:
    singleFileParser = SingleFileParser(filePath)
    singleFileParser.start()


def startProfiler(filePath):
    from parseLib import Logger
    from parseLib.Logger import log
    Logger.setProcessName(filePath)
    print(f"Starting - {filePath}")
    try:
        with cProfile.Profile() as pr:
            run(filePath= filePath)
        stats = pstats.Stats(pr)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.dump_stats(filename= f"./logs/{filePath}.prof")
    except Exception:
        log(traceback.format_exc())
        print(traceback.format_exc())
    else:
        print(f"Completed - {filePath}")


def startMp(filePaths):
    with multiprocessing.Pool(processes=5) as pool:
        pool.map(startProfiler, filePaths)
    from parseLib.Logger import compileLogs
    compileLogs(filePaths)


if __name__ == "__main__":
    files = [file for file in os.listdir("./DemoFiles/Demos/") if file[-4:] == '.dem']
    startMp(files)