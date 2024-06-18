# facebook.py
# 11.04.2024

import utils.webutils as webutils
import utils.console as console

import re

from selenium.webdriver.common.by import By
from time import sleep


class Facebook:
    SITE_LINK = "https://www.facebook.com/"
    SITE_LINK_ADD_PHOTOS_WITH = "/photos"
    SITE_LINK_ADD_PHOTOS_BY = "/photos_by"

    # Cookies block doing anything on whole webpage
    DECLINE_COOKIES_CLASS = "_42ft._4jy0._al66._4jy3._4jy1.selected._51sy"
    # Decline cookies while searching, when you declined cookies max 2 minutes before using profile search and than start searching it won't first appear during Init
    DECLINE_COOKIES_WHILE_SEARCHING_XPATH = "/html/body/div[3]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div[1]/div[2]"

    # Appears every time you open profile on facebook to ask you to log in
    CLOSE_LOG_TO_FACEBOOK_XPATH = "/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/div"

    # Better quality image stuff
    BETTER_QUALITY_IMAGES_SITE_SRC_CLASS = "x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.x1heor9g.x1sur9pj.xkrqix3.x1lliihq.x5yr21d.x1n2onr6.xh8yej3"
    BETTER_QUALITY_IMAGE_SRC_CLASS = "x1bwycvy.x193iq5w.x4fas0m.x19kjcj4"
    BETTER_QUALITY_IMAGE_PREVIOUS_CLASS = "x14yjl9h.xudhj91.x18nykt9.xww2gxu.x6s0dn4.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x3nfvp2.xl56j7k.x1n2onr6.x1qhmfi1.xsdox4t.x1useyqa"

    def __init__(self):
        console.Task("Initialising facebook")

    def Init(self, driver):
        driver.get(self.SITE_LINK)

        cookies_decline = webutils.LoopUntilElementFoundByClassName(driver, self.DECLINE_COOKIES_CLASS, 5, False)
        if cookies_decline is not None:
            driver.execute_script("arguments[0].click();", cookies_decline)

        # We have to wait, so cookies decline will get remembered by facebook
        sleep(5)

        console.SubTask("Successfully initialized facebook")
        return True

    def InitProfileImagesSearch(self, driver, profile_name, photos_with):
        if photos_with is True:
            driver.get(self.SITE_LINK + profile_name + self.SITE_LINK_ADD_PHOTOS_WITH)
        else:
            driver.get(self.SITE_LINK + profile_name + self.SITE_LINK_ADD_PHOTOS_BY)

        # Facebook do be remembering
        sleep(1)
        if webutils.DoesElementExistXPath(driver, self.DECLINE_COOKIES_WHILE_SEARCHING_XPATH):
            driver.find_element(By.XPATH, self.DECLINE_COOKIES_WHILE_SEARCHING_XPATH).click()

        close_log_to_facebook = webutils.LoopUntilElementFoundByXPath(driver, self.CLOSE_LOG_TO_FACEBOOK_XPATH)
        if close_log_to_facebook is None:
            return False
        driver.execute_script("arguments[0].click();", close_log_to_facebook)

        sleep(2.5)

        return True

    def ProfileImagesSearch(self, driver, profile_name):
        if not self.InitProfileImagesSearch(driver, profile_name, False):
            console.SubError("Failed to init profile search at facebook")
            raise Exception()

        images_url = []

        if len(driver.find_elements(By.CLASS_NAME, self.BETTER_QUALITY_IMAGES_SITE_SRC_CLASS)) == 0:
            return images_url

        # What thingy below does is basically reload first photo to get it's real post url
        driver.execute_script("arguments[0].click();", driver.find_elements(By.CLASS_NAME, self.BETTER_QUALITY_IMAGES_SITE_SRC_CLASS)[0])
        sleep(2.5)
        driver.execute_script("arguments[0].click();", driver.find_elements(By.CLASS_NAME, self.BETTER_QUALITY_IMAGE_PREVIOUS_CLASS)[0])
        sleep(5)
        driver.execute_script("arguments[0].click();", driver.find_elements(By.CLASS_NAME, self.BETTER_QUALITY_IMAGE_PREVIOUS_CLASS)[1])
        sleep(2.5)

        image_url = driver.find_element(By.CLASS_NAME, self.BETTER_QUALITY_IMAGE_SRC_CLASS).get_attribute("src")
        first_image_site_fbid = format(re.search("fbid=(.*)&set=", driver.current_url).group(1))

        # Scroll through images until you find first image of this person
        while True:
            images_url.append(image_url)

            driver.execute_script("arguments[0].click();", driver.find_elements(By.CLASS_NAME, self.BETTER_QUALITY_IMAGE_PREVIOUS_CLASS)[1])

            while True:
                try:
                    new_image_url = driver.find_element(By.CLASS_NAME, self.BETTER_QUALITY_IMAGE_SRC_CLASS).get_attribute("src")
                    if image_url != new_image_url:
                        image_url = new_image_url
                        break
                except:
                    continue
                continue

            if first_image_site_fbid == format(re.search("fbid=(.*)&set=", driver.current_url).group(1)):
                break

        return images_url
