import asyncio

import pytest
from unittest.mock import patch, Mock, AsyncMock, MagicMock

from custom_fixtures import mock_element
from src.service.selenium_service import *
from tests.custom_fixtures import xpaths, selectors

@pytest.fixture(scope='module')
def mock_actions():
    with patch('src.service.selenium_service.ActionChains') as actions_mock:
        actions_mock.return_value.move_to_element.return_value.click.return_value.perform = Mock()
        yield actions_mock

@pytest.fixture(scope='function')
def mock_ec():
    with patch('src.service.selenium_service.EC') as ec_mock:
        ec_mock.return_value.visibility_of_element_located = Mock()
        ec_mock.return_value.element_to_be_clickable = Mock()
        yield ec_mock

@pytest.fixture(scope='function')
def mock_web_driver_wait():
    with patch('src.service.selenium_service.WebDriverWait') as wd_mock:
        wd_mock.return_value.until = Mock()

        yield wd_mock

@pytest.fixture(scope="function")
def mock_driver(mock_element):
    with patch('src.service.selenium_service.Chrome') as driver_mock:
        driver_mock.return_value = MagicMock()
        driver_mock.return_value.get = MagicMock()
        driver_mock.return_value.find_elements = MagicMock()
        driver_mock.return_value.find_element = MagicMock()
        driver_mock.return_value.execute_script = MagicMock()
        driver_mock.return_value.switch_to.window = MagicMock()
        driver_mock.return_value.close = MagicMock()
        driver_mock.return_value.quit = MagicMock()
        yield driver_mock

