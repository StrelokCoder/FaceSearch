# instgram.py
# 10.04.2024

import utils.webutils as webutils
import utils.console as console
import utils.config as config

import re

from selenium.webdriver.common.by import By
from time import sleep


class Instagram:
    SITE_LINK = "https://www.instagram.com/"
    SITE_LINK_NEW_WINDOW = "https://www.instagram.com"

    # Cookies block webpage from loading
    DECLINE_COOKIES_CLASS = "_a9--._ap36._a9_1"

    # Have to click it before we start searching for photos, cause site will restructure after we click it(class names don't change) and we want to see more photos anyway
    SHOW_MORE_IMAGES_XPATH = "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[2]/section/main/div/div[3]/div[1]/div/button"
    # Sometimes this will pop up, blocking doing anything on webpage
    CLOSE_LOG_TO_INSTAGRAM_XPATH = "/html/body/div[7]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div[1]/div"

    # Will be used to read if more images are visible
    ROWS_BODY_XPATH = "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[2]/section/main/div/div[3]/article/div/div"
    # In those rows images are hold
    IMAGES_ROW_CLASS = "_ac7v.xzboxd6.x11ulueq.x1f01sob.xwq5r7b.xcghwft"

    # Some posts are multiimage, we check if they are to open them and get other images
    IS_POST_WITH_ADDITIONAL_INFO_CLASS = "x1lliihq.x1n2onr6.x9bdzbf"
    IS_POST_MULTIIMAGE_VIEWBOX_PARAMETER = "0 0 48 48"

    # Holds link to new site
    IMAGE_NEW_SITE_LINK_CLASS = "x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz._a6hd"
    # Holds link to image in main site
    IMAGE_LINK_CLASS = "x5yr21d.xu96u03.x10l6tqk.x13vifvy.x87ps6o.xh8yej3"

    # New site managment
    IMAGES_HOLDER_CLASS = "_acay"
    NEW_SITE_GO_LEFT_CLASS = "._afxv._al46._al47"
    NEW_SITE_GO_RIGHT_CLASS = "._afxw._al46._al47"

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

        # Not everyone has so many images, that this will appear
        show_more_images = webutils.LoopUntilElementFoundByXPath(driver, self.SHOW_MORE_IMAGES_XPATH)
        if show_more_images is not None:
            driver.execute_script("arguments[0].click();", show_more_images)

        sleep(1)

        if config.IsHavingInstagramAccount():
            console.SubTask("\nLog into your instagram account\n")
            sleep(120)

        return True

    def ProfileImagesSearch(self, driver, profile_name):
        if not self.InitProfileImagesSearch(driver, profile_name):
            console.SubError("Failed to init profile search at instagram")
            raise Exception()

        images_info = []

        y = 0
        break_count = 0
        previous_padding_top = "0px"

        current_image_row = 0

        while True:
            images_rows = driver.find_elements(By.CLASS_NAME, self.IMAGES_ROW_CLASS)
            current_row_count = len(images_rows)

            while current_image_row < current_row_count:
                break_count = 0

                link_holders = images_rows[current_image_row].find_elements(By.CLASS_NAME, self.IMAGE_NEW_SITE_LINK_CLASS)
                current_image_row += 1

                for link_holder in link_holders:
                    # Check if site has additional info(multiple images per post) and if so open this post in new site, !!!!!!!!!!!!!!!!!! Doesn't work, cause viewBox returns none for reason I don't know
                    if webutils.DoesElementExistClassName(link_holder, self.IS_POST_WITH_ADDITIONAL_INFO_CLASS) == True and link_holder.find_element(By.CLASS_NAME, self.IS_POST_WITH_ADDITIONAL_INFO_CLASS).get_attribute("viewBox") == self.IS_POST_MULTIIMAGE_VIEWBOX_PARAMETER:
                        driver.get(self.SITE_LINK_NEW_WINDOW + link_holder.get_attribute("href"))
                    else:
                        images_info.append(link_holder.find_element(By.CLASS_NAME, self.IMAGE_LINK_CLASS).get_attribute("src"))
                    sleep(0.05)

                # Opened site with more images
                while len(driver.window_handles) != 1:
                    driver.switch_to.window(driver.window_handles[len(driver.window_handles) - 1])
                    sleep(2)

                    images_holder = driver.find_element(By.CLASS_NAME, self.IMAGES_HOLDER_CLASS)

                    while True:
                        if webutils.DoesElementExistClassName(images_holder, self.NEW_SITE_GO_LEFT_CLASS) == False:
                            images_info.append(images_holder.find_elements(By.CLASS_NAME, self.IMAGE_LINK_CLASS))[0]
                        else:
                            images_info.append(images_holder.find_elements(By.CLASS_NAME, self.IMAGE_LINK_CLASS))[1]

                        if webutils.DoesElementExistClassName(images_holder, self.NEW_SITE_GO_RIGHT_CLASS) == False:
                            break
                        else:
                            driver.execute_script("arguments[0].click();", images_holder.find_element(By.CLASS_NAME, self.NEW_SITE_GO_RIGHT_CLASS))
                            sleep(2)

                    driver.close()
                    sleep(0.05)
                driver.switch_to.window(driver.window_handles[0])

            current_padding_top = format(re.search("padding-top: (.*); position", driver.find_element(By.XPATH, self.ROWS_BODY_XPATH).get_attribute("style")).group(1))

            # Instagram loaded new row of images
            if current_padding_top != previous_padding_top:
                previous_padding_top = current_padding_top
                current_image_row -= 1
                break_count = 0
            else:
                break_count += 1
                if break_count > 10:
                    break

            driver.execute_script("window.scrollTo(0, arguments[0]);", y)
            y += 200

            sleep(1)

            if webutils.DoesElementExistXPath(driver, self.CLOSE_LOG_TO_INSTAGRAM_XPATH):
                driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, self.CLOSE_LOG_TO_INSTAGRAM_XPATH))

        return images_info
