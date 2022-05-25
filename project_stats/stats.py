#!/usr/bin/env python
"""Generate project stats."""

import bandit  # noqa: Unused, but needed for subprocessing
import json
import os
import pygount
import rich
import subprocess

from radon.complexity import cc_rank
from radon.metrics import mi_visit, mi_rank
from radon.visitors import ComplexityVisitor
from rich.progress import Progress


class BotStats(object):
    """Bot stats class."""

    PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    STATS_OUTPUT_FILE = os.path.join(PROJECT_DIR, 'project_stats', 'stats.md')
    EXTS = 'md,py,yaml'
    FILES_TO_SKIP = ''
    FOLDERS_TO_SKIP = 'docs,images,ref'
    BANDIT_OUTPUT_FILE = os.path.join(
        PROJECT_DIR, 'project_stats', 'bandit.json'
    )

    def __init__(self) -> None:
        """Init."""
        super(BotStats, self).__init__()

        self.analyses = []
        self.project_summary = pygount.ProjectSummary()

        self.complexity = {}
        self.maintainability = {}

        self.total_score = 0
        self.total_scanned = 0
        self.total_files = 0
        self.total_maintainability = 0

        self.too_complex_functions = {}
        self.too_complex_files = []

    def generate_pygount_report(self) -> None:
        """Complexity report in python."""
        # Build the pygount source scanner.
        source_scanner = pygount.analysis.SourceScanner(
            [self.PROJECT_DIR],
            suffixes=pygount.common.regexes_from(
                self.EXTS,
                default_patterns_text='*',
                source=None,
            ),
            folders_to_skip=pygount.common.regexes_from(
                self.FOLDERS_TO_SKIP,
                default_patterns_text=(
                    pygount.analysis.DEFAULT_FOLDER_PATTERNS_TO_SKIP_TEXT
                ),
                source=None,
            ),
            name_to_skip=pygount.common.regexes_from(
                self.FILES_TO_SKIP,
                default_patterns_text=(
                    pygount.analysis.DEFAULT_NAME_PATTERNS_TO_SKIP_TEXT
                ),
                source=None,
            ),
        )

        # Build the paths to scan.
        source_paths_and_groups_to_analyze = list(
            source_scanner.source_paths()
        )

        # For convenience, use a duplicate pool since some files,
        # eg. __init__.py are duplicates.
        duplicate_pool = pygount.analysis.DuplicatePool()

        # Build regexes from the patterns
        generated_regexes = pygount.common.regexes_from(
            pygount.analysis.DEFAULT_GENERATED_PATTERNS_TEXT
        )

        # Analyze the files and build the report.
        with Progress(transient=True) as progress:
            try:
                for source_path, group in progress.track(
                    source_paths_and_groups_to_analyze,
                    description='Generating Pygount Report...',
                ):
                    source_analysis = (
                        pygount.analysis.SourceAnalysis.from_file(
                            source_path,
                            group,
                            'automatic',
                            'utf-8',
                            generated_regexes=generated_regexes,
                            duplicate_pool=duplicate_pool,
                        )
                    )
                    # Build a project summary for the table.
                    self.project_summary.add(source_analysis)

                    # Add each individual analysis for processing.
                    self.analyses.append(source_analysis)

            except Exception as e:
                rich.print(f'Unable to scan {source_path}: {e}')

            finally:
                progress.stop()

    def create_pygount_markdown(self) -> str:
        """Convert the pygount report to a markdown table.

        Returns:
            md (str): Pygount taable as markdown.
        """
        md = []

        # Get the language summaries in order of code use.
        language_summaries = sorted(
            self.project_summary.language_to_language_summary_map.values(),
            key=lambda l: l.code_count,
            reverse=True,
        )

        # Build table header.
        md.append(
            '|Language|File Count|Code Count|Documentation Count|Empty Count|'
            'String Count|'
        )
        md.append('|---|---|---|---|---|---|')

        # Add each language summary.
        for ls in language_summaries:
            language = ls.language.strip('__')
            md.append(
                f'|{language}|{ls.file_count}|{ls.code_count}|'
                f'{ls.documentation_count}|{ls.empty_count}|{ls.string_count}|'
            )

        return '\n'.join(md)

    def generate_radon_report(self) -> str:
        """Generate a complexity report from radon.

        Returns:
            (str): radon complexity data.
        """
        # Filter the language files.
        python_files = [a for a in self.analyses if a.language == 'Python']
        with Progress(transient=True) as progress:
            for analysis in progress.track(
                python_files, description='Creating Radon Markdown...'
            ):

                with open(analysis.path, 'r') as in_file:
                    data = in_file.read()

                    # Generate the complexity of the code per file.
                    self.complexity[
                        analysis.path
                    ] = ComplexityVisitor.from_code(data)

                    # # Generate the maintainability report per file.
                    score = mi_visit(data, False)
                    rank = mi_rank(score)

                    # Format and store the maintainability.
                    self.maintainability[analysis.path] = {
                        'score': float('{:.2f}'.format(score)),
                        'rank': rank,
                    }

            progress.stop()

    def create_radon_complexity_markdown(self) -> str:
        """Convert the radon complexity data to markdown.

        Returns:
            str: Radon data in markdown.
        """
        md = []

        # Create complexity markdown.
        with Progress(transient=True) as progress:
            for path in progress.track(
                self.complexity, description='Creating Radon Markdown...'
            ):
                self.total_files += 1

                md.append(f'`{path}`  ')
                md.append('## Maintainability ##')
                score, rank = self.calculate_maintainability(path)
                md.append(
                    '{} (*{}*)'.format(float('{:.2f}'.format(score)), rank)
                )

                self.total_maintainability += score

                # 20 is the threshold for complexity of C or worse.
                if score < 20:
                    self.too_complex_files.append(
                        '`{}`: {} (*{}*)'.format(
                            path, float('{:.2f}'.format(score)), rank
                        )
                    )

                cv = self.complexity[path]

                if cv.classes or cv.functions:
                    md.append('## Complexity ##')

                # Add the class and method complexity markdowns.
                md.extend(self.generate_class_complexity(path, cv))

                # Add the function complexity markdowns.
                md.extend(self.generate_function_complexity(path, cv))

                md.append('\n---\n')

            progress.stop()

        md.insert(0, '\n---\n')

        # Calculate average maintainability score and rank.
        average_maintainability = '{:.2f}'.format(
            self.total_maintainability / self.total_files
        )
        average_maintainability_rank = mi_rank(float(average_maintainability))

        md.insert(
            0,
            f'**Average Maintainability**: {average_maintainability} '
            f'(*{average_maintainability_rank}*)  ',
        )

        # Calculate average complexity score and rank.
        average_complexity = '{:.2f}'.format(
            self.total_score / self.total_scanned
        )
        average_complexity_rank = cc_rank(float(average_complexity))

        md.insert(
            0,
            f'**Average Complexity**: {average_complexity} '
            f'(*{average_complexity_rank}*)  ',
        )

        return '\n'.join(md)

    def generate_class_complexity(
        self, path: str, cv: ComplexityVisitor
    ) -> list[str]:
        """Generate the radon complexity for a given class and its methods.

        Args:
            path (str): File path.
            cv (ComplexityVisitor): Complexity visitor for a class.

        Returns:
            list[str]: Complexity markdown as a list of formatted strings.
        """
        md = []

        # Go through the classes in the ComplexityVisitor
        for cv_class in cv.classes:
            class_complexity = cv_class.real_complexity
            class_rank = cc_rank(class_complexity)
            class_prefix = '└' if cv_class == cv.classes[-1] else '├'

            md.append(
                f'&nbsp;&nbsp;&nbsp;&nbsp;{class_prefix} Class: '
                f'`{cv_class.name}`: '
                f'{class_complexity} (*{class_rank}*)  '
            )

            self.total_score += class_complexity
            self.total_scanned += 1

            for method in cv_class.methods:
                method_rank = cc_rank(method.complexity)
                method_prefix = '└' if method == cv_class.methods[-1] else '├'

                md.append(
                    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
                    f'{method_prefix} Method: '
                    f'`{method.name}`: {method.complexity} '
                    f'(*{method_rank}*)  '
                )
                self.total_score += method.complexity
                self.total_scanned += 1

                if method.complexity > 10:
                    if path not in self.too_complex_functions:
                        self.too_complex_functions[path] = []

                    self.too_complex_functions[path].append(
                        f'Method: `{method.name}`: '
                        f'{method.complexity} (*{method_rank}*)  '
                    )

        return md

    def generate_function_complexity(
        self, path: str, cv: ComplexityVisitor
    ) -> list[str]:
        """Generate function complexity as markdown.

        Args:
            path (str): File path.
            cv (ComplexityVisitor): Complexity visitor for a class.

        Returns:
            list[str]: Complexity markdown as a list of formatted strings.
        """
        md = []

        for cv_function in cv.functions:
            function_rank = cc_rank(cv_function.complexity)
            function_prefix = '└' if cv_function == cv.functions[-1] else '├'

            md.append(
                f'&nbsp;&nbsp;&nbsp;&nbsp;{function_prefix} '
                f'Function: `{cv_function.name}`: '
                f'{cv_function.complexity} (*{function_rank}*)  '
            )

            if cv_function.complexity > 10:
                if path not in self.too_complex_functions:
                    self.too_complex_functions[path] = []

                self.too_complex_functions[path].append(
                    f'Method: `{cv_function.name}`: '
                    f'{cv_function.complexity} (*{function_rank}*)  '
                )

            self.total_score += cv_function.complexity
            self.total_scanned += 1

        return md

    def calculate_maintainability(self, path: str) -> tuple[int, str]:
        """Calculate the maintainability of a given path.

        Args:
            path (str): File path.

        Returns:
            (tuple(score (int), rank (str))): The score and rank of the file.
        """
        with open(path, 'r') as in_file:
            score = mi_visit(in_file.read(), False)
            rank = mi_rank(score)

            return score, rank

    def create_radon_maintainability_markdown(self) -> str:
        """Convert the radon maintainability data to markdown.

        Returns:
            (str): radon data in markdown.
        """
        md = []

        for path in self.maintainability:
            score = self.maintainability[path]['score']
            rank = self.maintainability[path]['rank']
            md.append(f'`{path}`: {score} (*{rank}*)  ')

        return '\n'.join(md)

    def generate_complex_files(self) -> str:
        """Create the markdown for complex files.

        Returns:
            (str): Complex files in markdown format.
        """
        md = []

        for file in sorted(self.too_complex_files):
            md.append(file)

        return '\n'.join(md)

    def generate_complex_functions(self) -> str:
        """Create the markdown for complex functions.

        Returns:
            (str): Complex functions in markdown format.
        """
        md = []

        for path in sorted(self.too_complex_functions):
            md.append(f'`{path}`  ')

            for func in self.too_complex_functions[path]:
                md.append(f'&nbsp;&nbsp;&nbsp;&nbsp;{func}')

        return '\n'.join(md)

    def generate_bandit_report(self) -> None:
        """Generate the bandit report and save it as JSON."""
        # Bandit command.
        cmd = [
            'bandit',
            '--recursive',
            '--severity-level',
            'low',
            '--confidence-level',
            'low',
            '--skip',
            'B311,B404',
            '--output',
            self.BANDIT_OUTPUT_FILE,
            '--format',
            'json',
            '--exit-zero',
            self.PROJECT_DIR,
        ]

        # Track the progress of the subprocess as a single chunk.
        with Progress(transient=True) as progress:
            task = progress.add_task('Running Bandit...', total=100)
            progress.update(task, advance=1)

            # Call bandit via subprocess.
            subprocess.check_output(cmd, stderr=subprocess.STDOUT),

            progress.update(task, advance=100)
            progress.stop()

        # Read in the generated bandit data.
        with open(self.BANDIT_OUTPUT_FILE, 'r') as in_file:
            self.bandit_data = json.load(in_file)

    def create_bandit_markdown(self) -> str:
        """Create the markdown for bandit.

        Returns:
            (str): Bandit report in markdown format.
        """
        md = []

        # Get the results from the bandit report.
        results = self.bandit_data.get('results', {})

        with Progress(transient=True) as progress:
            for result in progress.track(
                results, description='Creating Bandit Markdown...'
            ):
                code = result.get('code', '')
                col_offset = result.get('col_offset', '')
                filename = result.get('filename', '')
                issue_confidence = result.get('issue_confidence', '')
                link = result.get('issue_cwe', {}).get('link', '')
                issue_severity = result.get('issue_severity', '')
                issue_text = result.get('issue_text', '')
                line_number = result.get('line_number', '')
                more_info = result.get('more_info', '')
                test_id = result.get('test_id', '')
                test_name = result.get('test_name', '')

                # Format the code.
                md.extend(
                    [
                        f'## {test_name} - Severity: {issue_severity} - '
                        f'Confidence: {issue_confidence} ##',
                        f'`{filename}`@`{col_offset}`:`{line_number}`  \n'
                        f'```python{code}```  ',
                        f'**Issue**: {issue_text}  ',
                        f'**ID**: {test_id}  ',
                        f'**More info**: {more_info}  ',
                        f'**Bandit link**: {link}  ',
                        '\n---\n',
                    ]
                )

            progress.stop()

        return '\n'.join(md)

    def generate_stats_report(self) -> None:
        """Generate the project stats report."""
        # Generate the reports.
        self.generate_pygount_report()
        pygount_table = self.create_pygount_markdown()
        self.generate_radon_report()
        radon_complexity_report = self.create_radon_complexity_markdown()
        complex_files = self.generate_complex_files()
        complex_functions = self.generate_complex_functions()
        self.generate_bandit_report()
        bandit_report = self.create_bandit_markdown()

        # Compile the md file.
        md_file = [
            '# Project Statistics #',
            'Generated by `stats.py`  ',
            '## How To Read This ##',
            'Complexity is calculated on a scale from 1 - 41+ '
            'where lower is better.  ',
            'Maintainability is calculated on a scale from 1 - 100 '
            'where higher is better.  ',
            '# Project Code Summary #',
            pygount_table,
            '\n---\n',
            '# Overly Complex Files #',
            complex_files,
            '# Overly Complex Functions #',
            '\n---\n',
            complex_functions,
            '\n---\n',
            '# Security Report #',
            '\n---\n',
            bandit_report,
            '# Full Project Complexity Report #',
            radon_complexity_report,
        ]

        # Save out the file.
        with open(self.STATS_OUTPUT_FILE, 'w') as out_file:
            out_file.write('\n'.join(md_file))

        rich.print('Done')


if __name__ == '__main__':
    bot_stats = BotStats()
    bot_stats.generate_stats_report()
