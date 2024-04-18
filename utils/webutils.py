# webutils.py
# 04.03.2024

import utils.console as console
import utils.utils as utils

from utils.enums import Directories

import selenium.webdriver as webdriver
import requests
import os

from selenium.webdriver.common.by import By
from multiprocessing import Process
from pathlib import Path
from time import sleep


def GetWebdriver():
    options = webdriver.FirefoxOptions()
    options.add_argument("-headless")
    service = webdriver.FirefoxService("/snap/bin/geckodriver")
    driver = webdriver.Firefox(options=options, service=service)
    # driver.minimize_window()
    driver.maximize_window()
    return driver


def WebDriverCloseAllExtraTabs(driver):
    while len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[len(driver.window_handles) - 1])
        driver.close()
    driver.switch_to.window(driver.window_handles[0])


def DoesElementExistXPath(parent, xpath):
    try:
        parent.find_element(By.XPATH, xpath)
    except:
        return False
    return True


def DoesElementExistClassName(parent, class_name):
    try:
        parent.find_element(By.CLASS_NAME, class_name)
    except:
        return False
    return True


def DoesElementExistByID(parent, id):
    try:
        parent.find_element(By.ID, id)
    except:
        return False
    return True


def LoopUntilElementFoundByXPath(parent, xpath, loop_time=5):
    check = 0
    while not DoesElementExistXPath(parent, xpath):
        if check > loop_time:
            console.SubError("Couldn't find element with xpath: {0}".format(xpath))
            return None
        check += 0.1
        sleep(0.1)
    return parent.find_element(By.XPATH, xpath)


def LoopUntilElementFoundByClassName(parent, class_name, loop_time=5):
    check = 0
    while not DoesElementExistClassName(parent, class_name):
        if check > loop_time:
            console.SubError("Couldn't find element with class name: {0}".format(class_name))
            return None
        check += 0.1
        sleep(0.1)
    return parent.find_element(By.CLASS_NAME, class_name)


def LoopUntilElementNotFoundByClassName(parent, class_name, loop_time=5):
    check = 0
    while DoesElementExistClassName(parent, class_name):
        if check > loop_time:
            console.SubError("Element by class name: {0}, still exists".format(class_name))
            return False
        check += 0.1
        sleep(0.1)
    return True


def LoopUntilElementFoundByID(parent, id, loop_time=5):
    check = 0
    while not DoesElementExistByID(parent, id):
        if check > loop_time:
            console.SubError("Couldn't find element with id: {0}".format(id))
            return None
        check += 0.1
        sleep(0.1)
    return parent.find_element(By.ID, id)


def DoesElementTextEqual(parent, attribute_name, attribute_text):
    return parent.get_attribute(attribute_name) == attribute_text


def LoopUntilElementAttributeIsEqualText(parent, attribute_name, attribute_text, loop_time=5):
    check = 0
    while not DoesElementTextEqual(parent, attribute_name, attribute_text):
        if check > loop_time:
            console.SubError("Attribute with name: {0}, isn't equal to text: {1}".format(attribute_name, attribute_text))
            return False
        check += 0.1
        sleep(0.1)
    return True


def ScrollDownPage(driver, scrolls_amount, sleep_time):
    for i in range(0, scrolls_amount, 1):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(sleep_time)


# If you remove this url will be treated as list of single characters aka function will crash
def DownloadImage(url, image_path):
    try:
        image_bytes = requests.get(url, timeout=10).content
    except:
        return

    if len(image_bytes) != 0:
        utils.SaveImage(image_path, image_bytes, [("url", url)])


def BatchDownloadImages(urls):
    threads_busy = 0
    processes = []

    while len(urls) != 0 or threads_busy != 0:
        while len(urls) != 0 and threads_busy < os.cpu_count():
            end_idx = len(urls) - 1
            url = urls[end_idx]
            urls.pop(end_idx)

            process = Process(target=DownloadImage, args=(url, Directories.DownloadsTemporary + utils.RandomString() + ".png"))
            processes.append(process)
            process.start()
            threads_busy += 1

        for process in processes:
            if not process.is_alive():
                processes.remove(process)
                threads_busy -= 1

        sleep(0.01)


def DownloadUrls(array_urls_array, no_urls_message):
    any_urls = False
    for urls_array in array_urls_array:
        if len(urls_array) != 0:
            any_urls = True
            break

    if any_urls == False:
        console.SubError(no_urls_message)
        return False

    for urls_array in array_urls_array:
        BatchDownloadImages(urls_array)

    return True


def BatchDownloadMatchedImages(directory_name, matches):
    directory_path = Directories.DownloadsEncodings + directory_name + "/"
    Path(directory_path).mkdir(parents=False, exist_ok=True)

    threads_busy = 0
    processes = []

    downloaded_matches = 48
    while (len(matches) != 0 and downloaded_matches > 0) or threads_busy != 0:
        while len(matches) != 0 and downloaded_matches > 0 and threads_busy < os.cpu_count():
            end_idx = len(matches) - 1
            url = matches[end_idx][0]

            process = Process(target=DownloadImage, args=(url, directory_path + "{:.10f}".format(matches[end_idx][1]) + ".png"))
            processes.append(process)

            matches.pop(end_idx)
            process.start()
            threads_busy += 1
            downloaded_matches -= 1

        for process in processes:
            if not process.is_alive():
                processes.remove(process)
                threads_busy -= 1

        sleep(0.01)
