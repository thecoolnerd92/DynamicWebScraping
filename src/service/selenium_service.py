from src.repository.web_driver_interface import WebDriverInterface
from src.service.util_service import get_logger

from selenium.webdriver.chrome.options import Options
from undetected_chromedriver import Chrome, ChromeOptions
import tempfile
from fake_useragent import UserAgent

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

import json
logger = get_logger(__name__)

class SeleniumUndetectableDriverService(WebDriverInterface):
    def __init__(self, sleep, timeout=5, *args, **kwargs):
        logger.info(f"Initialized SeleniumUndetectableDriver")
        try:
            options = Options() # ChromeOptions() # webdriver.ChromeOptions()
            options.add_argument("--kiosk-printing")
            # options.add_argument("--kiosk")
            settings = {
                "recentDestinations": [{"id": "Save as PDF", "origin": "local"}],
                "selectedDestinationId": "Save as PDF",
                "version": 2,
            }
            prefs = {
                "printing.print_preview_sticky_settings.appState": json.dumps(settings),
                "plugins.always_open_pdf_externally": True,
                "download.prompt_for_download": False,
            }
            options.add_experimental_option("prefs", prefs)
            # Add more realistic, human-like arguments
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--window-size=1920,1080")
            # # options.add_argument("--window-size=1440,900")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument(f"user-agent={UserAgent().random}")
            #
            # temp_dir = '~/Chrome_dev_session' # tempfile.mkdtemp()
            temp_dir = tempfile.mkdtemp()
            options.add_argument(f"--user-data-dir={temp_dir}")
            driver = Chrome(options=options, use_subprocess=True)
            self.__sleep = sleep
            driver.implicitly_wait(timeout)
            driver.maximize_window()
            logger.info(f'Initialized Chrome driver')
            self.__driver = driver
            self.__actions = ActionChains(driver)
            self.__original_window = driver.current_window_handle

        except Exception as e:
            logger.error(f'An error occurred loading chrome driver: {e}')


    async def get(self, url):
        await self.__sleep(1)
        self.__driver.get(url)
        self.__original_window = self.__driver.current_window_handle
        return self.__driver

    def get_original_page(self):
        return self.__original_window

    async def find_elements(self, by=By.XPATH, value='', action={}, timeout=15, required=True, *args, **kwargs):
        wait = action.get('wait', .5)
        await self.__sleep(wait)
        try:
            WebDriverWait(self.__driver, action.get('wait', timeout)).until(
                EC.visibility_of_element_located((by, value))
            )
            await self.__sleep(wait)
            elements = self.__driver.find_elements(by=by, value=value)

            if not len(elements) and required:
                raise Exception(f"Element for {action['type']} action was not found")

            self.__driver.execute_script("arguments[0].scrollIntoView(true);", elements)
            return elements
        except Exception as e:
            logger.error(f"Error: The element was not visible & clickable within the given time. {e}")
            raise

    async def find_element(self, by=By.XPATH, value='', action={}, timeout=4, required=True, *args, **kwargs):
        wait = action.get('wait', .5)
        await self.__sleep(wait)
        try:
            WebDriverWait(self.__driver, action.get('wait', timeout)).until(
                EC.visibility_of_element_located((by, value))
            )
            await self.__sleep(wait)
            element = self.__driver.find_element(by=by, value=value)

            if element is None and required:
                raise Exception(f"Element was not found")

            self.__driver.execute_script("arguments[0].scrollIntoView(true);", element)
            return element
        except Exception as e:
            logger.error(f"Error: The element was not visible & clickable within the given time. {e}")
            if required:
                raise
            else:
                return None

    async def click_element(self, element=None, timeout=5, required=True, *args, **kwargs):
        """selenium has additional actions that need to be performed for bot detection"""

        try:
            WebDriverWait(self.__driver, timeout).until(
                EC.element_to_be_clickable(element)
            )
            await self.__sleep(.5)
            # return element.click()
            return self.__actions.move_to_element(element).click().perform()
        except Exception as e:
            logger.error(f'The button was not found', e)
            if required:
                raise
            else:
                return None

    async def type_input(self, action={}, element=None, *args, **kwargs):
        """
        Clear and type input into and input html element
        """
        wait = action.get('wait', 1)
        await self.__sleep(wait)
        await self.click_element(element, *args, **kwargs)
        await self.__sleep(wait)
        element.clear()
        await self.__sleep(wait)
        for char in str(action.get("value", "")):
            # simulate human behavior by typing one char at a time
            element.send_keys(char)
            await self.__sleep(wait / 5)
        logger.info("Text was input successfully.")

    async def dropdown_select(self, action={}, element=None, *args, **kwargs):
        """Select an option from a select droption element"""
        wait = action.get('wait', .5)
        try:
            await self.__sleep(wait)
            await self.click_element(element, *args, **kwargs)
            await self.__sleep(wait)
            select = Select(element)

            await self.__sleep(wait)
            select.select_by_visible_text(action.get("value", ""))
            await self.click_element(element, *args, **kwargs)

        except Exception as e:
            logger.error(f"Dropdown selection error. {e}")

    async def upload(self, value='', element=None, wait=1, *args, **kwargs):
        """Upload a document to the website"""
        try:
            await self.__sleep(wait)
            await element.send_keys(str(value))
        except Exception as e:
            logger.error(f'Error uploading file: {e}')

    async def switch_window(self, wait=2, *args, **kwargs):
        """Switch window for pop up opening"""
        await self.__sleep(wait)
        all_windows = self.__driver.window_handles

        # 5. Loop through handles to find the new one and switch
        for window in all_windows:
            if window != self.__original_window:
                self.__driver.switch_to.window(window)
                logger.info(f"Switched to new web page: {window}")
                break

    async def return_to_original_window(self, *args, **kwargs):
        """Return to original window when pop up window closes"""
        current_window = self.__driver.current_window_handle
        self.__driver.close()
        if current_window != self.__original_window:
            self.__driver.switch_to.window(self.__original_window).switch_to.window(self.__original_window)
            logger.info(f"Returned to original web page: {self.__original_window}")

    def close(self):
        """Close the browser"""
        self.__driver.quit()
        logger.info(f"Completed all actions. Closing driver.")