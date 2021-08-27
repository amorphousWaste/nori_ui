"""Globals."""

import logging
import os
import yaml

from exceptions import exceptions

# Define the path local to the package
LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(module)s> %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S%p')

LOG = logging.getLogger("nori_ui")

# Load the config file
config_path = os.path.join(LOCAL_PATH, 'config.yaml')
if not os.path.exists(config_path):
    raise exceptions.NoriConfigError(
        'Config file missing from: {}.'.format(config_path)
    )

try:
    with open(config_path, 'r') as config_file:
        CONFIG = yaml.full_load(config_file)
except Exception as e:
    raise exceptions.NoriConfigError('Invalid config.')
