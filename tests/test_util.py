from lib2to3.pgen2.driver import Driver

import pytest

from src.service.util_service import CustomDriver
from src.service.nodriver_service import NoDriverService
from src.service.selenium_service import SeleniumUndetectableDriverService
import asyncio
from unittest.mock import patch, Mock, mock_open, MagicMock

from src.service.util_service import *
from custom_fixtures import create_test_files

@pytest.fixture(scope='session')
def mock_dt():
    with patch('src.service.util_service.dt', autospec=True) as mock_dt:
        mock_dt.datetime.now = Mock()
        mock_dt.timedelta = Mock()
        mock_dt.datetime.timestamp = Mock()
        yield mock_dt


@pytest.fixture(scope='function')
def mock_web_driver():
    with patch('src.service.util_service.webdriver', autospec=True) as mock_driver:
        # url = "https://books.toscrape.com/"
        yield mock_driver

@pytest.fixture(scope='function')
def mock_driver_wait():
    # return_value = request.param['return_value']
    with patch('src.services.selenium.WebDriverWait') as mock_wait:
        mock_wait.return_value.until.return_value = Mock()
        yield mock_wait

# Helper function to mock the write_pickle_file
@pytest.fixture
def mock_write_pickle_file():
    with patch('src.service.util_service.write_pickle_file') as mock_write:
        yield mock_write


@pytest.mark.parametrize(
    'driver_class',
    [([NoDriverService]), ([SeleniumUndetectableDriverService])]
)
def test_driver_initialization(driver_class):
    """Testing the general CustomDriver Class"""
    print('driver class', driver_class)
    driver = CustomDriver(driver_class)
    attrs = [
        'get', 'find_element', 'find_elements', 'click_element', 'type_input',
        'dropdown_select', 'file_upload', 'open_new_window', 'return_to_original_window',
        'close'
    ]
    assert all(hasattr(driver, attr) for attr in attrs)

    # assert it doesnt have private variables
    privates = ['__driver', '__sleep']
    assert not any(hasattr(driver, attr) for attr in privates)

@pytest.mark.asyncio
@patch('src.service.util_service.random.uniform')
@patch('src.service.util_service.asyncio.sleep')
async def test_sleep(mock_sleep, mock_random):
    mock_random.return_value = 1.5333

    await sleep(2)
    assert mock_random.is_called_once_with(1.2, 2)
    assert mock_sleep.is_called_once_with(1.5333)

def test_get_date_range_tuple():
    """
    Test getting a date range from monday to sunday
    """
    test_day = dt.date(2025, 10, 9)
    query_date = dt.datetime.combine(test_day, dt.time.min)
    date_format = "%Y-%m-%d %H:%M:%S"
    monday, sunday = get_date_range_tuple(query_date)

    assert query_date > monday
    assert query_date > sunday
    assert sunday > monday
    assert monday == dt.datetime.strptime('2025-09-29 00:00:00', date_format)
    assert sunday == dt.datetime.strptime('2025-10-05 00:00:00', date_format)


@pytest.mark.parametrize(
        'create_test_files',
        [{"file_prefixes": ['file1', 'latest_file']}],
        indirect=True
    )
@patch('src.service.util_service.glob.glob')
def test_get_most_recent_download_file(mock_glob ,create_test_files):
    """
    Test getting most recent download file from Downloads folder
    Ideally the folder path would be an input variable, but I did not write the code,
    so I can just mock the glob.glob return value
    """
    mock_glob.return_value = create_test_files
    res = get_most_recent_downloaded_file('file/path')
    filename = os.path.split(res)[1]
    assert filename.startswith('latest_file')

class TestCheckPath:
    @patch('src.service.util_service.os')
    def test_check_path(self, mock_os):
        mock_os.path.exists.return_value = False
        path = 'filepath'
        check_path(path)
        assert mock_os.path.exists.call_count == 1
        assert mock_os.makedirs.is_called_with(path)

    @patch('src.service.util_service.os')
    def test_check_path_exception(self, mock_os):
        mock_os.path.exists.return_value = False
        mock_os.makedirs.side_effect = PermissionError('Permission Denied')
        with pytest.raises(Exception) as e:
            path = 'filepath'
            check_path(path)
            assert e.value == 'Permission Denied'
            assert mock_os.path.exists.call_count == 1

        # assert mock_os.path.exists.call_count == 1
        # assert mock_os.makedirs.is_called_with(path)

attr_list = ['id', 'name', 'class', 'href', 'src', 'value', 'style', 'alt', 'innerHTML', 'outerHTML']
funcs = ['is_displayed', 'is_enabled']
builtin_values = ['text', 'tag_name', 'size', 'location']

my_el = {}
for att in attr_list + funcs + builtin_values:
    my_el[att] = None

