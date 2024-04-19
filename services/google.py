# google.py
# 06.03.2024

import utils.webutils as webutils
import utils.console as console

from selenium.webdriver.common.by import By
from time import sleep, time


class Google:
    SITE_LINK = "https://images.google.com/"

    TEXT_SEARCH_WEB_PAGES_COUNT = 12

    # Cookies block any actions until we accept/decline them
    DECLINE_COOKIES_CLASS = "W0wltc"

    # Send text here and press button to start searching for it
    TEXT_INPUT_CLASS = "gLFyf"
    SEARCH_TEXT_BUTTON_CLASS = "Tg7LZd"

    # Thumbnail image container, you have to press button to get access to better quality image
    THUMBNAIL_IMAGE_SRC_CLASS = "YQ4gaf"
    THUMBNAIL_BUTTON_CLASS = "F0uyec"

    # Zoom in image info
    BETTER_QUALITY_IMAGE_SRC_CLASS = "sFlh5c.pT0Scc.iPVvYb"

    def __init__(self):
        console.Task("Initialising google")

    def Init(self, driver):
        driver.get(self.SITE_LINK)

        cookies_decline = webutils.LoopUntilElementFoundByID(driver, self.DECLINE_COOKIES_CLASS)
        if cookies_decline is None:
            return False
        driver.execute_script("arguments[0].click();", cookies_decline)

        console.SubTask("Successfully initialized google")
        return True

    def InitTextImageSearch(self, driver, image_text):
        driver.get(self.SITE_LINK)

        # driver = webutils.GetWebdriver()

        text_input = webutils.LoopUntilElementFoundByClassName(driver, self.TEXT_INPUT_CLASS)
        if text_input is None:
            return False
        sleep(0.25)
        text_input.send_keys(image_text)

        search_button = webutils.LoopUntilElementFoundByClassName(driver, self.SEARCH_TEXT_BUTTON_CLASS)
        if search_button is None:
            return False
        driver.execute_script("arguments[0].click();", search_button)

        # Wait to just fully load site, it's much faster than yandex
        sleep(2.5)

        return True

    def GetLayoutInfos(self, driver):
        webutils.ScrollDownPage(driver, 3, 2)
        sleep(2)

        elements_count = len(driver.find_elements(By.CLASS_NAME, self.THUMBNAIL_BUTTON_CLASS))

        current_url = driver.current_url

        layout_infos = [[0] * 4 for i in range(0, self.TEXT_SEARCH_WEB_PAGES_COUNT, 1)]
        layout_infos[0] = [0, int(elements_count / self.TEXT_SEARCH_WEB_PAGES_COUNT), False, 0]
        for i in range(1, self.TEXT_SEARCH_WEB_PAGES_COUNT, 1):
            driver.execute_script("window.open(" ");")
            driver.switch_to.window(driver.window_handles[i])
            driver.get(current_url)
            check = 0
            while len(driver.find_elements(By.CLASS_NAME, self.THUMBNAIL_BUTTON_CLASS)) < elements_count:
                sleep(1)
                if check > 6:
                    elements_count = len(driver.find_elements(By.CLASS_NAME, self.THUMBNAIL_BUTTON_CLASS))
                    break
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                check += 1
            sleep(1)
            layout_infos[i] = [0, int(elements_count / self.TEXT_SEARCH_WEB_PAGES_COUNT), False, 0]

        return layout_infos

    def SetLayoutInfo(self, current_image, max_image, clicked_image, fail_safe_timer):
        return [current_image, max_image, clicked_image, fail_safe_timer]

    def TextImagesSearch(self, driver, image_text):
        images_info = []

        if not self.InitTextImageSearch(driver, image_text):
            console.SubError("Failed to init reverse image search at yandex")
            return images_info

        # array of (current_image, max_image, clicked_image, fail_safe_timer)
        layout_infos = self.GetLayoutInfos(driver)

        while True:
            should_break = True
            for i in range(0, len(layout_infos), 1):
                if layout_infos[i][0] < layout_infos[i][1]:
                    current_time = time()
                    should_break = False
                    driver.switch_to.window(driver.window_handles[i])
                    if layout_infos[i][2] == False:
                        driver.execute_script("arguments[0].click();", driver.find_elements(By.CLASS_NAME, self.THUMBNAIL_BUTTON_CLASS)[layout_infos[i][0] * self.TEXT_SEARCH_WEB_PAGES_COUNT + i])
                        layout_infos[i][2] = True
                    else:
                        if layout_infos[i][3] > 1:
                            layout_infos[i] = self.SetLayoutInfo(layout_infos[i][0] + 1, layout_infos[i][1], False, 0)
                            continue
                        elif webutils.DoesElementExistClassName(driver, self.BETTER_QUALITY_IMAGE_SRC_CLASS):
                            images_info.append(driver.find_element(By.CLASS_NAME, self.BETTER_QUALITY_IMAGE_SRC_CLASS).get_attribute("src"))
                            layout_infos[i] = self.SetLayoutInfo(layout_infos[i][0] + 1, layout_infos[i][1], False, 0)
                            continue
                        layout_infos[i][3] += time() - current_time

            if should_break:
                break

        webutils.WebDriverCloseAllExtraTabs(driver)

        return images_info
