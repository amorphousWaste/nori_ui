#!/usr/bin/env python
"""Script to run before releasing a new version."""

import argparse
import os
import subprocess

from rich.progress import Progress

from project_stats import stats

PROJECT_NAME = 'nori_ui'
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(ROOT_DIR, PROJECT_NAME)
DOCS_DIR = os.path.join(ROOT_DIR, 'docs')
STATS_DIR = os.path.join(ROOT_DIR, 'project_stats')
GITHUB_PATH = f'https://github.com/amorphousWaste/{PROJECT_NAME}'


def get_args() -> dict:
    """Get the args from argparse.

    Returns:
        args (dict): Arguments from argparse.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--skipdocs',
        help='Run the pre-release script without generating docs.',
        action='store_true',
    )

    parser.add_argument(
        '--skipstats',
        help='Run the pre-release script without generating stats.',
        action='store_true',
    )

    parser.add_argument(
        '--skipblack',
        help='Run the pre-release script without black linting.',
        action='store_true',
    )

    args = parser.parse_args()
    return vars(args)


def generate_docs() -> None:
    """Generate pdoc documentation."""
    os.environ['PYTHONPATH'] = PROJECT_DIR

    cmd = [
        'pdoc',
        '--template-directory',
        os.path.join(DOCS_DIR, 'pdoc'),
        '--output-directory',
        DOCS_DIR,
        '--logo',
        f'"{GITHUB_PATH}/blob/main/images/icon_small.png"',
        '--logo-link',
        f'"{GITHUB_PATH}"',
        PROJECT_DIR,
    ]

    with Progress(transient=True) as progress:
        task = progress.add_task('Running pdoc...', total=100)
        progress.update(task, advance=1)

        # Call pdoc via subprocess.
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)

        progress.update(task, advance=100)
        progress.stop()


def generate_stats() -> None:
    """Generate the bot stats."""
    bot_stats = stats.BotStats()
    bot_stats.generate_stats_report()


def run_black() -> None:
    """Run black formatting check."""
    cmd = [
        'black',
        '--skip-string-normalization',
        '--diff',
        '--color',
        '--line-length',
        '79',
        '--target-version',
        'py39',
        ROOT_DIR,
    ]

    print('Running black...')
    # Call black via subprocess.
    output = subprocess.check_output(cmd)
    print(str(output.decode('utf-8')))


def run_prerelease() -> None:
    """Run the pre-release code."""
    # Get the arguments.
    args = get_args()

    if not args.get('skipdocs', False):
        generate_docs()

    if not args.get('skipstats', False):
        generate_stats()

    if not args.get('skipblack', False):
        run_black()


if __name__ == '__main__':
    run_prerelease()