class TestPickle:
    """Test pickling function"""
    def test_pickle_memoize_with_cache_key_and_debug_true(self, mock_write_pickle_file, tmp_path):
        """Test pickle-memoize with debug True and with a cache key input"""
        html_attrs = HtmlAttributes()
        selenium_el = html_attrs.get_element(my_el)
        # cache_el = html_attrs.set_element(selenium_el)
        @pickled_memoize(cache_dir=tmp_path)
        def mock_decorated_function(self, value, cache_key=None):
            return [value]  # Return a list to test that branch

        # setattr(my_el, 'get_attribute', self.get_attribute)
        # mock_get_driver.return_value.find_element_.return_value = html_attrs.get_element(my_el)
        mock_self = MagicMock()
        mock_self.debug = True  # Ensure caching is enabled

        result = mock_decorated_function(mock_self, value=selenium_el, cache_key='test_key')
        assert result == [selenium_el]
        mock_write_pickle_file.assert_called_once()
        call_args, call_kwargs = mock_write_pickle_file.call_args
        assert isinstance(call_args[0], list)
        assert call_args[1] == os.path.join(tmp_path, 'test_key.pkl')

    def test_pickle_memoize_no_cache_key_and_debug_true(self, mock_write_pickle_file, tmp_path):
        """Test pickle-memoize with debug True and no cache key"""
        html_attrs = HtmlAttributes()
        selenium_el = html_attrs.get_element(my_el)
        @pickled_memoize(cache_dir=tmp_path)
        def mock_decorated_function(self, value, cache_key='cache_key'):
            return [value]  # Return a list to test that branch

        # setattr(my_el, 'get_attribute', self.get_attribute)
        # mock_get_driver.return_value.find_element_.return_value = html_attrs.get_element(my_el)
        mock_self = MagicMock()
        mock_self.debug = True  # Ensure caching is enabled

        result = mock_decorated_function(mock_self, value=selenium_el)
        assert result == [selenium_el]
        mock_write_pickle_file.assert_called_once()
        call_args, call_kwargs = mock_write_pickle_file.call_args
        assert isinstance(call_args[0], list)

    def test_pickle_memoize_non_list_el(self, mock_write_pickle_file, tmp_path):
        """Test pickle-memoize with non-list selenium element"""
        html_attrs = HtmlAttributes()
        selenium_el = html_attrs.get_element(my_el)
        @pickled_memoize(cache_dir=tmp_path)
        def mock_decorated_function(self, value, cache_key='cache_key'):
            return value  # Return a list to test that branch

        # setattr(my_el, 'get_attribute', self.get_attribute)
        # mock_get_driver.return_value.find_element_.return_value = html_attrs.get_element(my_el)
        mock_self = MagicMock()
        mock_self.debug = True  # Ensure caching is enabled

        result = mock_decorated_function(mock_self, value=selenium_el)
        assert result == selenium_el
        mock_write_pickle_file.assert_called_once()
        call_args, call_kwargs = mock_write_pickle_file.call_args
        assert isinstance(call_args[0], dict)


class TestWritePickleFile:

    def setup_method(self, method):
        self.cacheable_data = {"sample_data": []}

    @patch('src.service.util_service.pickle.dump')
    def test_write_pickle_file_success(self, mock_pickle_dump, mock_dt, tmp_path):
        now = dt.datetime.now()
        mock_dt.datetime.now.return_value = now
        mock_dt.timedelta.return_value = dt.timedelta(hours=0)
        mock_dt.datetime.timestamp.return_value = now.timestamp()
        pick_data = {
            "cached_html": self.cacheable_data,
            "expiration_date": int(now.timestamp())
        }

        m = mock_open()
        with patch('builtins.open', m):
            file = tmp_path / 'file.pkl'
            write_pickle_file(self.cacheable_data, file)
            m.assert_called_once()
            mock_pickle_dump.assert_called_once_with(pick_data, m.return_value)

    @patch('src.service.util_service.os.path.exists')
    def test_permission_denied(self, mock_os_path_exists, tmp_path):
        file = tmp_path / 'file.pkl'
        mock_os_path_exists.return_value = True
        m = mock_open()
        # m.return_value.__enter__.return_value = None
        m.side_effect = PermissionError('Permission Denied')
        with patch('builtins.open', m):
            with pytest.raises(Exception) as e:
                write_pickle_file(self.cacheable_data, file)
                assert str(e.value) == 'Permission Denied'

        # print('e', str(e.value))
        # assert str(e.value) == 'Permission Denied'

    @patch('src.service.util_service.os.path.exists')
    def test_unknown_exception(self, mock_os_path_exists, tmp_path):
        file = tmp_path / 'file.pkl'
        mock_os_path_exists.return_value = True
        m = mock_open()
        m.side_effect = Exception('Unknown Exception')
        with patch('builtins.open', m):
            with pytest.raises(Exception) as e:
                write_pickle_file(self.cacheable_data, file)
                assert str(e.value) == 'Unknown Exception'