class TestSeleniumUdDriverService:
    @pytest.mark.asyncio
    async def test_driver_init_error(self,  mock_driver):
        mock_driver.return_value.current_window_handle = 'original'

        mock_sleep = AsyncMock()
        mock_driver.side_effect = Exception('Selenium Driver initialization error')
        with pytest.raises(Exception) as e:
            SeleniumUndetectableDriverService(mock_sleep, 1)
            assert e.value == 'Selenium Driver initialization error'

    @pytest.mark.asyncio
    async def test_get(self,  mock_driver):
        mock_driver.return_value.current_window_handle = 'original'

        mock_sleep = AsyncMock()
        driver = SeleniumUndetectableDriverService(mock_sleep, 1)
        await driver.get('https://example.com')
        mock_driver.return_value.get.assert_called_once_with('https://example.com')
        # assert mock_driver.return_value.get.is_called_with('https://example.com')

    @pytest.mark.asyncio
    async def test_find_elements_success(self, mock_driver, mock_element, mock_ec, mock_web_driver_wait):
        mock_web_driver_wait.return_value.until.return_value = True
        action = {'wait': 1, 'xpath': xpaths['uname_input'], 'type': 'click'}
        mock_driver.return_value.find_elements.return_value = [mock_element]


        mock_sleep = AsyncMock()
        driver = SeleniumUndetectableDriverService(mock_sleep, 1)
        res = await driver.find_elements(by=By.XPATH, value=action['xpath'])

        assert res == [mock_element]
        assert mock_driver.return_value.find_elements.is_called_with(by=By.XPATH, value=action['xpath'])
        mock_web_driver_wait.return_value.until.assert_called_once()
        mock_ec.visibility_of_element_located.assert_called_once_with((By.XPATH, action['xpath']))
        mock_driver.return_value.execute_script.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_elements_exception(self, mock_driver, mock_element, mock_ec, mock_web_driver_wait):
        mock_web_driver_wait.return_value.until.return_value = True
        action = {'wait': 1, 'xpath': xpaths['uname_input'], 'type': 'click'}
        mock_driver.return_value.find_elements.return_value = []

        mock_sleep = AsyncMock()
        with pytest.raises(Exception) as e:
            driver = SeleniumUndetectableDriverService(mock_sleep, 1)
            await driver.find_elements(by=By.XPATH, value=action['xpath'])

            assert e.value == f"Element for {action['type']} action was not found"

    @pytest.mark.asyncio
    async def test_find_element_success(self, mock_driver, mock_element, mock_ec, mock_web_driver_wait):
        mock_web_driver_wait.return_value.until.return_value = True
        action = {'wait': 1, 'xpath': xpaths['uname_input'], 'type': 'click'}
        mock_driver.return_value.find_element.return_value = mock_element


        mock_sleep = AsyncMock()
        driver = SeleniumUndetectableDriverService(mock_sleep, 1)
        res = await driver.find_element(by=By.XPATH, value=action['xpath'])

        assert res == mock_element
        mock_driver.return_value.find_element.assert_called_once_with(by=By.XPATH, value=action['xpath'])
        mock_web_driver_wait.return_value.until.assert_called_once()
        mock_ec.visibility_of_element_located.assert_called_once_with((By.XPATH, action['xpath']))
        assert mock_driver.return_value.execute_script.is_called_once()

    @pytest.mark.asyncio
    async def test_find_element_exception(self, mock_driver, mock_element, mock_ec, mock_web_driver_wait):
        mock_driver.return_value.until.return_value = True
        action = {'wait': 1, 'xpath': xpaths['uname_input'], 'type': 'click'}
        mock_driver.return_value.find_element.return_value = None

        mock_sleep = AsyncMock()
        with pytest.raises(Exception) as e:
            driver = SeleniumUndetectableDriverService(mock_sleep, 1)
            await driver.find_element(by=By.XPATH, value=action['xpath'])

            assert e.value == f"Element was not found"

    @pytest.mark.asyncio
    async def test_click_element_success(self, mock_driver, mock_element, mock_ec, mock_web_driver_wait,
                                         mock_actions):
        mock_web_driver_wait.return_value.until.return_value = True


        mock_sleep = AsyncMock()
        driver = SeleniumUndetectableDriverService(mock_sleep, 1)
        await driver.click_element(element=mock_element)

        mock_sleep.assert_called_once()
        mock_web_driver_wait.return_value.until.assert_called_once()
        mock_ec.element_to_be_clickable.assert_called_once_with(mock_element)
        mock_actions.return_value.move_to_element.assert_called_once_with(mock_element)
        mock_actions.return_value.move_to_element.return_value.click.return_value.perform.assert_called_once()

    @pytest.mark.asyncio
    async def test_click_element_exception(self, mock_driver, mock_element, mock_ec, mock_web_driver_wait,
                                         mock_actions):
        mock_driver.return_value.until.return_value = True

        mock_sleep = AsyncMock()
        driver = SeleniumUndetectableDriverService(mock_sleep, 1)
        await driver.click_element(element=mock_element)

        mock_actions.return_value.move_to_element.side_effect = Exception('Button not found or clickable')
        with pytest.raises(Exception) as e:
            driver = SeleniumUndetectableDriverService(mock_sleep, 1)
            await driver.click_element(element=mock_element)

            assert e.value == f"Button not found or clickable"

    @pytest.mark.asyncio
    @patch('src.service.selenium_service.SeleniumUndetectableDriverService.click_element')
    async def test_type_input_success(self, mock_click, mock_driver, mock_element):
        mock_element.clear = Mock()
        mock_element.send_keys = Mock()
        action = {'wait': 1, 'value': 'uname', 'type': 'input'}

        mock_sleep = AsyncMock()
        driver = SeleniumUndetectableDriverService(mock_sleep, 1)
        await driver.type_input(element=mock_element, action=action)

        assert mock_sleep.call_count == 3 + len(action['value'])
        assert mock_element.send_keys.call_count == len(action['value'])
        mock_click.assert_called_once()

    @pytest.mark.asyncio
    @patch('src.service.selenium_service.SeleniumUndetectableDriverService.click_element')
    @patch('src.service.selenium_service.Select')
    async def test_dropdown_select_success(self, mock_select, mock_click, mock_driver, mock_element):
        mock_sleep = AsyncMock()
        mock_select.select_by_visible_text = Mock()
        action = {'wait': 1, 'value': 'uname', 'type': 'input'}

        driver = SeleniumUndetectableDriverService(mock_sleep, 1)
        await driver.dropdown_select(element=mock_element, action=action)

        assert mock_sleep.call_count == 3
        mock_select.return_value.select_by_visible_text.assert_called_once_with(action['value'])
        mock_click.assert_called_with(mock_element)
        assert mock_click.call_count == 2

    @pytest.mark.asyncio
    @patch('src.service.selenium_service.SeleniumUndetectableDriverService.click_element')
    @patch('src.service.selenium_service.Select')
    async def test_dropdown_select_exception(self, mock_select, mock_click, mock_driver, mock_element,
                                         mock_actions):
        mock_sleep = AsyncMock()
        mock_select.select_by_visible_text = Mock()
        action = {'wait': 1, 'value': 'uname', 'type': 'input'}

        mock_select.return_value.select_by_visible_text.side_effect = Exception('Dropdown Select Error')
        with pytest.raises(Exception) as e:
            driver = SeleniumUndetectableDriverService(mock_sleep, 1)
            await driver.dropdown_select(element=mock_element, action=action)
            assert e.value == 'Dropdown Select Error'

    @pytest.mark.asyncio
    async def test_file_upload_success(self, mock_driver, mock_element, mock_actions):
        value = 'path/to/some/file.txt'

        mock_sleep = AsyncMock()

        driver = SeleniumUndetectableDriverService(mock_sleep, 1)
        await driver.file_upload(value=value, element=mock_element)

        mock_sleep.assert_called_once_with(1)
        assert mock_element.send_keys.is_called_once_with(value)

    @pytest.mark.asyncio
    async def test_file_upload_exception(self, mock_driver, mock_element,  mock_actions):
        value = 'path/to/some/file.txt'

        mock_sleep = AsyncMock()
        mock_element.send_keys.side_effect = Exception('File Upload Error')
        with pytest.raises(Exception) as e:
            driver = SeleniumUndetectableDriverService(mock_sleep, 1)
            await driver.file_upload(value=value, element=mock_element)
            assert e.value == 'File Upload Error'

    @pytest.mark.asyncio
    async def test_switch_window(self, mock_driver, mock_element):

        mock_sleep = AsyncMock()
        original_window = 'https://www.google.com'
        new_window = 'example.com'
        mock_driver.return_value.window_handles = [original_window, new_window]

        driver = SeleniumUndetectableDriverService(mock_sleep, 1)
        await driver.open_new_window()

        mock_driver.return_value.switch_to.window.assert_called_once_with(new_window)

    @pytest.mark.asyncio
    async def test_return_to_original_window(self, mock_driver, mock_element):

        mock_sleep = AsyncMock()
        original_window = 'https://www.google.com'
        new_window = 'example.com'
        mock_driver.return_value.window_handles = [original_window, new_window]
        mock_driver.return_value.current_window_handle = 'https://www.google.com'

        driver = SeleniumUndetectableDriverService(mock_sleep, 1)
        mock_driver.return_value.current_window_handle = 'example.com'
        await driver.return_to_original_window()

        mock_driver.return_value.switch_to.window.assert_called_once_with(original_window)
        mock_driver.return_value.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close(self, mock_driver):

        mock_sleep = AsyncMock()

        driver = SeleniumUndetectableDriverService(mock_sleep, 1)
        driver.close()

        mock_driver.return_value.quit.assert_called_once()