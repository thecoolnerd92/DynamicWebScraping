# import yaml
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S %Z')
logger = logging.getLogger(__name__)


def load_json(file_path):
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