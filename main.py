from SingleFileParser import SingleFileParser
import multiprocessing
import os


def startFunc(filePath):
    print(f"Starting - {filePath}")
    try:
        singleFileParser = SingleFileParser(filePath)
        singleFileParser.start()
    except Exception as e:
        pass
    else:
        print(f"Completed - {filePath}")


def startMp(filePaths):
    with multiprocessing.Pool(processes=8) as pool:
        pool.map(startFunc, filePaths)


if __name__ == "__main__":
    files = os.listdir("./DemoFiles/Demos/")
    startMp(files)