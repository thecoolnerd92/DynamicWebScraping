import asyncio

import pytest
from unittest.mock import patch, Mock, mock_open, MagicMock, AsyncMock
from src.main import *
from custom_fixtures import create_named_test_file, mock_element
# import pickle # Barry
from settings import *

attr_list = ['id', 'name', 'class', 'href', 'src', 'value', 'style', 'alt', 'innerHTML', 'outerHTML']
funcs = ['is_displayed', 'is_enabled']
builtin_values = ['text', 'tag_name', 'size', 'location']

@pytest.fixture(scope="function")
def mock_uc_start():
    with patch('src.service.nodriver_service.uc.start') as uc_mock:
        uc_mock.return_value.stop = Mock()
        uc_mock.return_value.close = AsyncMock()
        uc_mock.return_value.get = AsyncMock()
        uc_mock.return_value.get.return_value.xpath = AsyncMock()
        uc_mock.return_value.get.return_value.find = AsyncMock()
        page = AsyncMock()
        page.evaluate = AsyncMock()
        page.text = "Original Page"
        page.url = 'example.com'
        page.bring_to_front = AsyncMock()
        uc_mock.return_value.get.return_value = page
        uc_mock.return_value.tabs = [page]
        uc_mock.return_value.get_targets.return_value = [page]

        yield uc_mock

@pytest.fixture(scope='function')
def mock_scraper_class(mock_element):
    with patch('src.main.DynamicWebScraping') as scraper_mock:
        scraper_mock = AsyncMock()
        scraper_mock.find_elements.return_value = mock_element
        scraper_mock.find_element.return_value = mock_element
        scraper_mock.click_element = AsyncMock()
        scraper_mock.type_input = AsyncMock()
        scraper_mock.open_new_window = AsyncMock()
        scraper_mock.get_original_page = AsyncMock()
        scraper_mock.return_to_original_window = AsyncMock()
        yield scraper_mock


@pytest.fixture(scope='function')
def mock_driver_wait():
    # return_value = request.param['return_value']
    with patch('src.main.WebDriverWait') as mock_wait:
        mock_wait.return_value.until.return_value = Mock()
        yield mock_wait

@pytest.fixture(scope='function')
def mock_sleep():
    with patch('src.main.sleep') as sleep_mock:
        yield sleep_mock

@pytest.fixture(scope='session')
def mock_requests():
    with patch('src.main.requests') as requests_mock:
        requests_mock.Session.return_value = Mock()
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None

        # Set the `__enter__` and `__exit__` methods to make it a context manager
        # setattr(mock_response, '__enter__', )
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = False
        # Create an iterable for iter_content, as the `for` loop needs to run
        # This simulates a file with content, a list of byte chunks
        mock_response.iter_content.return_value = iter([b'chunk1', b'chunk2'])

        # Set up the mock for requests.Session.get to return our context manager mock
        requests_mock.Session.return_value.get.return_value = mock_response

        yield requests_mock

class TestDynamicWebScraping:
    @pytest.mark.asyncio
    async def test_get_driver(self, mock_uc_start):
        actions = [
            {
                'type': 'url',
                'value': 'weburl'
            }
        ]
        config = {
            "actions": actions
        }
        my_class = DynamicWebScraping(config, mock_uc_start.return_value)
        await my_class.get_driver('example.com')

        mock_uc_start.return_value.get.assert_called_once_with('example.com')


    @pytest.mark.asyncio
    async def test_get_driver_exception(self, mock_uc_start):
        actions = [
            {
                'type': 'url',
                'value': 'weburl'
            }
        ]
        config = {
            "actions": actions
        }
        my_class = DynamicWebScraping(config, mock_uc_start.return_value)
        mock_uc_start.return_value.get.side_effect = Exception("Error Starting UC Driver")
        with pytest.raises(Exception) as e:
            await my_class.get_driver('example.com')
            assert e.value == "Error Starting UC Driver"


        mock_uc_start.return_value.get.assert_called_once_with('example.com')

