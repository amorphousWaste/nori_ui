"""Globals."""

import os
import yaml

from exceptions import exceptions

# Define the path local to the package
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_PATH = os.path.dirname(BASE_PATH)
CONFIG_PATH = os.path.join(PROJECT_PATH, 'configs', 'config.yaml')

# Load the config file
if not os.path.exists(CONFIG_PATH):
    raise exceptions.NoriConfigError(
        f'Config file missing from: {CONFIG_PATH}.'
    )

try:
    with open(CONFIG_PATH, 'r') as config_file:
        CONFIG = yaml.full_load(config_file)
except Exception:
    raise exceptions.NoriConfigError('Invalid config.')
