# facebook.py
# 11.04.2024

import utils.webutils as webutils
import utils.console as console

from selenium.webdriver.common.by import By
from time import sleep


class Facebook:
    SITE_LINK = "https://www.facebook.com/"
    SITE_LINK_ADD_PHOTOS_WITH = "/photos"
    SITE_LINK_ADD_PHOTOS_BY = "/photos_by"

    # Cookies block whole webpage
    DECLINE_COOKIES_CLASS = "_42ft._4jy0._al66._4jy3._4jy1.selected._51sy"

    # Appears every time you open profile on facebook
    CLOSE_LOG_TO_FACEBOOK_XPATH = "/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/div"

    # This image will be hold on seperate site, cause some people have a lot of photos and it's just faster to open them in new page
    BETTER_QUALITY_IMAGE_SITE_SRC_CLASS = "x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.x1heor9g.xt0b8zv.x1lliihq.x5yr21d.x1n2onr6.xh8yej3"
    BETTER_QUALITY_IMAGE_SRC_CLASS = "x85a59c.x193iq5w.x4fas0m.x19kjcj4"

    def __init__(self):
        console.Task("Initialising facebook")

    def Init(self, driver):
        driver.get(self.SITE_LINK)

        cookies_decline = webutils.LoopUntilElementFoundByClassName(driver, self.DECLINE_COOKIES_CLASS, 10)
        if cookies_decline is None:
            return False
        cookies_decline.click()

        sleep(4)

        console.SubTask("Successfully initialized facebook")
        return True

    def InitProfileImagesSearch(self, driver, profile_name, photos_with):
        if photos_with is True:
            driver.get(self.SITE_LINK + profile_name + self.SITE_LINK_ADD_PHOTOS_WITH)
        else:
            driver.get(self.SITE_LINK + profile_name + self.SITE_LINK_ADD_PHOTOS_BY)

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

        images_info = []

        loops = 0
        previous_highest_image = 0

        images_src_sites = []

        while loops < 100:
            current_highest_image = 0

            checks_for_loaded = 0
            # Loop to check if new images loaded
            while True:
                current_highest_image = len(driver.find_elements(By.CLASS_NAME, self.BETTER_QUALITY_IMAGE_SITE_SRC_CLASS))

                # This means, that all images were loaded
                if current_highest_image != previous_highest_image or checks_for_loaded >= 50:
                    break

                checks_for_loaded += 1
                sleep(0.1)

            # Just an extra time to wait, cause sometimes it takes time before new images load
            sleep(3)

            if current_highest_image == previous_highest_image:
                break

            previous = previous_highest_image
            images_preview_photos = driver.find_elements(By.CLASS_NAME, self.BETTER_QUALITY_IMAGE_SITE_SRC_CLASS)

            # Get links to sites with image with better quality
            while previous < current_highest_image:
                images_src_sites.append(images_preview_photos[previous].get_attribute("href"))
                previous += 1

            # Open sites with better quality images
            while previous_highest_image < current_highest_image:
                # Open new window
                driver.execute_script("window.open(" ");")
                sleep(0.05)

                # Switch to window and go to the link
                driver.switch_to.window(driver.window_handles[len(driver.window_handles) - 1])
                driver.get(images_src_sites[previous_highest_image])
                previous_highest_image += 1
                sleep(0.05)

            # Now get images urls
            while len(driver.window_handles) != 1:
                driver.switch_to.window(driver.window_handles[len(driver.window_handles) - 1])
                image_src = webutils.LoopUntilElementFoundByClassName(driver, self.BETTER_QUALITY_IMAGE_SRC_CLASS, 1)
                if image_src is not None:
                    images_info.append(driver.find_element(By.CLASS_NAME, self.BETTER_QUALITY_IMAGE_SRC_CLASS).get_attribute("src"))
                driver.close()
            driver.switch_to.window(driver.window_handles[0])

            # Scroll down so more images will get loaded
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            loops += 1

        return images_info
