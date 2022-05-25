"""Example UI.

This is used both to test changes to functionality and styling as well as a
basic reference for working with widgets.
"""

import os

from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from typing import Optional

import nori
import utils
from presets import dialogs
from widgets import switch


class ExampleUI(QtWidgets.QWidget):
    """A general example of UI elements in a Nori Window."""

    def __init__(self) -> None:
        """Init."""
        super(ExampleUI, self).__init__()

        self.init_UI()

    def init_UI(self) -> None:
        """Initialize the UI."""
        self.main_layout = QtWidgets.QVBoxLayout()
        self.grid_layout = QtWidgets.QGridLayout()
        self.main_layout.addLayout(self.grid_layout)
        self.setLayout(self.main_layout)

        self.create_title_label()
        self.create_line_edit()
        self.create_check_box_group()
        self.create_radio_button_group()
        self.create_combo_box()
        self.create_text_box_group()
        self.create_slider()
        self.create_spin_box()

        self.create_tabbed_layout()

        self.create_line()
        self.bottom_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.bottom_layout)
        self.create_progress_bar()
        self.create_buttons()

    def create_title_label(self) -> None:
        """Create the title label."""
        self.title_label = QtWidgets.QLabel('Example UI')
        self.title_label.setObjectName('title')
        self.title_label.setToolTip('Tooltip!')
        self.grid_layout.addWidget(self.title_label, 0, 0, 1, 2)

    def create_line_edit(self) -> None:
        """Create the line edit."""
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.setPlaceholderText('Line Edit')
        self.grid_layout.addWidget(self.line_edit, 1, 0, 1, 2)

    def create_check_box_group(self) -> None:
        """Create the group containing the checkboxes."""
        self.check_box_group = QtWidgets.QGroupBox('Check Boxes')
        self.check_box_layout = QtWidgets.QVBoxLayout()
        self.check_box_group.setLayout(self.check_box_layout)

        self.check_box_one = QtWidgets.QCheckBox('Check 1')
        self.check_box_layout.addWidget(self.check_box_one)

        self.check_box_two = QtWidgets.QCheckBox('Check 2')
        self.check_box_layout.addWidget(self.check_box_two)

        self.check_box_three = QtWidgets.QCheckBox('Check 3')
        self.check_box_three.setEnabled(False)
        self.check_box_layout.addWidget(self.check_box_three)

        self.check_box_four = QtWidgets.QCheckBox('Check 4')
        self.check_box_four.setEnabled(False)
        self.check_box_four.setChecked(True)
        self.check_box_layout.addWidget(self.check_box_four)

        self.grid_layout.addWidget(self.check_box_group, 2, 0, 1, 1)

    def create_radio_button_group(self) -> None:
        """Create the group containing the radio buttons."""
        self.radio_button_group = QtWidgets.QGroupBox('Radio Buttons')
        self.radio_button_layout = QtWidgets.QVBoxLayout()
        self.radio_button_group.setLayout(self.radio_button_layout)

        self.radio_button_one = QtWidgets.QRadioButton('Radio 1')
        self.radio_button_layout.addWidget(self.radio_button_one)

        self.radio_button_two = QtWidgets.QRadioButton('Radio 2')
        self.radio_button_layout.addWidget(self.radio_button_two)

        self.radio_button_three = QtWidgets.QRadioButton('Radio 3')
        self.radio_button_three.setEnabled(False)
        self.radio_button_layout.addWidget(self.radio_button_three)

        self.radio_button_four = QtWidgets.QRadioButton('Radio 4')
        self.radio_button_four.setEnabled(False)
        self.radio_button_four.setChecked(True)
        self.radio_button_layout.addWidget(self.radio_button_four)

        self.grid_layout.addWidget(self.radio_button_group, 2, 1, 1, 1)

    def create_combo_box(self) -> None:
        """Create the editable combo box with some items."""
        self.combo_box = QtWidgets.QComboBox()
        self.combo_box.setEditable(True)
        self.combo_box.addItems(['Item 1', 'Item 2', 'Item 3'])

        self.grid_layout.addWidget(self.combo_box, 3, 0, 1, 2)

    def create_text_box_group(self):
        """Create a text box with some sample text."""
        self.text_box = QtWidgets.QTextEdit()

        lorem_ipsum = (
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '
            'Cras ac sollicitudin turpis, vitae malesuada purus. '
            'Etiam eu rutrum nisi, quis pretium lacus.'
        )

        self.text_box.setText(lorem_ipsum)
        self.grid_layout.addWidget(self.text_box, 4, 0, 1, 2)

    def create_slider(self) -> None:
        """Create a slider."""
        self.slider = QtWidgets.QSlider(Qt.Horizontal)
        self.slider.setRange(0, 10)
        self.grid_layout.addWidget(self.slider, 5, 0, 1, 1)

    def create_spin_box(self) -> None:
        """Create a spin box."""
        self.spin_box = QtWidgets.QSpinBox()
        self.spin_box.setRange(-999, 999)

        self.grid_layout.addWidget(self.spin_box, 5, 1, 1, 1)

    def create_tabbed_layout(self) -> None:
        """Create a tabbed section with a few tabs containing widgets."""
        self.tabs = QtWidgets.QTabWidget()
        self.grid_layout.addWidget(self.tabs, 0, 2, 6, 1)

        self.create_list_tab()

        self.create_tree_tab()

        self.create_table_tab()

        self.create_custom_widgets_tab()

    def create_list_tab(self) -> None:
        """Create the tab with a list widget."""
        name = 'List'
        items = 15
        self.tab_one_widget = QtWidgets.QWidget()
        self.tab_one_layout = QtWidgets.QVBoxLayout()
        self.tab_one_widget.setLayout(self.tab_one_layout)

        self.list_title = QtWidgets.QLabel(name)
        self.tab_one_layout.addWidget(self.list_title)

        self.list = QtWidgets.QListWidget()
        self.tab_one_layout.addWidget(self.list)

        self.list.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        self.list.setAlternatingRowColors(True)

        for i in range(1, items + 1):
            self.list.addItem(f'List Item {i}')

        self.tabs.addTab(self.tab_one_widget, name)

    def create_tree_tab(self) -> None:
        """Create the tab with a tree widget."""
        name = 'Tree'
        columns = 2
        items = 15
        headers = []

        self.tab_two_widget = QtWidgets.QWidget()
        self.tab_two_layout = QtWidgets.QVBoxLayout()
        self.tab_two_widget.setLayout(self.tab_two_layout)

        self.tree_title = QtWidgets.QLabel(name)
        self.tab_two_layout.addWidget(self.tree_title)

        self.tree = QtWidgets.QTreeWidget()
        self.tab_two_layout.addWidget(self.tree)

        self.tree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tree.setAlternatingRowColors(True)

        self.tree.setColumnCount(columns)
        for column in range(columns):
            headers.append(f'Header {column + 1}')

        self.tree.setHeaderLabels(headers)

        for i in range(items):
            item = QtWidgets.QTreeWidgetItem([f'Tree Item {i + 1}', ''])
            self.tree.addTopLevelItem(item)
            subItem = QtWidgets.QTreeWidgetItem(['', f'Sub-Item {i + 1}'])
            item.addChild(subItem)

        self.tabs.addTab(self.tab_two_widget, name)

    def create_table_tab(self) -> None:
        """Create the tab with a table widget."""
        name = 'Table'
        rows = 10
        columns = 10
        headers = []

        self.tab_three_widget = QtWidgets.QWidget()
        self.tab_three_layout = QtWidgets.QVBoxLayout()
        self.tab_three_widget.setLayout(self.tab_three_layout)

        self.table_title = QtWidgets.QLabel(name)
        self.tab_three_layout.addWidget(self.table_title)

        self.table = QtWidgets.QTableWidget()
        self.tab_three_layout.addWidget(self.table)

        self.table.setRowCount(rows)
        self.table.setColumnCount(columns)
        self.table.setSortingEnabled(True)
        self.table.resizeColumnToContents(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)

        for column in range(columns):
            headers.append(f'Header {column + 1}')

        self.table.setHorizontalHeaderLabels(headers)

        for r in range(rows):
            for c in range(columns):
                item = QtWidgets.QTableWidgetItem(f'Row {r} Col {c}')
                self.table.setItem(r, c, item)

        self.table.resizeColumnsToContents()

        self.tabs.addTab(self.tab_three_widget, name)

    def create_custom_widgets_tab(self) -> None:
        """Create the tab with the custom widgets."""
        name = 'Custom'

        self.tab_four_widget = QtWidgets.QWidget()
        self.tab_four_layout = QtWidgets.QVBoxLayout()
        self.tab_four_widget.setLayout(self.tab_four_layout)

        self.circle_slider = switch.Switch()
        self.tab_four_layout.addWidget(self.circle_slider)

        self.square_slider = switch.Switch(type='square')
        self.tab_four_layout.addWidget(self.square_slider)

        self.tabs.addTab(self.tab_four_widget, name)

    def create_line(self) -> None:
        """Create a horizontal line."""
        self.h_line = QtWidgets.QFrame()
        self.h_line.setObjectName('line')
        self.h_line.setFrameShape(QtWidgets.QFrame.HLine)
        self.h_line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.main_layout.addWidget(self.h_line)

    def create_progress_bar(self) -> None:
        """Create a progress bar."""
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(1, 10)
        self.progress_bar.setValue(7)
        self.progress_bar.setMaximumHeight(8)

        self.bottom_layout.addWidget(self.progress_bar)

    def create_buttons(self) -> None:
        """Create the buttons."""
        self.bottom_layout.addStretch(1)

        self.dialog_button = QtWidgets.QPushButton('Create Dialog')
        self.dialog_button.clicked.connect(self.create_dialog)
        self.bottom_layout.addWidget(self.dialog_button)

        self.error_dialog_button = QtWidgets.QPushButton('Create Error Dialog')
        self.error_dialog_button.clicked.connect(self.create_error_dialog)
        self.bottom_layout.addWidget(self.error_dialog_button)

        self.file_dialog_button = QtWidgets.QPushButton('Open File Dialog')
        self.file_dialog_button.clicked.connect(self.open_file_dialog)
        self.bottom_layout.addWidget(self.file_dialog_button)

        self.close_button = QtWidgets.QPushButton('Close')
        self.bottom_layout.addWidget(self.close_button)

    def create_dialog(self) -> None:
        """Create a dialog."""
        self.dialog = dialogs.NDialog(
            parent=self, title='Info', message='This is an info dialog.'
        )
        self.dialog.show()

    def create_error_dialog(self) -> None:
        """Create an error dialog."""
        self.dialog = dialogs.NErrorDialog(
            parent=self,
            title='Error',
            message='Don\'t do that again.',
            failure_message=(
                'This would be where you put your traceback or other message.'
            ),
        )
        self.dialog.show()

    def open_file_dialog(self) -> QtWidgets.QFileDialog:
        """Create a file dialog.

        Returns:
            dialog (QtWidgets.QFileDialog): File dialog.
        """
        dialog = QtWidgets.QFileDialog.getOpenFileName(
            parent=self,
            caption='File Dialog',
            options=QtWidgets.QFileDialog.DontUseNativeDialog,
        )
        return dialog


