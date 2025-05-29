# price_config.py

import json
import os


def load_price_config():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    # Assuming checker_config.json is in the same folder as this file;
    # adjust the path if it sits in the project root.
    config_path = os.path.join(root_dir, "checker_config.json")
    with open(config_path, "r") as f:
        return json.load(f)


PRICE_CONFIG = load_price_config()
