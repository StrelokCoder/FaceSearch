# console.py
# 04.03.2024

import sys
import os

from colorama import Fore, Style


def Clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def Task(text):
    print(Fore.BLUE + Style.BRIGHT + "\n:: {0}:".format(text))


def SubTask(text):
    print(Fore.GREEN + Style.BRIGHT + "    -> " + Fore.RESET + Style.RESET_ALL + text)


def Error(text):
    print(Fore.RED + Style.BRIGHT + "\n:: {0}:".format(text))


def SubError(text):
    print(Fore.RED + Style.BRIGHT + "    -> {0}".format(text))


def NewLine():
    print("\n")


def SuppressPrint():
    sys.stdout = open(os.devnull, "w")


def RestorePrint():
    sys.stdout = sys.__stdout__