def create_example(
    default: Optional[bool] = False,
    from_file: Optional[bool] = False,
    style: Optional[str] = 'default',
    palette: Optional[str] = 'default',
) -> nori.Nori:
    """Create the example widget.

    Args:
        default (bool): Whether or not to show the example widget within a
            Nori Window.
            Default is False (use the Nori Window).
        from_file (bool): Whether or not to load the central widget from a
            file or use the notmal example.
            Default is False (use the normal example).
        style (str): The name of the stylesheet to use.
            If nothing is provided, a default is used.
            'none' can also be provided to not apply any styling.
                In the case of a child window, it will inherit the parents
                style and palette.
        palette (str): The name of the palette to use.
            If none is provided, a default is used.

    Returns:
        mw (Nori): Nori window.
    """
    cw = ExampleUI()

    dock_widget = QtWidgets.QDockWidget('Dock Panel')
    dock_widget_label = QtWidgets.QLabel('Dock Stuff')
    dock_widget.setWidget(dock_widget_label)

    dock_widget2 = QtWidgets.QDockWidget('Dock Panel 2')
    dock_widget_label2 = QtWidgets.QLabel('More Dock Stuff')
    dock_widget2.setWidget(dock_widget_label2)

    if default:
        mw = QtWidgets.QMainWindow()
        mw.setWindowTitle('Default Example UI')
        mw.setCentralWidget(cw)
        mw.addDockWidget(Qt.RightDockWidgetArea, dock_widget)
        mw.addDockWidget(Qt.RightDockWidgetArea, dock_widget2)
        mw.tabifyDockWidget(dock_widget, dock_widget2)
        dock_widget.raise_()

    elif from_file:
        widget_file = os.path.join(os.path.dirname(__file__), 'widget_file.ui')

        mw = nori.Nori(
            central_widget=widget_file,
            title='Example UI From File',
            as_popup=False,
            center=True,
        )

    else:
        mw = nori.Nori(
            central_widget=cw, title='Example UI', as_popup=False, center=True
        )

        mw.add_dock_panel(
            widget=dock_widget_label, position='right', title='Dock Panel'
        )

        mw.add_dock_panel(
            widget=dock_widget_label2, position='right', title='Dock Panel 2'
        )

    cw.close_button.clicked.connect(mw.close)

    utils.move_to_center(mw)

    return mw
