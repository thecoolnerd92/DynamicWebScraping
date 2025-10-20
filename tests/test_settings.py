import pytest
from custom_fixtures import create_named_test_file, mock_json_load

from settings import _load_json
import json

class TestLoadJson:
    @pytest.mark.parametrize(
        'create_named_test_file',
        [{"file_name": 'test_file.json', 'file_text': '{}'}],
        indirect=True
    )
    def test_load_json_success(self, create_named_test_file, mock_json_load):
        # mock_json_load.return_value = {}
        my_file = create_named_test_file
        mock_json_load.return_value = {}
        res = _load_json(my_file)
        assert res == {}
        assert mock_json_load.is_called_once_with('')

    @pytest.mark.parametrize(
        'create_named_test_file',
        [{"file_name": 'test_file.json', 'file_text': '{}'}],
        indirect=True
    )
    def test_file_not_found_exception(self, mock_json_load, create_named_test_file):
        mock_json_load.side_effect = FileNotFoundError('File not found')
        with pytest.raises(Exception) as e:
            my_file = create_named_test_file
            _load_json(my_file)
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
            _load_json(my_file)
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
            _load_json(my_file)
            assert e.value == 'Unknown Exception'