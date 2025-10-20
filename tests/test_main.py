
import pytest
from unittest.mock import patch, Mock, mock_open, MagicMock
from src.html_cache import *
from custom_fixtures import create_named_test_file
import pickle # Barry
cache_folder = f'{cwd}\\pickle_cache'

attr_list = ['id', 'name', 'class', 'href', 'src', 'value', 'style', 'alt', 'innerHTML', 'outerHTML']
funcs = ['is_displayed', 'is_enabled']
builtin_values = ['text', 'tag_name', 'size', 'location']""

@pytest.fixture(scope='function')
def mock_get_driver():
    with patch('src.html_cache.get_driver', autospec=True) as mock_driver:
        # url = "https://books.toscrape.com/"
        mock_driver.return_value.get_cookies.return_value = Mock()
        yield mock_driver

@pytest.fixture(scope='function')
def mock_driver_wait():
    # return_value = request.param['return_value']
    with patch('src.html_cache.WebDriverWait') as mock_wait:
        mock_wait.return_value.until.return_value = Mock()
        yield mock_wait

@pytest.fixture(scope='session')
def mock_requests():
    with patch('src.html_cache.requests') as requests_mock:
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

class TestSampleClass:
    @patch('src.html_cache.SampleClass._run_download_document')
    @patch('src.html_cache.SampleClass._run_click_visible_button')
    @patch('src.html_cache.time')
    def test_run_actions(self, mock_time, mock_run_click_visible_btn, mock_run_download_doc, mock_get_driver):
        mock_time.sleep.return_value = None
        mock_run_click_visible_btn.return_value = None
        actions = [
            {
                'type': 'url',
                'value': 'weburl'
            },
            {
                'type': 'download',
                'wait': 2,
                'value': 'fileurl'
            },
            {
                'type': 'click',
            }
        ]
        config = {
            "actions": actions
        }
        my_class = SampleClass(config)
        my_class.run_actions(actions)
        mock_run_download_doc.assert_called_once()
        mock_run_click_visible_btn.assert_called_once()
        mock_get_driver.return_value.get.assert_called_once()
        mock_time.sleep.assert_called_once()

    @patch('src.html_cache.time')
    def test_get_driver_exception(self, mock_time, mock_get_driver):
        mock_time.sleep.return_value = None
        actions = [
            {
                'type': 'url',
                'value': 'weburl'
            }
        ]
        config = {
            "actions": actions
        }
        my_class = SampleClass(config)

        mock_get_driver.return_value.get.side_effect = Exception('Chrome Driver Initialization Exception')
        with pytest.raises(Exception) as e:
            my_class.run_actions(actions)
            assert e.value == 'Chrome Driver Initialization Exception'


    @pytest.mark.parametrize(
        'get_pickle_cache',
        [{"filepath": f'{cache_folder}\\click_action_1.pkl'}],
        indirect=True
    )
    def test_button_click(self, mock_driver_wait, mock_get_driver, get_pickle_cache):
        # mock_driver_wait.return_value.until.return_value = element
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
        html_els = get_pickle_cache if isinstance(get_pickle_cache, list) else [get_pickle_cache]
        find_elements = MagicMock(return_value=html_els)
        mock_get_driver.return_value.find_elements_ = find_elements # get from pickle cache

        mock_driver_wait.return_value.until.return_value.click = MagicMock(return_value=None)
        my_class = SampleClass(config)
        my_class._run_click_visible_button(action, 2, 1)

        mock_get_driver.return_value.find_elements_.assert_called_once()
        mock_driver_wait.return_value.until.return_value.click.assert_called_once()

    def test_click_btn_not_found_exception(self, mock_driver_wait, mock_get_driver):
        action = {
            "type": "download",
            "xpath": '//*[@id="default"]/div/div/div/div/section/div[2]/ol/li[2]/article/div[2]/form',
            "value": "WOTC_temp",
            "wait": 2,
            "debug": True,
            "index": 1
        }
        config = {
            "actions": [action],
            "download_directory": ''
        }
        my_el = {}
        for att in attr_list + builtin_values:
            my_el[att] = None
        for att in funcs:
            my_el[att] = False

        html_attrs = HtmlAttributes()
        mock_get_driver.return_value.find_elements_.return_value = [html_attrs.get_element(my_el)]
        my_class = SampleClass(config)
        with pytest.raises(Exception) as e:
            my_class._run_click_visible_button(action, 2, 1)
            assert "Button was not found" in str(e.value)
        # html_attrs.attributes['href'] = False


    @pytest.mark.parametrize(
        'create_named_test_file',
        [{"file_name": "test_file.txt"}],
        indirect=True
    )
    def test_doc_download(self, create_named_test_file, mock_get_driver, mock_requests):
        """http file download"""

        action = {
            "type": "download",
            "xpath": '//*[@id="default"]/div/div/div/div/section/div[2]/ol/li[2]/article/div[2]/form',
            "value": "WOTC_temp",
            "wait": 2,
            "debug": True,
            "index": 1
        }
        config = {
            "actions": [action],
            "download_directory": os.path.split(create_named_test_file)[0]
        }
        my_el = {}
        for att in attr_list + funcs + builtin_values:
            my_el[att] = None
        my_el['href'] = 'https://website.com/downloadable_file.txt'

        html_attrs = HtmlAttributes()
        html_attrs.attributes['href'] = my_el['href']
        mock_get_driver.return_value.find_element_.return_value = html_attrs.get_element(my_el)
        my_class = SampleClass(config)
        m = mock_open()
        with patch('builtins.open', m):
            my_class._run_download_document(action, 2, 1)

            mock_requests.Session.return_value.get.assert_called_with(my_el['href'], timeout=2, stream=True)
            mock_get_driver.return_value.get_cookies.assert_called()
            m.assert_called_once()
            assert m.return_value.write.call_count == 2
            mock_requests.Session.return_value.get.return_value.iter_content.assert_called_once()

    def test_doc_download_exception(self, mock_requests, mock_get_driver):
        action = {
            "type": "download",
            "xpath": '//*[@id="default"]/div/div/div/div/section/div[2]/ol/li[2]/article/div[2]/form',
            "value": "WOTC_temp",
            "wait": 2,
            "debug": True,
            "index": 1
        }
        config = {
            "actions": [action],
            "download_directory": ''
        }
        my_class = SampleClass(config)
        get_attribute = Mock()
        get_attribute.return_value = 'file_url'
        mock_get_driver.return_value.find_element_.return_value = HtmlElement
        mock_get_driver.return_value.find_element_.return_value.get_attribute = Mock(return_value='file_url')
        mock_requests.Session.return_value.get.side_effect = Exception('Get req error')

        with pytest.raises(Exception) as e:
            my_class._run_download_document(action, 2, 1)
            assert e.value == 'Get req error'

    @pytest.mark.parametrize(
        'get_pickle_cache',
        [{"filepath": f'{cache_folder}\\input_action_3.pkl'}],
        indirect=True
    )
    def test_type_input(self, mock_driver_wait, mock_get_driver, get_pickle_cache):
        """"""
        action = {
              "type": "input",
              "xpath": '//*[@id="default"]/div/div/div/div/input/div[2]/ol/li[2]/article/div[2]/form',
              "value": "input text val",
              "wait": 2,
              "debug": True,
                "index": 1
        }
        config = {
            "actions": [action]
        }
        html_els = get_pickle_cache if isinstance(get_pickle_cache, list) else [get_pickle_cache]
        find_elements = MagicMock(return_value=html_els)
        mock_get_driver.return_value.find_elements_ = find_elements # get from pickle cache
        mock_driver_wait.return_value.until.return_value.send_keys = MagicMock(return_value=None)

        my_class = SampleClass(config)
        my_class._run_type_input(action, 2, 1)

        mock_get_driver.return_value.find_elements_.assert_called_once()
        mock_driver_wait.return_value.until.return_value.send_keys.assert_called_once_with(action['value'])

    @pytest.mark.parametrize(
        'get_pickle_cache',
        [{"filepath": f'{cache_folder}\\input_action_3.pkl'}],
        indirect=True
    )
    def test_type_input_exception(self, mock_driver_wait, mock_get_driver, get_pickle_cache):
        action = {
              "type": "input",
              "xpath": '//*[@id="default"]/div/div/div/div/input/div[2]/ol/li[2]/article/div[2]/form',
              "value": "input text val",
              "wait": 2,
              "debug": True,
                "index": 1
        }
        config = {
            "actions": [action]
        }
        html_els = get_pickle_cache if isinstance(get_pickle_cache, list) else [get_pickle_cache]
        find_elements = MagicMock(return_value=html_els)
        mock_get_driver.return_value.find_elements_ = find_elements # get from pickle cache
        mock_driver_wait.return_value.until.return_value.send_keys.side_effect = Exception('Selenium Text Input Error')
        my_class = SampleClass(config)
        with pytest.raises(Exception) as e:
            my_class._run_type_input(action, 2, 1)
            assert e.value == 'Selenium Text Input Error'

    @pytest.mark.parametrize(
        'get_pickle_cache',
        [{"filepath": f'{cache_folder}\\input_select_4.pkl'}],
        indirect=True
    )
    @patch('src.html_cache.Select')
    def test_dropdown_select(self, mock_select, mock_driver_wait, mock_get_driver, get_pickle_cache):
        action = {
              "type": "select",
              "xpath": '//*[@id="default"]/div/div/div/div/input/div[2]/ol/li[2]/article/div[2]/form',
              "value": "Select Option",
              "wait": 2,
              "debug": True,
                "index": 1
        }
        config = {
            "actions": [action]
        }
        html_els = get_pickle_cache if isinstance(get_pickle_cache, list) else [get_pickle_cache]
        find_elements = MagicMock(return_value=html_els)
        mock_get_driver.return_value.find_elements_ = find_elements # get from pickle cache
        mock_select.return_value.select_by_visible_text = MagicMock(return_value=None)

        my_class = SampleClass(config)
        my_class._run_dropdown_selection(action, 2, 1)

        mock_get_driver.return_value.find_elements_.assert_called_once()
        mock_select.return_value.select_by_visible_text.assert_called_once_with(action['value'])

    @pytest.mark.parametrize(
        'get_pickle_cache',
        [{"filepath": f'{cache_folder}\\input_action_3.pkl'}],
        indirect=True
    )
    @patch('src.html_cache.Select')
    def test_select_exception(self, mock_select, mock_driver_wait, mock_get_driver, get_pickle_cache):
        action = {
              "type": "select",
              "xpath": '//*[@id="default"]/div/div/div/div/input/div[2]/ol/li[2]/article/div[2]/form',
              "value": "Select Option",
              "wait": 2,
              "debug": True,
                "index": 1
        }
        config = {
            "actions": [action]
        }
        html_els = get_pickle_cache if isinstance(get_pickle_cache, list) else [get_pickle_cache]
        find_elements = MagicMock(return_value=html_els)
        mock_get_driver.return_value.find_elements_ = find_elements # get from pickle cache
        mock_select.return_value.select_by_visible_text.side_effect = Exception('Selenium Select Error')

        my_class = SampleClass(config)
        with pytest.raises(Exception) as e:
            my_class._run_dropdown_selection(action, 2, 1)
            assert e.value == f'Selenium Select Error'



