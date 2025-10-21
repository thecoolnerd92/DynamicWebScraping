import requests

from src.service.util_service import *
import datetime as dt

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

# 1. Get the absolute path of the file
full_file_path = os.path.abspath(__file__)
# 2. Get the directory path (the folder the file is in)
directory_path = os.path.dirname(full_file_path)

logger = get_logger()

class DynamicWebScraping:
    """
    Sample Web Scraping class
    """
    def __init__(self, config, driver_):
        self.__config = config
        self._logger = logger
        self.__debug_mode = config.get("debug", False)
        self.__driver: CustomDriver = driver_
        self.__actions = ActionChains(self.__driver)
        self.path_separator = self.__config.get('separator', '\\')
        self.download_directory = config.get('download_directory', f'.{self.path_separator}')

    async def get_driver(self, url):
        try:
            await self.__driver.get(url)

        except Exception as e:
            logger.error(f"Chrome Driver Initialization Error: {e}")
            raise

    async def run_actions(self, actions, timeout=30):
        """
        Run the actions that you want to be completed on some web page
        :param actions: the actions to be performed, dict
        :param timeout: default wait time to wait for elements to be found
        """
        index = 0
        for action in actions:
            if "wait" in action.keys(): # Sleep
                self._logger.debug(f'Sleeping for {action["wait"]} seconds')
                await sleep(action.get('wait', 5))

            self._logger.debug(f'Running {action["type"]} action')
            match action["type"]:
                case "click": # click an element
                    await self._run_click_visible_button(action, timeout, index)

                case "download": # download some doc
                    await self._run_download_document(action, timeout, index)

                case "external_click": # for pop up window
                    await self._run_popup_window(action)

                case "input": # type input fields
                    await self._run_type_input(action, timeout, index)

                case "select": # dropdown selection
                    await self._run_dropdown_selection(action, timeout, index)
                # add more custom cases....
            index += 1

        if self.__debug_mode:
            input('Press Enter to close the browser...')
            await sleep(2)
            self.__driver.close()

    async def _run_popup_window(self, action, timeout= 1, *args, **kwargs):
        """
        open a pop-up window and then return back to the original page
        not fully tested
        """
        curr_page = await self.__driver.switch_window()
        sub_actions = action.get('sub_actions', [])
        await self.run_actions(sub_actions)
        # resume = input('Click enter to return to original window')
        # while self.__driver.get_original_page() != curr_page:
        #     await sleep(timeout)

        await sleep(timeout)
        return self.__driver.return_to_original_window()

    async def _run_download_document(self, action, timeout, *args, **kwargs):
        """
        Download a document with an http get request
        """
        download_directory = f'{self.download_directory}{self.path_separator}{action.get("value")}'

        xpath = action["xpath"]
        element = await self.__driver.find_element(by=By.XPATH, value=xpath, action=action)
        # await self.__driver.click_element(element=element)
        file_url = element.get_attribute('href')
        filename = f"{download_directory}{self.path_separator}{os.path.basename(file_url)}_{dt.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
        try:
            session = requests.Session()
            with session.get(file_url, timeout=timeout, stream=True) as r:
                r.raise_for_status()
                self.__driver.get_cookies()

                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                self._logger.info(f'Download Complete')

        except Exception as e:
            self._logger.error(f"Error downloading file: {e}")

    async def _run_click_visible_button(self, action, *args, **kwargs):
        """
        Click a button or element
        """
        try:
            xpath = action["xpath"]
            btn = await self.__driver.find_element(by=By.XPATH, value=xpath, action=action)

            required = action.get('required', False)
            if required and not (btn and await btn.is_displayed()):
                raise Exception(f"The button was not found in the given wait time")

            self.__logged_in = False
            await self.__driver.click_element(element=btn, required=False)
            self._logger.info("Button was clicked successfully.")

        except Exception as e:
            # Handle the timeout error if the element is not found
            self._logger.error(f"Error: Button click error. {e}")

    async def _run_type_input(self, action, *args, **kwargs):
        """
        Type into an input field
        """
        try:
            xpath = action["xpath"]
            typeable_input = await self.__driver.find_element(by=By.XPATH, value=xpath, action=action)

            required = action.get('required', False)
            if required and not (typeable_input and await typeable_input.is_displayed()):
                raise Exception(f"The input element was not found in the given wait time")
            await self.__driver.type_input(action=action, element=typeable_input)

        except Exception as e:
            # Handle the timeout error if the element is not found
            self._logger.error(f"Error: Text input error. {e}")

    async def _run_dropdown_selection(self, action, *args, **kwargs):
        """
        select an option from a dropdown option select element
        """
        try:
            xpath = action["xpath"]
            wait = action.get('wait', 1)
            dropdown_el = await self.__driver.find_element(by=By.XPATH, value=xpath, action=action) # self.__get_element(xpath, action, index, timeout)
            await sleep(wait)
            required = action.get('required', False)
            if required and not (dropdown_el and await dropdown_el.is_displayed()):
                raise Exception(f"The dropdown was not found in the given wait time")
            await self.__driver.dropdown_select(action=action, element=dropdown_el)

        except Exception as e:
            self._logger.error(f"Dropdown selection error. {e}")

        ######################### Add more custom actions below #########################

async def main():
    driver = CustomDriver(timeout=10)
    web_scraper = DynamicWebScraping(config, driver)  # config is read in the settings.py file at the top level of the project
    # get driver
    await web_scraper.get_driver(config["url"])
    await web_scraper.run_actions(config['actions'])

if __name__ == "__main__":
    from settings import config
    import nodriver as uc
    uc.loop().run_until_complete(main())
