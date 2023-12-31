from SingleFileParser import SingleFileParser
import multiprocessing
import os
import traceback


def startFunc(filePath):
    print(f"Starting - {filePath}")
    try:
        singleFileParser = SingleFileParser(filePath)
        singleFileParser.start()
    except Exception:
        print(traceback.format_exc())
    else:
        print(f"Completed - {filePath}")


def startMp(filePaths):
    with multiprocessing.Pool(processes=8) as pool:
        pool.map(startFunc, filePaths)


if __name__ == "__main__":
    files = [file for file in os.listdir("./DemoFiles/Demos/") if file[-4:] == '.dem']
    startMp(files)