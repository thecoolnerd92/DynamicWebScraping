
from src.load_config import load_json
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.resolve()

# specify your config file here
# __config_file = f'{PROJECT_ROOT}/incolumitas_challenge.json'
__config_file = f'{PROJECT_ROOT}/bot_detection_config.json'
# __config_file = f'{PROJECT_ROOT}/test_config.json'
config = load_json(__config_file)