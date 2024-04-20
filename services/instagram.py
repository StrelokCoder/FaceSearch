# instgram.py
# 10.04.2024

import utils.webutils as webutils
import utils.console as console

import re

from selenium.webdriver.common.by import By
from time import sleep


class Instagram:
    SITE_LINK = "https://www.instagram.com/"

    # Cookies block webpage from loading
    DECLINE_COOKIES_CLASS = "_a9--._ap36._a9_1"

    # Have to click it before we start searching for photos, cause site will restructure after we click it and we want to see more photos anyway
    SHOW_MORE_IMAGES_XPATH = "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[2]/section/main/div/div[3]/div[1]/div/button"
    # Sometimes this will pop up, blocking doing anything on webpage
    CLOSE_LOG_TO_INSTAGRAM_XPATH = "/html/body/div[7]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div[1]/div"

    # In those rows images are hold
    IMAGES_ROW_CLASS = "_ac7v.xzboxd6.x11ulueq.x1f01sob.xwq5r7b.xcghwft"

    # Some posts are multiimage, we check if they are to open them and get other images
    IS_POST_WITH_ADDITIONAL_INFO_CLASS = "x1lliihq.x1n2onr6.x9bdzbf"
    IS_POST_MULTIIMAGE_VIEWBOX_PARAMETER = "0.0.48.48"

    # Info related to image
    IMAGE_OPEN_NEW_SITE_CLASS = "x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz._a6hd"
    IMAGE_LINK_CLASS = "x5yr21d.xu96u03.x10l6tqk.x13vifvy.x87ps6o.xh8yej3"

    def __init__(self):
        console.Task("Initialising instagram")

    def Init(self, driver):
        driver.get(self.SITE_LINK)

        cookies_decline = webutils.LoopUntilElementFoundByClassName(driver, self.DECLINE_COOKIES_CLASS, 10, False)
        if cookies_decline is not None:
            cookies_decline.click()

        # We have to wait, so cookies decline will get remembered
        sleep(5)

        console.SubTask("Successfully initialized instagram")
        return True

    def InitProfileImagesSearch(self, driver, profile_name):
        driver.get(self.SITE_LINK + profile_name)

        close_log_to_instagram = webutils.LoopUntilElementFoundByXPath(driver, self.CLOSE_LOG_TO_INSTAGRAM_XPATH)
        if close_log_to_instagram is None:
            return False
        driver.execute_script("arguments[0].click();", close_log_to_instagram)

        sleep(1)

        return True

    def ProfileImagesSearch(self, driver, profile_name):
        if not self.InitProfileImagesSearch(driver, profile_name):
            console.SubError("Failed to init profile search at instagram")
            raise Exception()

        images_info = []

        # driver = webutils.GetWebdriver()

        y = 0
        previous_padding_top = 0

        current_image_row = 0

        while True:
            current_padding_top = format(re.search("padding-top: (.*); position", driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[2]/section/main/div/div[3]/article/div[1]/div").get_attribute("style")).group(1))

            # Instagram loaded new row of images
            if current_padding_top != previous_padding_top:
                previous_padding_top = current_padding_top
                current_image_row -= 1

            driver.execute_script("window.scrollTo(0, arguments[0]);", y)
            y += 100
            sleep(1)

        return images_info
