from datetime import datetime
from pprint import pformat
import os


LOGDIR = "./logs/"
processName = "MAIN"
logFilePath = f"{LOGDIR}{processName}-log.log"


def setProcessName(_processName: str) -> None:
    global processName, logFilePath
    processName = _processName
    logFilePath = f"{LOGDIR}{processName}-log.log"


def compileLogs(ProcessList: list) -> None:
    logLines = []
    for processName in ProcessList:
        logFilePath = f"{LOGDIR}{processName}-log.log"
        if not os.path.isfile(logFilePath):
            # parsing stopped in the middle and this file never exists OR there are no logs for this file.
            continue
        with open(logFilePath, "r") as file:
            logLines.extend(file.readlines())
        filePath = os.path.join(os.getcwd(), logFilePath)
        os.remove(filePath)

    logFileName = f"[{datetime.now().strftime('%m-%d-%YT%H-%M-%S')}]-run-log.log"
    with open(f"{LOGDIR}{logFileName}", "a") as file:
        file.writelines(logLines)
    print(f"Run logs at {LOGDIR}{logFileName}")


def log(*msgs: object, tag: str = "INFO") -> None:
    global logFilePath
    msg = " ".join([str(ele) for ele in msgs])
    text = f"[{processName}] [{datetime.now().strftime('%H:%M:%S')}] [{tag}] {msg}\n"
    with open(logFilePath, "a") as file:
        file.write(text)


def logp(msg: object, *, tag: str = "INFO") -> None:
    global logFilePath
    text = f"[{processName}] [{datetime.now().strftime('%H:%M:%S')}] [{tag}] \n{pformat(msg)}\n"
    with open(logFilePath, "a") as file:
        file.write(text)