#     @pytest.mark.parametrize(
#         'get_pickle_cache',
#         [{"filepath": f'{cache_folder}\\click_action_1.pkl'}],
#         indirect=True
#     )
#     @patch('src.main.DynamicWebScraping._run_download_document')
#     @patch('src.main.DynamicWebScraping._run_click_visible_button')
#     @patch('src.main.time')
#     def test_run_actions(self, mock_time, mock_run_click_visible_btn, mock_run_download_doc, mock_uc_start):
#         mock_time.sleep.return_value = None
#         mock_run_click_visible_btn.return_value = None
#         actions = [
#             {
#                 'type': 'url',
#                 'value': 'weburl'
#             },
#             {
#                 'type': 'download',
#                 'wait': 2,
#                 'value': 'fileurl'
#             },
#             {
#                 'type': 'click',
#             }
#         ]
#         config = {
#             "actions": actions
#         }
#         my_class = DynamicWebScraping(config, mock_uc_startuc.return_value.get)
#         my_class.run_actions(actions)
#         mock_run_download_doc.assert_called_once()
#         mock_run_click_visible_btn.assert_called_once()
#         mock_uc_start.return_value.get.assert_called_once()
#         mock_time.sleep.assert_called_once()
#
    @pytest.mark.asyncio
    async def test_button_click(self, mock_scraper_class, mock_uc_start, mock_sleep, mock_element):
        action = {
              "type": "click",
              "xpath": '//*[@id="default"]/div/div/div/div/section/div[2]/ol/li[2]/article/div[2]/form',
              "value": "https://books.toscrape.com/",
              "wait": 2,
              "debug": True,
                "index": 1
        }
        config = {
            "actions": [action]
        }
        test_element = mock_element
        mock_scraper_class.find_element.return_value = test_element

        my_class = DynamicWebScraping(config, mock_scraper_class)
        await my_class.run_actions([action])

        mock_sleep.assert_called_once()
        mock_scraper_class.find_element.assert_called_once_with(by=By.XPATH, value=action['xpath'], action=action)
        mock_scraper_class.click_element.assert_called_once_with(element=test_element, required=False)

    @pytest.mark.asyncio
    async def test_button_click_not_found_exception(self, mock_scraper_class, mock_uc_start, mock_sleep, mock_element):
        action = {
            "type": "click",
            "xpath": '//*[@id="default"]/div/div/div/div/section/div[2]/ol/li[2]/article/div[2]/form',
            "value": "https://books.toscrape.com/",
            "wait": 2,
            "required": True,
            "debug": True,
            "index": 1
        }
        config = {
            "actions": [action]
        }
        test_element = mock_element
        test_element.is_displayed = AsyncMock()
        test_element.is_displayed.return_value = False
        mock_scraper_class.find_element.return_value = test_element

        with pytest.raises(Exception) as e:
            my_class = DynamicWebScraping(config, mock_scraper_class)
            await my_class.run_actions([action])
            assert e.value == f"The button was not found in the given wait time"
            mock_scraper_class.find_element.assert_called_once_with(by=By.XPATH, value=action['xpath'], action=action)
            mock_scraper_class.click_element.assert_not_called()
            mock_sleep.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_type_input(self, mock_scraper_class, mock_uc_start, mock_sleep, mock_element):
        action = {
              "type": "input",
              "xpath": '//*[@id="default"]/div/div/div/div/section/div[2]/ol/li[2]/article/div[2]/form',
              "value": "https://books.toscrape.com/",
              "wait": 2,
              "debug": True,
                "index": 1
        }
        config = {
            "actions": [action]
        }
        test_element = mock_element
        mock_scraper_class.find_element.return_value = test_element

        my_class = DynamicWebScraping(config, mock_scraper_class)
        await my_class.run_actions([action])

        mock_sleep.assert_called_once()
        mock_scraper_class.find_element.assert_called_once_with(by=By.XPATH, value=action['xpath'], action=action)
        mock_scraper_class.type_input.assert_called_once_with(element=test_element, action=action)

    @pytest.mark.asyncio
    async def test_run_type_input_not_found_exception(self, mock_scraper_class, mock_uc_start, mock_sleep, mock_element):
        action = {
            "type": "input",
            "xpath": '//*[@id="default"]/div/div/div/div/section/div[2]/ol/li[2]/article/div[2]/form',
            "value": "https://books.toscrape.com/",
            "wait": 2,
            "required": True,
            "debug": True,
            "index": 1
        }
        config = {
            "actions": [action]
        }
        test_element = mock_element
        test_element.is_displayed = AsyncMock()
        test_element.is_displayed.return_value = False
        mock_scraper_class.find_element.return_value = test_element

        with pytest.raises(Exception) as e:
            my_class = DynamicWebScraping(config, mock_scraper_class)
            await my_class.run_actions([action])
            assert e.value == f"The input element was not found in the given wait time"
            mock_scraper_class.find_element.assert_called_once_with(by=By.XPATH, value=action['xpath'], action=action)
            mock_scraper_class.type_input.assert_not_called()
            mock_sleep.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_dropdown_selection(self, mock_scraper_class, mock_uc_start, mock_sleep, mock_element):
        action = {
            "type": "select",
            "xpath": '//*[@id="default"]/div/div/div/div/section/div[2]/ol/li[2]/article/div[2]/form',
            "value": "https://books.toscrape.com/",
            "wait": 2,
            "debug": True,
            "index": 1
        }
        config = {
            "actions": [action]
        }
        test_element = mock_element
        mock_scraper_class.find_element.return_value = test_element

        my_class = DynamicWebScraping(config, mock_scraper_class)
        await my_class.run_actions([action])

        assert mock_sleep.call_count == 2
        mock_scraper_class.find_element.assert_called_once_with(by=By.XPATH, value=action['xpath'], action=action)
        mock_scraper_class.dropdown_select.assert_called_once_with(element=test_element, action=action)

    @pytest.mark.asyncio
    async def test_run_dropdown_selection_not_found_exception(self, mock_scraper_class, mock_uc_start, mock_sleep, mock_element):
        action = {
            "type": "select",
            "xpath": '//*[@id="default"]/div/div/div/div/section/div[2]/ol/li[2]/article/div[2]/form',
            "value": "https://books.toscrape.com/",
            "wait": 2,
            "required": True,
            "debug": True,
            "index": 1
        }
        config = {
            "actions": [action]
        }
        test_element = mock_element
        test_element.is_displayed = AsyncMock()
        test_element.is_displayed.return_value = False
        mock_scraper_class.find_element.return_value = test_element

        with pytest.raises(Exception) as e:
            my_class = DynamicWebScraping(config, mock_scraper_class)
            await my_class.run_actions([action])
            assert e.value == f"The dropdown was not found in the given wait time"
            mock_scraper_class.find_element.assert_called_once_with(by=By.XPATH, value=action['xpath'],
                                                                    action=action)
            mock_scraper_class.dropdown_select.assert_not_called()
            assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    async def test_run_dropdown_selection(self, mock_scraper_class, mock_uc_start, mock_sleep, mock_element):
        action = {
            "type": "select",
            "xpath": '//*[@id="default"]/div/div/div/div/section/div[2]/ol/li[2]/article/div[2]/form',
            "value": "https://books.toscrape.com/",
            "wait": 2,
            "debug": True,
            "index": 1
        }
        config = {
            "actions": [action]
        }
        test_element = mock_element
        mock_scraper_class.find_element.return_value = test_element

        my_class = DynamicWebScraping(config, mock_scraper_class)
        await my_class.run_actions([action])

        assert mock_sleep.call_count == 2
        mock_scraper_class.find_element.assert_called_once_with(by=By.XPATH, value=action['xpath'], action=action)
        mock_scraper_class.dropdown_select.assert_called_once_with(element=test_element, action=action)

    @pytest.mark.asyncio
    async def test_run_dropdown_selection_not_found_exception(self, mock_scraper_class, mock_uc_start, mock_sleep):
        action = {
            "type": "select",
            "xpath": '//*[@id="default"]/div/div/div/div/section/div[2]/ol/li[2]/article/div[2]/form',
            "value": "https://books.toscrape.com/",
            "wait": 2,
            "required": True,
            "debug": True,
            "index": 1
        }
        config = {
            "actions": [action]
        }
        test_element = AsyncMock()
        test_element.is_displayed = AsyncMock()
        test_element.is_displayed.return_value = False
        mock_scraper_class.find_element.return_value = test_element

        with pytest.raises(Exception) as e:
            my_class = DynamicWebScraping(config, mock_scraper_class)
            await my_class.run_actions([action])
            assert e.value == f"The dropdown was not found in the given wait time"
            mock_scraper_class.find_element.assert_called_once_with(by=By.XPATH, value=action['xpath'],
                                                                    action=action)
            mock_scraper_class.dropdown_select.assert_not_called()
            assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    async def test_run_popup_window(self, mock_scraper_class, mock_uc_start, mock_sleep):
        action = {
            "type": "external_click",
            "xpath": '//*[@id="default"]/div/div/div/div/section/div[2]/ol/li[2]/article/div[2]/form',
            "value": "https://books.toscrape.com/",
            "debug": True,
            "index": 1,
            "sub_actions": []
        }
        config = {
            "actions": [action]
        }

        # call_count = 0
        # mock_scraper_class.get_original_page.return_value = 'original page'
        # mock_scraper_class.switch_window.return_value = 'new page'
        # # update the
        # def side_effect(*args, **kwargs):
        #     nonlocal call_count
        #     call_count += 1
        #     if call_count >= 3:  # Simulate condition met after 3 "sleeps"
        #         mock_scraper_class.get_original_page.return_value = 'original page'

        my_class = DynamicWebScraping(config, mock_scraper_class)
        await my_class.run_actions([action])

        assert mock_sleep.call_count == 1
        mock_scraper_class.open_new_window.assert_called_once()
        mock_scraper_class.return_to_original_window.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'create_named_test_file',
        [{"file_name": "test_file.txt"}],
        indirect=True
    )
    @patch('src.main.dt')
    async def test_run_download_document(self, mock_dt, create_named_test_file, mock_scraper_class, mock_element, mock_requests):
        action = {
            "type": "download",
            "xpath": '//*[@id="default"]/div/div/div/div/section/div[2]/ol/li[2]/article/div[2]/form',
            "value": "temp_folder",
            "debug": True,
            "index": 1,
            "sub_actions": []
        }
        directory = os.path.split(create_named_test_file)[0]
        config = {
            "actions": [action],
            "separator": "/",
            "download_directory": directory
        }
        my_dt = "2025-10-01-00-00-00"
        mock_dt.datetime.now.return_value.strftime.return_value = my_dt
        filename = f"{directory}/temp_folder/file.txt_{my_dt}"

        my_class = DynamicWebScraping(config, mock_scraper_class)
        mock_scraper_class.find_element.return_value = mock_element
        mock_element.get_attribute = Mock()
        mock_element.get_attribute.return_value = 'https://file.text'
        m = mock_open()

        # @pytest.mark.asyncio
        with patch('builtins.open', m):
            await my_class.run_actions([action])

            mock_requests.Session.return_value.get.assert_called_with('https://file.text', timeout=30, stream=True)
            m.assert_called_once()
            assert m.return_value.write.call_count == 2
            mock_requests.Session.return_value.get.return_value.iter_content.assert_called_once()
            mock_scraper_class.find_element.assert_called_once_with(by=By.XPATH, value=action['xpath'], action=action)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'create_named_test_file',
        [{"file_name": "test_file.txt"}],
        indirect=True
    )
    @patch('src.main.dt')
    async def test_run_download_document_exception(self, mock_dt, create_named_test_file, mock_scraper_class, mock_element, mock_requests):
        action = {
            "type": "download",
            "xpath": '//*[@id="default"]/div/div/div/div/section/div[2]/ol/li[2]/article/div[2]/form',
            "value": "temp_folder",
            "debug": True,
            "index": 1,
            "sub_actions": []
        }
        directory = os.path.split(create_named_test_file)[0]
        config = {
            "actions": [action],
            "separator": "/",
            "download_directory": directory
        }
        my_dt = "2025-10-01-00-00-00"
        mock_dt.datetime.now.return_value.strftime.return_value = my_dt
        filename = f"{directory}/temp_folder/file.txt_{my_dt}"

        my_class = DynamicWebScraping(config, mock_scraper_class)
        mock_scraper_class.find_element.return_value = mock_element
        mock_element.get_attribute = Mock()
        mock_element.get_attribute.return_value = 'https://file.text'
        m = mock_open()

        # @pytest.mark.asyncio
        with patch('builtins.open', m):
            mock_requests.Session.return_value.get.side_effect = Exception('Get req error')

            with pytest.raises(Exception) as e:
                await my_class.run_actions([action])
                assert e.value == 'Get req error'