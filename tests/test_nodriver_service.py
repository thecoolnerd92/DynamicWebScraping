import asyncio

import pytest
from unittest.mock import patch, Mock, AsyncMock

from custom_fixtures import mock_element, mock_uc_start
from src.service.nodriver_service import NoDriverService
from tests.custom_fixtures import xpaths, selectors

@pytest.fixture(scope='session')
def mock_sleep():
    with patch('src.service.nodriver_service') as sleep_mock:
        sleep_mock = AsyncMock()
        yield sleep_mock

class TestNoDriverService:
    @pytest.mark.asyncio
    async def test_nodriver_service_get(self, mock_uc_start, mock_sleep):
        """driver initialization"""
        url = 'https://www.google.com'
        driver = NoDriverService(mock_sleep)
        await driver.get(url)

        assert mock_uc_start.is_called_once()
        assert mock_uc_start.return_value.get.is_called_once_with(url)
        assert mock_sleep.is_called()

    @pytest.mark.asyncio
    async def test_nodriver_service_get_original_page(self, mock_uc_start, mock_sleep):
        """test getting the original page/ tab/ window"""
        url = 'https://www.google.com'
        driver = NoDriverService(mock_sleep)
        await driver.get(url)
        res = driver.get_original_page()

        assert res == mock_uc_start.return_value.get.return_value
        assert mock_sleep.is_called()

    @pytest.mark.asyncio
    async def test_nodriver_service_get_page(self, mock_uc_start, mock_sleep):
        """test getting the current page/ tab/ window"""
        url = 'https://www.google.com'
        driver = NoDriverService(mock_sleep)
        await driver.get(url)
        res = driver.get_original_page()

        assert res == mock_uc_start.return_value.get.return_value
        assert mock_sleep.is_called()

    @pytest.mark.asyncio
    async def test_find_elements(self, mock_uc_start, mock_sleep, mock_element):
        value = xpaths['email_input']
        elements = [mock_element]

        url = 'https://www.google.com'
        driver = NoDriverService(mock_sleep)
        page = await driver.get(url)
        page.xpath.return_value = elements
        # page.evaluate = AsyncMock()

        res = await driver.find_elements(value=value)
        assert page.xpath.is_called_with(value, 1)
        assert hasattr(res[0], 'is_displayed')
        assert mock_sleep.is_called()
        assert page.evaluate.call_count == len(elements)

    @pytest.mark.asyncio
    async def test_find_elements_exception_caught(self, mock_uc_start, mock_sleep):
        value = selectors['uname_input']
        action = {'type': 'click', 'selector': selectors['uname_input']}

        url = 'https://www.google.com'
        driver = NoDriverService(mock_sleep)
        page = await driver.get(url)
        page.xpath.return_value = []

        with pytest.raises(Exception) as e:
            await driver.find_elements(value=value, action=action, by='classname')
            assert page.xpath.is_called_with(value, 1, )
            assert e.value == f"Element for {action['type']} action was not found"

    @pytest.mark.asyncio
    async def test_find_element(self, mock_uc_start, mock_sleep):
        value = xpaths['email_input']

        url = 'https://www.google.com'
        driver = NoDriverService(mock_sleep)
        page = await driver.get(url)
        page.find.return_value = mock_element
        page.evaluate = AsyncMock()

        res = await driver.find_element(value=value)
        assert page.find.is_called_with(value, 1)
        assert hasattr(res, 'get_value')
        assert mock_sleep.is_called()
        assert page.evaluate.is_called_with(value)

    @pytest.mark.asyncio
    async def test_find_element_exception_caught(self, mock_uc_start, mock_sleep):
        value = selectors['uname_input']
        action = {'type': 'click', 'selector': selectors['uname_input']}

        url = 'https://www.google.com'
        driver = NoDriverService(mock_sleep)
        page = await driver.get(url)
        page.find.return_value = None

        with pytest.raises(Exception) as e:
            await driver.find_element(value=value)
            assert page.find.is_called_with(value, 1)
            assert e.value == f"Element for {action['type']} action was not found"

    @pytest.mark.asyncio
    async def test_click_element(self, mock_uc_start, mock_sleep, mock_element):
        value = xpaths['email_input']

        url = 'https://www.google.com'
        driver = NoDriverService(mock_sleep)
        page = await driver.get(url)

        test_element = mock_element
        page.find.return_value = test_element

        res = await driver.find_element(value=value)
        await driver.click_element(element=res)
        assert test_element.click.is_called()
        assert mock_sleep.is_called()

    @pytest.mark.asyncio
    async def test_type_input(self, mock_uc_start, mock_sleep, mock_element):
        value = xpaths['email_input']

        url = 'https://www.google.com'
        driver = NoDriverService(mock_sleep)
        page = await driver.get(url)

        test_element = mock_element
        get = Mock()
        # test_element.return_value.attrs.get.return_value = 'test input'
        page.find.return_value = test_element
        get.return_value = 'test input'

        # await driver.find_element(value=value)
        await driver.type_input(action={'value': value}, element=test_element)

        assert get.is_called_with('value')
        assert test_element.clear_input.is_called()
        assert test_element.send_keys.call_count == len(value)
        assert mock_sleep.is_called()

    @pytest.mark.asyncio
    async def test_dropdown_select(self, mock_uc_start, mock_sleep, mock_element):
        value = xpaths['email_input']

        url = 'https://www.google.com'
        driver = NoDriverService(mock_sleep)
        page = await driver.get(url)

        test_element = mock_element
        get = Mock()
        # test_element.return_value = TestElement(['enabled', get])
        # test_element.return_value.attrs.get.return_value = 'test input'
        page.find.return_value = test_element
        page.evaluate.side_effect = [None, 'not test option', 'test option']
        get.return_value = 'test option'

        # await driver.find_element(value=value)
        await driver.dropdown_select(action={'value': value, 'xpath': xpaths['email_input']},
                                     element=test_element)

        assert test_element.send_keys.is_called_with(value)
        assert page.evaluate.call_count == 3
        assert mock_sleep.is_called()

    @pytest.mark.asyncio
    async def test_dropdown_select_exception(self, mock_uc_start, mock_sleep, mock_element):
        value = xpaths['email_input']

        url = 'https://www.google.com'
        driver = NoDriverService(mock_sleep)
        page = await driver.get(url)

        test_element = mock_element
        get = Mock()
        # test_element.return_value.attrs.get.return_value = 'test input'
        page.find.return_value = test_element
        page.evaluate.side_effect = [None, 'not test option', 'test option']
        get.return_value = 'test option'

        # await driver.find_element(value=value)
        with pytest.raises(Exception) as e:
            await driver.dropdown_select(action={'value': value, 'xpath': xpaths['email_input']},
                                     element=test_element)
            assert e.value == 'Dropdown option could not be selected'

    @pytest.mark.asyncio
    async def test_upload_success(self, mock_uc_start, mock_sleep, mock_element):
        value = 'path/to/some/file.txt'

        url = 'https://www.google.com'
        driver = NoDriverService(mock_sleep)
        page = await driver.get(url)

        test_element = mock_element
        get = Mock()
        # test_element.return_value = TestElement(['enabled', get])
        # test_element.return_value.attrs.get.return_value = 'test input'
        page.find.return_value = test_element

        # await driver.find_element(value=value)
        await driver.upload(action={'value': value}, element=test_element)

        assert test_element.send_keys.is_called_with(value)
        assert mock_sleep.is_called()

    @pytest.mark.asyncio
    async def test_upload_exception_raised(self, mock_uc_start, mock_sleep, mock_element):
        value = 'path/to/some/file.txt'

        url = 'https://www.google.com'
        driver = NoDriverService(mock_sleep)
        page = await driver.get(url)

        test_element = mock_element
        get = Mock()
        # test_element.return_value = TestElement(['enabled', get])
        # test_element.return_value.attrs.get.return_value = 'test input'
        page.find.return_value = test_element

        # await driver.find_element(value=value)
        test_element.send_keys.side_effect = Exception('File upload issue')
        with pytest.raises(Exception) as e:

            await driver.upload(action={'value': value}, element=test_element)
            assert e.value == 'File upload issue'
            assert mock_sleep.is_called()

    @pytest.mark.asyncio
    @patch('src.service.nodriver_service.logger')
    async def test_switch_window(self, mock_logger, mock_uc_start, mock_sleep):

        url = 'https://www.google.com'
        driver = NoDriverService(mock_sleep)
        page1 = AsyncMock()
        page1.text = "Page 1"
        page1.url = 'example1.com'
        page1.bring_to_front = AsyncMock()
        page2 = AsyncMock()
        page2.text = "Page 2"
        page2.url = 'example2.com'
        page2.bring_to_front = AsyncMock()
        page = await driver.get(url)
        mock_uc_start.return_value.get_targets.return_value = [page, page1, page2]

        await driver.switch_window(tab_url='example2.com')
        page2.bring_to_front.assert_called()

        mock_logger.info.assert_called_with(f"Switched to new web page: {page2.text}")
        assert mock_sleep.is_called()

    @pytest.mark.asyncio
    @patch('src.service.nodriver_service.logger')
    async def test_return_to_original_window(self, mock_logger, mock_uc_start, mock_sleep):

        url = 'https://www.google.com'
        driver = NoDriverService(mock_sleep)
        page1 = AsyncMock()
        page1.text = "Page 1"
        page1.url = 'example1.com'
        page1.bring_to_front = AsyncMock()
        page2 = AsyncMock()
        page2.text = "Page 2"
        page2.url = 'example2.com'
        page2.bring_to_front = AsyncMock()
        page = await driver.get(url)
        mock_uc_start.return_value.get_targets.return_value = [page, page1, page2]

        await driver.return_to_original_window()
        page.bring_to_front.assert_called_once()
        page.close.assert_called_once()
        mock_logger.info.assert_called_with(f"Returned to original web page: {page.text}")

    @pytest.mark.asyncio
    async def test_close(self, mock_uc_start, mock_sleep):
        driver = NoDriverService(mock_sleep)
        await driver.get('example.com')

        await driver.close()
        assert mock_uc_start.close.is_called_once()
        assert mock_uc_start.stop.is_called_once()

