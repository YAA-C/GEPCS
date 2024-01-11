from SingleFileParser import SingleFileParser
import multiprocessing
import os
import traceback
import time


def startFunc(filePath):
    print(f"Starting - {filePath}")
    try:
        t0 = time.time()        
        singleFileParser = SingleFileParser(filePath)
        singleFileParser.start()
        t1 = time.time()
        print("Time Taken: ", t1-t0)
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