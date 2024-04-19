# config.py
# 19.04.2024

from configparser import ConfigParser

import os


def GetDatabaseDownloadLimit():
    config = ConfigParser()
    config.read("config.ini")
    return int(config.get("main", "database_download_limit"))


def GetDownloadProcessesCount():
    config = ConfigParser()
    config.read("config.ini")
    processes_count = config.get("main", "download_processes_count")

    if processes_count == "cpu":
        return os.cpu_count()
    else:
        return int(processes_count)


def IsHeadlessMode():
    config = ConfigParser()
    config.read("config.ini")
    headless = config.get("main", "headless_mode")

    if headless == "true":
        return True
    elif headless == "false":
        return False


def GetSimilarityThreshold():
    config = ConfigParser()
    config.read("config.ini")
    return float(config.get("main", "similarity_threshold"))


def GetGeckodriverPath():
    config = ConfigParser()
    config.read("config.ini")
    return float(config.get("main", "similarity_threshold"))