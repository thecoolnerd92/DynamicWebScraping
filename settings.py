
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S %Z')
logger = logging.getLogger(__name__)


def _load_json(file_path):
    """
    Load a json file and handle any errors
    :param file_path: path to the input json file to load, str
    :return:
    """
    try:
        with open(file_path, 'r') as config_file:
            config_data = json.load(config_file)
        return config_data
    except FileNotFoundError:
        logger.error(f"Error: Configuration file '{file_path}' not found.")
        raise
    except json.JSONDecodeError:
        logger.error(f"Error: Invalid JSON format in '{file_path}'.")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise

from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.resolve()

# specify your config file here
# __config_file = f'{PROJECT_ROOT}/incolumitas_challenge.json'
__config_file = f'{PROJECT_ROOT}/bot_detection_config.json'
# __config_file = f'{PROJECT_ROOT}/test_config.json'
config = _load_json(__config_file)