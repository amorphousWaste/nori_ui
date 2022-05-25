"""Unified Window Class."""

import webbrowser

from PySide6 import QtCore, QtGui, QtWidgets
from typing import Callable, Optional

import utils

from log import LOG


class Nori(QtWidgets.QMainWindow):
    """The main window for applications."""

    DEFAULT_ICON = 'defaultIcon.png'
    DEFAULT_TITLE = 'Nori'

    PACKAGE_CONFIG = utils.get_package_config()

    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        central_widget: Optional[QtWidgets.QWidget] = None,
        icon: Optional[str] = None,
        title: Optional[str] = None,
        show_status_bar: Optional[bool] = None,
        as_popup: Optional[bool] = None,
        center: Optional[bool] = None,
        style: Optional[str] = None,
        palette: Optional[str] = None,
        on_open: Optional[Callable] = None,
        on_close: Optional[Callable] = None,
        refresh: Optional[Callable] = None,
        help_link: Optional[str] = None,
        fonts: Optional[list[str]] = None,
    ) -> None:
        """Initialize the window.

        Args:
            parent (QObject): The parent application, window, widget, etc.
            central_widget (QWidget or .ui file path):
                The widget to set as the central widget.
                If using a .ui file path, provide a string. The .ui file should
                load a QWidget, not a window.
            icon (str): The name of the icon to set for the window.
            title (str): The title of the window.
            show_status_bar (bool): Whether or not to show the status bar.
                If False, messages sent to the status bar will be ignored.
            as_popup (bool): Whether of not to make this window a popup.
                As a popup, the window becomes modal and will not have a menu
                bar or status bar.
            center (bool): Whether or not to center the window.
            style (str): The name of the stylesheet to use.
                If nothing is provided, a default is used.
                'none' can also be provided to not apply any styling.
                    In the case of a child window, it will inherit the parents
                    style and palette.
            palette (str): The name of the palette to use.
                If none is provided, a default is used.
            on_open (function): Function to run when the window opens.
            on_close (function): Function to run when the window closes.
            refresh (function): Function to run when "File" -> "Refresh" is
                clicked. If nothing is provided, the "Refresh" item is not
                created.
            help_link (str): The URL of the Confluence page for the
                application.
            fonts (list): List of font families to load.
        """
        super(Nori, self).__init__(parent)

        self.parent = parent
        self.central_widget = central_widget
        self.icon = icon or self.DEFAULT_ICON
        self.title = title or self.DEFAULT_TITLE
        self.show_status_bar = show_status_bar or False
        self.as_popup = as_popup or False
        self.center = center or False
        self.style = style or utils.DEFAULT_STYLE
        self.palette = palette or utils.DEFAULT_PALETTE
        self.on_open = on_open
        self.on_close = on_close
        self.refresh = refresh
        self.help_link = help_link or self.PACKAGE_CONFIG['nori_github_page']
        self.fonts = fonts or []

        self.app = utils.get_app_instance()

        # This stores the docked widgets
        self.docked_widgets = {
            'top': {
                'area': QtCore.Qt.TopDockWidgetArea,
                'widgets': [],
            },
            'right': {
                'area': QtCore.Qt.RightDockWidgetArea,
                'widgets': [],
            },
            'bottom': {
                'area': QtCore.Qt.BottomDockWidgetArea,
                'widgets': [],
            },
            'left': {
                'area': QtCore.Qt.LeftDockWidgetArea,
                'widgets': [],
            },
        }

        if not self.parent:
            self.parent = utils.get_application_window()

        self.setWindowTitle(self.title)
        self.set_window_icon()
        self.stylesheet = self._setStyleSheet()

        self._set_central_widget()

        if self.show_status_bar:
            self.statusBar().show()

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        if not self.as_popup:
            self.add_menu_bar()
            self.add_file_menu()

        else:
            self.setWindowFlags(
                self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint
            )
            self.setWindowModality(QtCore.Qt.ApplicationModal)

        if self.fonts:
            self.load_fonts()

        if self.center:
            utils.move_to_center(self)

        # Set dock options
        self.setDockOptions(
            QtWidgets.QMainWindow.AnimatedDocks
            | QtWidgets.QMainWindow.AllowNestedDocks
            | QtWidgets.QMainWindow.AllowTabbedDocks
        )

    def set_window_icon(self) -> None:
        """Set the window icon."""
        window_icon = utils.get_icon(self.icon) or utils.get_icon(
            self.DEFAULT_ICON
        )
        self.setWindowIcon(window_icon)

    def keyPressEvent(self, event: QtCore.QEvent) -> None:
        """Check for certain keys being pressed and act on them.

        Override of built in keyPressEvent.
        """
        # Press escape to close the window
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

        # These prevent Maya from stealing focus when Shift or Ctrl are pressed
        if event.modifiers() and QtCore.Qt.ShiftModifier:
            self.shift = True

        if event.modifiers() and QtCore.Qt.ControlModifier:
            self.control = True

    def _setStyleSheet(self) -> None:
        """Set the window stylesheet."""
        # If the style given in 'none', don't apply any styling
        if self.style == 'none':
            return ''

        style = utils.get_stylesheet(self.style, self.palette)
        self.setStyleSheet(style)
        return style

    def _set_central_widget(self) -> None:
        """Set the central widget."""
        if isinstance(self.central_widget, str):
            self.central_widget = utils.load_widget_from_file(
                self.central_widget
            )

        if not self.central_widget:
            return

        LOG.debug(f'Setting central_widget: {self.central_widget}')
        self.setCentralWidget(self.central_widget)

    def add_dock_panel(
        self,
        widget: QtWidgets.QWidget = None,
        position: str = None,
        title: str = None,
        floating: bool = None,
    ) -> None:
        """Add a dockable panel to the main window.

        Args:
            widget (QWidget): Any object that inherits QWidget.
            position (str): Position for the docked widget.
                Can be 'top', 'right', 'bottom', or 'left'.
                Default is 'right'.
            title (str): The title of the dock.
            floating (bool): Whether the widget is floating.
        """
        floating = True if floating else False
        position = position or 'right'
        title = title or "{}_{}".format(
            position, len(self.docked_widgets[position]['widgets'])
        )

        dock_widget = QtWidgets.QDockWidget(title)
        if widget:
            dock_widget.setWidget(widget)

        # Add the dock widget
        self.addDockWidget(self.docked_widgets[position]['area'], dock_widget)

        # If any widgets are already docked in this position, add the new one
        # as a tabbed dock undernieth the existing ones
        if self.docked_widgets[position]['widgets']:
            self.tabifyDockWidget(
                self.docked_widgets[position]['widgets'][-1], dock_widget
            )

        # Add the widget to the list of docked widgets
        self.docked_widgets[position]['widgets'].append(dock_widget)

        # Keep the first widget on top
        self.docked_widgets[position]['widgets'][0].raise_()

        dock_widget.setFloating(floating)

    def remove_dock_panel(self, title: str) -> bool:
        """Remove a dockable panel based on name.

        Args:
            title (str): Name of the panel to remove.

        Returns:
            (bool): Whether or not the panel was successfully removed.
        """
        # Find the dock from the name
        for position in self.docked_widgets:
            for widget in self.docked_widgets[position]['widgets']:
                if title == widget.title():
                    self.removeWidget(widget)
                    widget.deleteLater()

                self.docked_widgets[position]['widgets'].remove(widget)
                LOG.debug(f'Removed panel: {title}')
                return True

        # This will run if nothing is found
        LOG.error(
            f'Panel \"{title}\" could not be deleted because it could not be '
            'found.'
        )
        return False

    def add_menu_bar(self) -> None:
        """Add a menu bar to the window."""
        self.menu_bar = QtWidgets.QMenuBar()
        self.setMenuBar(self.menu_bar)

    def add_file_menu(self):
        """Add the default File menu and associated actions."""
        actions = []

        actions.append(self.create_help_action())
        if self.refresh:
            actions.append('separator')
            actions.append(self.create_refresh_action())

        actions.append('separator')
        actions.append(self.create_close_action())

        self.file_menu = self.add_menu('&File', actions)

    def get_menus(self) -> list[QtGui.QAction]:
        """Get all the menus in the menu bar.

        Returns:
            menu_items (list): A list of menus.
        """
        menu_items = [
            i
            for i in self.menu_bar.children()
            if isinstance(i, QtWidgets.QMenu)
        ]

        return menu_items

    def add_menu(
        self, name: str, actions: Optional[list] = []
    ) -> QtWidgets.QMenu:
        """Add a menu to the given parent.

        Args:
            name (str): Name of the menu to add.
            actions (list): List of actions to add.

        Returns:
            menu (QMenu): The created menu with its actions
        """
        if self.as_popup:
            LOG.error('Cannot add menus in popup mode.')
            return

        if name in [m.title() for m in self.get_menus()]:
            LOG.warning('Menu already exists.')

        menu = self.menu_bar.addMenu(name)

        self.add_menu_actions(menu, actions)

    def add_menu_actions(
        self, menu: QtWidgets.QMenu, actions: Optional[list] = []
    ) -> None:
        """Add menu actions to the given menu.

        Args:
            menu (QMenu): The menu to add an action to.
            actions (list): A list of QActions or 'seperators'.
        """
        for action in actions:
            if action == 'separator':
                menu.addSeparator()
                continue

            menu.addAction(action)

    def create_refresh_action(self) -> QtGui.QAction:
        """Create the refresh menu action.

        Returns:
            action (QAction): The refresh action.
        """
        icon = utils.get_icon('outline-refresh-white.png')
        action = QtGui.QAction(icon, 'Refresh', self)
        action.setShortcut('Ctrl+R')
        action.triggered.connect(self.refresh)

        return action

    def create_help_action(self) -> QtGui.QAction:
        """Create the help menu action.

        Returns:
            action (QAction): The help action.
        """
        icon = utils.get_icon('cloud-question.png')
        action = QtGui.QAction(icon, 'Help', self)
        action.triggered.connect(self.get_help)

        return action

    def create_close_action(self) -> QtGui.QAction:
        """Create the close menu action.

        Returns:
            action (QAction): The close action.
        """
        icon = utils.get_icon('close-box-outline.png')
        action = QtGui.QAction(icon, 'Close', self)
        action.setShortcut('Ctrl+Q')
        action.triggered.connect(self.close)

        return action

    def get_help(self) -> None:
        """Open a browser window to the help page."""
        webbrowser.open(self.help_link, new=0, autoraise=True)

    def remove_menu(self, name: str) -> None:
        """Remove a menu from the window.

        Args:
            name (str): Menu name to remove.
        """
        if self.as_popup:
            LOG.error('Cannot remove menus in popup mode.')
            return

        if name in self.PACKAGE_CONFIG['locked_menus']:
            LOG.error('Cannot delete {}.'.format(name))

    def display_status_message(
        self, message: str, status: Optional[str] = ''
    ) -> bool:
        """Display a message in the status bar.

        Possible statuses:
        default: No background color
        success: Green background
        warning: Yellow background
        error: Red background

        Args:
            message (str): Message to display.
            status (str): Status of the message bar (used for coloring).

        Returns:
            result (bool): Whether or not the message was successfully
                displayed.
        """
        if not self.show_status_bar:
            LOG.warning(
                'Message sent to status bar, but status bar is not enabled.'
            )
            return False

        if status == 'success':
            self.statusBar().setObjectName('success')
        elif status == 'warning':
            self.statusBar().setObjectName('warning')
        elif status == 'error':
            self.statusBar().setObjectName('error')
        else:
            self.statusBar().setObjectName('')

        self.statusBar().showMessage(message)

        return True

    def closeEvent(self, event: QtCore.QEvent) -> None:
        """Cleanup when the window closes.

        Args:
            event (QEvent): Event triggeting the close.
        """
        LOG.debug('Closing')
        if self.on_close:
            self.on_close

    def load_fonts(self) -> None:
        """Load any custom fonts.

        Once the font is loaded, you can set it through:
            font = QFont("FONT_FAMILY", SIZE, FLAGS)
            OBJECT.setFont(font)
        Eg.
            font = QFont("Cousine", 24)
            self.setFont(font)
        """
        for font in self.fonts:
            utils.load_custom_fonts(font)

    def __repr__(self):
        """Return the instance."""
        return self

    def __str__(self):
        """Return name of the class."""
        return f'Name: {self.title}'