@pytest.fixture(scope='session')
def mock_json_load():
    with patch('src.html_cache.json.load') as mock_load:
        yield mock_load

class TestLoadJson:
    @pytest.mark.parametrize(
        'create_named_test_file',
        [{"file_name": 'test_file.json', 'file_text': '{}'}],
        indirect=True
    )
    def test_load_json_success(self, create_named_test_file):
        # mock_json_load.return_value = {}
        my_file = create_named_test_file
        res = load_json(my_file)
        assert res == {}

    @pytest.mark.parametrize(
        'create_named_test_file',
        [{"file_name": 'test_file.json', 'file_text': '{}'}],
        indirect=True
    )
    def test_file_not_found_exception(self, mock_json_load, create_named_test_file):
        mock_json_load.side_effect = FileNotFoundError('File not found')
        with pytest.raises(Exception) as e:
            my_file = create_named_test_file
            load_json(my_file)
            assert e.value == 'File not found'

    @pytest.mark.parametrize(
        'create_named_test_file',
        [{"file_name": 'test_file.json', 'file_text': '{}'}],
        indirect=True
    )
    def test_invalid_json_exception(self, mock_json_load, create_named_test_file):
        mock_json_load.side_effect = json.JSONDecodeError('Invalid JSON', 'json_string', 0)
        with pytest.raises(Exception) as e:
            my_file = create_named_test_file
            load_json(my_file)
            assert e.value == 'Invalid JSON'

    @pytest.mark.parametrize(
        'create_named_test_file',
        [{"file_name": 'test_file.json', 'file_text': '{}'}],
        indirect=True
    )
    def test_unknown_exception(self, mock_json_load, create_named_test_file):
        mock_json_load.side_effect = Exception('Unknown Exception')
        with pytest.raises(Exception) as e:
            my_file = create_named_test_file
            load_json(my_file)
            assert e.value == 'Unknown Exception'

