# yandex.py
# 04.03.2024

import utils.webutils as webutils
import utils.console as console

from selenium.webdriver.common.by import By
from time import sleep, time


class Yandex:
    SITE_LINK = "https://yandex.com/images/?rpt=imageview"

    # Cookies sometimes block similar images clicking
    DECLINE_COOKIES_CLASS = "gdpr-popup-v3-button.gdpr-popup-v3-button_id_mandatory"

    # Send here your photo path and it will be send to reverse search it
    PHOTO_INPUT_CLASS = "CbirCore-FileInput"
    # Click button to show us similar images to send photo
    SIMILAR_IMAGES_BUTTON = "Button2.Button2_width_max.Button2_view_default.Button2_size_l.Button2_link.CbirSimilar-MoreButton"

    # Layouts to search
    COLUMN_LAYOUT_CLASS = "justifier__col"
    ROW_LAYOUT_CLASS = "JustifierRowLayout"

    # Thumbnail image container, you have to press button to get access to better quality image
    THUMBNAIL_IMAGE_SRC_CLASS = "serp-item__thumb.justifier__thumb"
    THUMBNAIL_BUTTON_CLASS = "serp-item__thumb.justifier__thumb"

    # Zoom in image info, error message means, that full quality image can't be downloded
    BETTER_QUALITY_IMAGE_ERROR_CLASS = "ImagesViewer-ErrorMessage"
    CLOSE_BETTER_QUALITY_IMAGE_CLASS = "ImagesViewer-Close"
    BETTER_QUALITY_IMAGE_SRC_CLASS = "MMImage-Origin"

    def __init__(self):
        console.Task("Initialising yandex")

    def Init(self, driver):
        driver.get(self.SITE_LINK)

        cookies_decline = webutils.LoopUntilElementFoundByClassName(driver, self.DECLINE_COOKIES_CLASS)
        if cookies_decline is None:
            return False
        cookies_decline.click()

        console.SubTask("Successfully initialized yandex")
        return True

    def InitReverseImageSearch(self, driver, photo_path):
        driver.get(self.SITE_LINK)

        photo_input = webutils.LoopUntilElementFoundByClassName(driver, self.PHOTO_INPUT_CLASS)
        if photo_input is None:
            return False
        # Sometimes doesn't work when we don't wait
        sleep(0.25)
        photo_input.send_keys(photo_path)

        # This element is somewhat buggy
        similar_images = webutils.LoopUntilElementFoundByClassName(driver, self.SIMILAR_IMAGES_BUTTON, 15)
        if similar_images is None:
            photo_input.send_keys(photo_path)
            similar_images = webutils.LoopUntilElementFoundByClassName(driver, self.SIMILAR_IMAGES_BUTTON, 15)
            if similar_images is None:
                return False
        driver.execute_script("arguments[0].click();", similar_images)

        if not webutils.LoopUntilElementNotFoundByClassName(driver, self.SIMILAR_IMAGES_BUTTON, 15):
            return False

        # Wait to fully load site
        sleep(2)

        return True

    def IsLayoutColumn(self, driver):
        return len(driver.find_elements(By.CLASS_NAME, self.COLUMN_LAYOUT_CLASS)) != 0

    def GetLayoutObjects(self, driver, is_layout_column):
        if is_layout_column:
            return driver.find_elements(By.CLASS_NAME, self.COLUMN_LAYOUT_CLASS)
        else:
            return driver.find_elements(By.CLASS_NAME, self.ROW_LAYOUT_CLASS)

    def SetLayoutInfo(self, current_image, max_image, clicked_image, fail_safe_timer):
        return [current_image, max_image, clicked_image, fail_safe_timer]

    def GetLayoutInfos(self, driver):
        webutils.ScrollDownPage(driver, 6, 1.5)
        sleep(3)

        is_layout_column = self.IsLayoutColumn(driver)
        layout_count = len(self.GetLayoutObjects(driver, is_layout_column))

        elements_count = len(driver.find_elements(By.CLASS_NAME, self.THUMBNAIL_BUTTON_CLASS))

        current_url = driver.current_url

        layout_infos = [[0] * 4 for i in range(0, layout_count, 1)]
        layout_infos[0] = [0, len(self.GetLayoutObjects(driver, is_layout_column)[0].find_elements(By.CLASS_NAME, self.THUMBNAIL_BUTTON_CLASS)), False, 0]
        for i in range(1, layout_count, 1):
            driver.execute_script("window.open(" ");")
            driver.switch_to.window(driver.window_handles[i])
            driver.get(current_url)
            # In older version of yandex image search there was bug(?) where layout object switch between searches
            if i == 1 and is_layout_column != self.IsLayoutColumn(driver):
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                sleep(1)
                return self.GetLayoutInfos(driver)
            while len(self.GetLayoutObjects(driver, is_layout_column)) <= i:
                sleep(0.01)
            check = 0
            while len(driver.find_elements(By.CLASS_NAME, self.THUMBNAIL_BUTTON_CLASS)) < elements_count:
                sleep(1)
                if check > 10:
                    elements_count = len(driver.find_elements(By.CLASS_NAME, self.THUMBNAIL_BUTTON_CLASS))
                    break
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                check += 1
            sleep(1)
            layout_infos[i] = [0, len(self.GetLayoutObjects(driver, is_layout_column)[i].find_elements(By.CLASS_NAME, self.THUMBNAIL_BUTTON_CLASS)), False, 0]

        return layout_infos

    def ReverseImagesSearch(self, driver, photo_path):
        if not self.InitReverseImageSearch(driver, photo_path):
            console.SubError("Failed to init reverse image search at yandex")
            raise Exception()

        images_info = []

        # array of (current_image, max_image, clicked_image, fail_safe_timer)
        layout_infos = self.GetLayoutInfos(driver)
        is_layout_column = self.IsLayoutColumn(driver)

        while True:
            should_break = True
            for i in range(0, len(layout_infos), 1):
                if layout_infos[i][0] < layout_infos[i][1]:
                    current_time = time()
                    should_break = False
                    driver.switch_to.window(driver.window_handles[i])
                    if layout_infos[i][2] == False:
                        driver.execute_script("arguments[0].click();", self.GetLayoutObjects(driver, is_layout_column)[i].find_elements(By.CLASS_NAME, self.THUMBNAIL_BUTTON_CLASS)[layout_infos[i][0]])
                        layout_infos[i][2] = True
                    else:
                        if layout_infos[i][3] > 1:
                            layout_infos[i] = self.SetLayoutInfo(layout_infos[i][0] + 1, layout_infos[i][1], False, 0)
                            driver.execute_script("arguments[0].click();", driver.find_element(By.CLASS_NAME, self.CLOSE_BETTER_QUALITY_IMAGE_CLASS))
                            continue
                        elif webutils.DoesElementExistClassName(driver, self.BETTER_QUALITY_IMAGE_SRC_CLASS):
                            if driver.find_element(By.CLASS_NAME, self.BETTER_QUALITY_IMAGE_SRC_CLASS).get_attribute("src") != self.GetLayoutObjects(driver, is_layout_column)[i].find_elements(By.CLASS_NAME, self.THUMBNAIL_IMAGE_SRC_CLASS)[layout_infos[i][0]].get_attribute("src"):
                                images_info.append(driver.find_element(By.CLASS_NAME, self.BETTER_QUALITY_IMAGE_SRC_CLASS).get_attribute("src"))
                                layout_infos[i] = self.SetLayoutInfo(layout_infos[i][0] + 1, layout_infos[i][1], False, 0)
                                driver.execute_script("arguments[0].click();", driver.find_element(By.CLASS_NAME, self.CLOSE_BETTER_QUALITY_IMAGE_CLASS))
                                continue
                            elif webutils.DoesElementExistClassName(driver, self.BETTER_QUALITY_IMAGE_ERROR_CLASS):
                                # images_info.append(driver.find_element(By.CLASS_NAME, self.BETTER_QUALITY_IMAGE_SRC_CLASS).get_attribute("src"))
                                layout_infos[i] = self.SetLayoutInfo(layout_infos[i][0] + 1, layout_infos[i][1], False, 0)
                                driver.execute_script("arguments[0].click();", driver.find_element(By.CLASS_NAME, self.CLOSE_BETTER_QUALITY_IMAGE_CLASS))
                                continue
                        layout_infos[i][3] += time() - current_time

            if should_break:
                break

        webutils.WebDriverCloseAllExtraTabs(driver)

        return images_info
