
import logging

from selenium.common import NoSuchAttributeException

from src.repository.web_driver_interface import WebDriverInterface

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S %Z')
logger = logging.getLogger(__name__)

import tempfile
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
import nodriver as uc
from nodriver.core.element import Element as NodriverElement
from nodriver.core.tab import Tab as NodriverPage

# def uc_runner(func):
#     print('uc runner')
#     uc.loop().run_until_complete(func())
# import asyncio

# @add_sync_wrappers
class NoDriverService(WebDriverInterface):
    def __init__(self, sleep, implicit_wait=5, *args, **kwargs):
        logger.info(f"Initialized NoDriverClass")
        user_agent = UserAgent().random
        # self.browser_endpoint = "http://localhost:9222"
        self.__temp_dir = tempfile.mkdtemp()

        self.browser_args = [
            f"user-agent={user_agent}",
            # f"headless={False}"
            # "--window-size=1920,1080",
            "--start-maximized",
            # "--no-sandbox",
            # f"--user-data-dir={temp_dir}"
            # f"--user-data-dir={PROJECT_ROOT}/my_browser_profile"
        ]
        self.__driver = None
        self.__page = None
        self.__original_tab = None
        self.__initial_tab_count = 0
        self.__wait = implicit_wait
        self.__sleep = sleep

    async def get(self, url):
        """
        Get the web page
        :param url: the url to connect to, str
        :return self.__page: the current web page the driver got
        """
        self.__driver = await uc.start(
            user_data_dir='~/Chrome_dev_session',
            headless=False,
            #user_data_dir=str(self.__temp_dir),
            browser_args=self.browser_args
        )
        await self.__sleep(1)
        self.__page = await self.__driver.get(url)

        # initialize these variables for the first page connected
        self.__initial_tab_count = len(self.__driver.tabs) if not self.__initial_tab_count else self.__initial_tab_count
        self.__original_tab = self.__page if not self.__original_tab else self.__original_tab
        return self.__page

    def get_original_page(self):
        """return the private original tab value"""
        return self.__original_tab

    def get_page(self):
        """return the current private page variable"""
        return self.__page

    async def find_elements(self, value='', by=By.XPATH, action={}, required=True, *args, **kwargs):
        """
        Find elements matching the value selector
        :param value: html selector/ xpath, vtr
        :param by: type of selector, str
        :param required: whether the element is required to be in the document, boolean
        :return elements: array of found elements, list
        """
        try:
            elements = await self.__page.xpath(value, timeout=action.get('wait', 1))
            await self.__scroll_into_view(value)
            if not len(elements) and required:
                raise Exception(f"Element for {action['type']} action was not found")

            return [CustomWebElement(element, self.__page, xpath=value, selector='') for element in elements]

        except Exception as e:
            logger.error(f"Error: The element was not visible & clickable within the given time. {e}")
            raise

    async def find_element(self, by=By.XPATH, value='', action={}, required=True, timeout=3, *args, **kwargs):
        """
        Find the first element matching the value selector
        :return element: first found html element, nodriver.core.element.Element
        """

        xpath = value if (by == By.XPATH) else ''
        selector = value if (by != By.XPATH) else ''
        wait = action.get('wait', timeout)
        try:
            my_element = await self.__page.find(value, timeout=wait)
            await self.__scroll_into_view(value)
            if my_element is None and required:
                raise Exception(f"Element was not found")

            if my_element:
                return CustomWebElement(my_element, self.__page, xpath=xpath, selector=selector)
            return my_element

        except Exception as e:
            # Handle the timeout error if the element is not found
            logger.error(f"Error: The element was not visible & clickable within the given time. {e}")
            if required:
                raise
            else:
                return None

    async def click_element(self, element=None, required=False, *args, **kwargs):
        """selenium has additional actions that need to be performed for bot detection"""
        await self.__sleep(.5)
        return await element.click()

    async def type_input(self, action={}, element=None, *args, **kwargs):
        """
        Clear and type input into and input html element
        """
        # await element.click()
        value = element.attrs.get('value')
        wait = action.get('wait', .5)
        await self.__sleep(wait)
        await self.click_element(element, *args, **kwargs)
        # print(f"Value before clearing: '{value} - {e_val}'") # Prints ''
        await self.__sleep(wait)
        if value:
            await element.clear_input() # important, clear_input() and not .clear()
            # curr_value = await element.get_value()
            # print(curr_value)

        # simulate human behavior by typing one char at a time
        for char in str(action.get("value", "")):
            await element.send_keys(char)
            await self.__sleep(wait / 5)

        logger.info("Text was input successfully.")

    async def dropdown_select(self, by='xpath', action={}, element=None, *args, **kwargs):
        """Select an option from a select droption element"""
        wait = action.get('wait', .5)

        dropdown_xpath = action["xpath"].replace('"', "'")
        option_text = action.get("value", "")
        target_option_xpath = f"{dropdown_xpath}//option[text()='{option_text}']"
        try:
            # await element.focus()
            # await self.__sleep(.5)
            await self.click_element(element)
            await self.__sleep(wait)

            selection_script = f"""
                const dropdownEl = document.evaluate("{dropdown_xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                // document.evaluate(".//option[text()='{option_text}']", dropdownEl, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                const optionEl = document.querySelector("{option_text} 

                if (dropdownEl && optionEl) {{
                    // Step A: Directly set the state
                    optionEl.selected = true;
                    dropdownEl.value = optionEl.value;

                    // Step B: Dispatch all relevant events
                    dropdownEl.dispatchEvent(new Event('input', {{ 'bubbles': true }}));
                    dropdownEl.dispatchEvent(new Event('change', {{ 'bubbles': true }}));

                    // Step C: Execute a native JavaScript click on the OPTION.
                    // This is the final trigger that often works when nothing else does.
                    optionEl.click();
                }} else {{
                    throw new Error("Could not find dropdown or option to execute script.");
                }}
            """
            ##########
            logger.info(f"Waiting for option '{option_text}' to be ready...")
            option = await self.__page.find(target_option_xpath, timeout=5)
            target_value = option.attrs.get('value')
            # print('target', option_text, target_value)
            await self.__page.evaluate(selection_script)
            # await self.click_element(element)
            await self.__sleep(wait)
            logger.info(f"Successfully selected '{option_text}'.")

            async def check_value(expected, dropdown_xpath):
                """confirm the option was selected"""
                get_value_script = f'document.evaluate("{dropdown_xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.value;'
                actual = await self.__page.evaluate(get_value_script)
                return actual == expected

            # if click does not work
            if not await check_value(option_text, dropdown_xpath):
                """backup select action of it was not selected with page.evaluate"""
                await element.send_keys(option_text)
                if not await check_value(target_value, dropdown_xpath):
                    raise Exception('Dropdown option could not be selected')

            logger.info(f"Successfully selected '{option_text}'.")
            return  # await self.__wait(1)

        except Exception as e:
            logger.error(f"Dropdown selection error for {option_text} option. {e}")

    async def upload(self, value='', element=None, wait=1,  *args, **kwargs):
        """
        Upload a document to the website
        <input type="file">
        """
        try:
            await self.__sleep(wait)
            await element.send_keys(str(value))
        except Exception as e:
            logger.error(f'Error uploading file: {e}')

    async def __scroll_into_view(self, xpath):
        """Scroll to an element on the web page"""
        scroll_script = f"""
            const element = document.evaluate("{xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if (element) {{
                element.scrollIntoView(true);
            }}
        """
        # Execute the script
        return await self.__page.evaluate(scroll_script)

    async def switch_window(self, tab_url='', wait=2, *args, **kwargs):
        """Switch window for new pop up opening"""
        await self.__sleep(wait)
        # tabs = self.__driver.tabs
        targets = await self.__driver.get_targets()
        # print('len', len(tabs), self.__initial_tab_count)
        # print(tabs)
        for target in targets:
            if tab_url in target.url:
                #print('target url', target, target.url)
                # new_tab = tabs[-1]
                await target.bring_to_front()
                # self.__page = await tab_url # .get_page()
                self.__page = target
                logger.info(f"Switched to new web page: {self.__page.text}")
                return self.__page

        logger.info(f"Page not found")
        return self.__page

    async def return_to_original_window(self, *args, **kwargs):
        """Return to original window when pop up window closes"""
        await self.__page.close()
        await self.__original_tab.bring_to_front()
        self.__page = self.__original_tab
        logger.info(f"Returned to original web page: {self.__page.text}")
        return

    async def close(self):
        """Close the browser"""
        self.__driver.stop()
        await self.__driver.close()
        logger.info(f"Completed all actions. Closing driver.")

