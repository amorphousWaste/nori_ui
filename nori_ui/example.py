#!/usr/bin/env python
"""Launch window."""

import argparse
import sys

from PySide6 import QtWidgets

import nori

from examples import example_ui


def get_args() -> dict:
    """Get the args from argparse.

    Returns:
        args (dict): Arguments from argparse.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--icon', help='Define an icon')

    parser.add_argument('-t', '--title', help='Set a title')

    parser.add_argument('-y', '--style', help='Set a stylesheet')

    parser.add_argument('-l', '--palette', help='Set a palette')

    parser.add_argument(
        '-s',
        '--show_status_bar',
        help='Show the status bar',
        action='store_true',
    )

    parser.add_argument(
        '-p', '--as_popup', help='Show as popup', action='store_true'
    )

    parser.add_argument(
        '-c',
        '--center',
        help='Move the window to the center of the screen',
        action='store_true',
    )

    parser.add_argument(
        '-e',
        '--example',
        help='Display the example instead',
        action='store_true',
    )

    parser.add_argument(
        '-d',
        '--default',
        help='Display the example with a default QMainWindow',
        action='store_true',
    )

    parser.add_argument(
        '-f',
        '--from_file',
        help='Display a central widget loaded from a file',
        action='store_true',
    )

    args = parser.parse_args()

    return vars(args)


def launch_window() -> None:
    """Launch the Nori instance."""
    args = get_args()

    app = QtWidgets.QApplication([])

    if args['example']:
        mw = example_ui.create_example(
            default=args['default'],
            from_file=args['from_file'],
            style=args['style'],
            palette=args['palette'],
        )

    else:
        # Discard any invalid arguments for Nori, so discard them
        del args['example']
        del args['default']
        del args['from_file']
        mw = nori.Nori(**args)
        mw.setMinimumSize(500, 400)

    mw.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    launch_window()
