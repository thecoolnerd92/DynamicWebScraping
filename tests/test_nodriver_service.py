import asyncio

import pytest
from unittest.mock import patch, Mock, mock_open, MagicMock, AsyncMock

from src.service import nodriver_service
from custom_fixtures import create_named_test_file, mock_sleep
from src.service.nodriver_service import NoDriverService
from tests.custom_fixtures import xpaths, selectors


class TestElement:
    def __init__(self, attrs=[]):
        self.__attrs = attrs

    def attrs(self):
        return self.__attrs

class TestNoDriverService:
    @pytest.mark.asyncio
    @patch('src.service.nodriver_service.uc.start')
    async def test_nodriver_service_get(self, mock_uc_start, mock_sleep):
        """driver initialization"""
        url = 'https://www.google.com'
        mock_uc_start.return_value.get = AsyncMock()
        driver = NoDriverService(mock_sleep)
        await driver.get(url)

        assert mock_uc_start.is_called_once()
        assert mock_uc_start.return_value.get.is_called_once_with(url)

    @pytest.mark.asyncio
    @patch('src.service.nodriver_service.uc.start')
    async def test_nodriver_service_get_original_page(self, mock_uc_start, mock_sleep):
        """test getting the original page/ tab/ window"""
        url = 'https://www.google.com'
        mock_get = AsyncMock()
        mock_uc_start.return_value.get = mock_get
        driver = NoDriverService(mock_sleep)
        await driver.get(url)
        res = driver.get_original_page()

        assert res == mock_get.return_value

    @pytest.mark.asyncio
    @patch('src.service.nodriver_service.uc.start')
    async def test_nodriver_service_get_page(self, mock_uc_start, mock_sleep):
        """test getting the current page/ tab/ window"""
        url = 'https://www.google.com'
        mock_get = AsyncMock()
        mock_uc_start.return_value.get = mock_get
        driver = NoDriverService(mock_sleep)
        await driver.get(url)
        res = driver.get_original_page()

        assert res == mock_get.return_value

    @pytest.mark.asyncio
    @patch('src.service.nodriver_service.uc.start')
    async def test_find_elements(self, mock_uc_start, mock_sleep):
        value = xpaths['email_input']
        elements = [TestElement(['enabled'])]

        url = 'https://www.google.com'
        mock_get = AsyncMock()
        mock_uc_start.return_value.get = mock_get
        driver = NoDriverService(mock_sleep)
        page = await driver.get(url)
        page.xpath = AsyncMock()
        page.xpath.return_value = elements

        res = await driver.find_elements(value=value)
        assert page.xpath.is_called_with(value, 1)
        assert hasattr(res[0], 'is_displayed')

    @pytest.mark.asyncio
    @patch('src.service.nodriver_service.uc.start')
    async def test_find_elements_exception_caught(self, mock_uc_start, mock_sleep):
        value = selectors['uname_input']
        action = {'type': 'click', 'selector': selectors['uname_input']}

        url = 'https://www.google.com'
        mock_get = AsyncMock()
        mock_uc_start.return_value.get = mock_get
        driver = NoDriverService(mock_sleep)
        page = await driver.get(url)
        page.xpath = AsyncMock()
        page.xpath.return_value = []

        with pytest.raises(Exception) as e:
            await driver.find_elements(value=value, action=action, by='classname')
            assert page.xpath.is_called_with(value, 1, )
            assert e.value == f"Element for {action['type']} action was not found"