# @add_sync_wrappers
class CustomWebElement:
    """
    A custom wrapper class that holds a nodriver element.
    """
    def __init__(self, element: NodriverElement, page: NodriverPage, xpath='', selector=''):
        self._element = element
        self._xpath = xpath.replace('"', "'")
        self._selector = selector
        self._page = page

    def __getattr__(self, name):
        """
        forward methods not found on no driver element to my custom getattr
        :param name: attribute name
        :return: getattr methods
        """
        return getattr(self._element, name)

    def get_attribute(self, name):
        """Mimicking selenium get_attribute"""
        return self._element.attrs.get(name)

    async def is_displayed(self):
        """custom is_displayed method to mimick selenium"""
        visibility_script = None
        if self._xpath:
            visibility_script = f"""
                {{const el =
                    document.evaluate("{self._xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    if (!el) {{
                        false; // Return false if element not found
                    }} else {{
                        const style = window.getComputedStyle(el);
                        const isHidden = style.display === 'none' || style.visibility === 'hidden';
                        const hasSize = el.offsetWidth > 0 && el.offsetHeight > 0;
                        !isHidden && hasSize; // Return true only if not hidden AND has size
                    }}
                }}
            """
        elif self._selector:
            visibility_script = f"""
                {{const el =
                    document.querySelector("{self._selector}");
                    if (!el) {{
                        false; // Return false if element not found
                    }} else {{
                        const style = window.getComputedStyle(el);
                        const isHidden = style.display === 'none' || style.visibility === 'hidden';
                        const hasSize = el.offsetWidth > 0 && el.offsetHeight > 0;
                        !isHidden && hasSize; // Return true only if not hidden AND has size
                    }}
                }}
            """
        if visibility_script is None:
            raise NoSuchAttributeException("No selector or xpath found")

        return await self._page.evaluate(visibility_script)

    async def get_value(self):
        """Check the current value of an element"""
        if self._xpath:
            get_value_script = f'document.evaluate("{self.xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.value;'
            return await self._page.evaluate(get_value_script)
        if self._selector:
            get_value_script = f"""document.querySelector('{self._selector}').value"""
            return await self._page.evaluate(get_value_script)

        return None

    def is_enabled(self):
        """mimicking selenium is_inabled attribute"""
        return 'disabled' not in self._element.attrs

    @staticmethod
    def get_cookies():
        """Have to look more into this for nodriver"""
        return
