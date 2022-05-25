"""Logging."""

import logging
from rich.logging import RichHandler


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s %(asctime)s [%(filename)s:%(lineno)d]> %(message)s',
    datefmt='%Y/%m/%d %I:%M:%S%p',
    handlers=[RichHandler(rich_tracebacks=True)],
)
LOG = logging.getLogger('TwitchBot')
