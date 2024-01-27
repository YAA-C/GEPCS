from SingleFileParser import SingleFileParser
import multiprocessing
import os
import traceback


def startFunc(filePath):
    from parseLib import Logger
    from parseLib.Logger import log
    Logger.setProcessName(filePath)
    print(f"Starting - {filePath}")
    try:
        singleFileParser = SingleFileParser(filePath)
        singleFileParser.start()
    except Exception:
        log(traceback.format_exc())
        print(traceback.format_exc())
    else:
        print(f"Completed - {filePath}")


def startMp(filePaths):
    with multiprocessing.Pool(processes=5) as pool:
        pool.map(startFunc, filePaths)
    from parseLib.Logger import compileLogs
    compileLogs(filePaths)


if __name__ == "__main__":
    files = [file for file in os.listdir("./DemoFiles/Demos/") if file[-4:] == '.dem']
    startMp(files)