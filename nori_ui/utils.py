"""Utilities for the base window UI."""

import os

from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import QPoint
from typing import Optional

from init import BASE_PATH, CONFIG, PROJECT_PATH
from log import LOG

DEFAULT_STYLE = 'default'
DEFAULT_PALETTE = 'default'


def get_application_window() -> QtWidgets.QWidget:
    """Get the top level window for the current application.

    Returns:
        (QWidget): The main window of the application.
    """
    return QtWidgets.QApplication.activeWindow()


def get_app_instance() -> QtWidgets.QApplication:
    """Get the application instance if one exists.

    Returns:
        (QApplication): The application instance or None
    """
    return QtWidgets.QApplication.instance()


def create_app_instance() -> QtWidgets.QApplication:
    """Create an app instance.

    Returns:
        (QApplication): The application instance.
    """
    instance = get_app_instance()
    if not instance:
        return QtWidgets.QApplication([])
    else:
        return instance


def get_icons_path() -> str:
    """Return the directory containing the icons.

    Returns:
        icons_path (str): Path to the icons folder.
    """
    return os.path.join(PROJECT_PATH, CONFIG['icons_location'])


def get_styles_path() -> str:
    """Return the directory containing the styles.

    Returns:
        styles_path (str): Path to the styles folder.
    """
    return os.path.join(PROJECT_PATH, CONFIG['styles_location'])


def get_palettes_path() -> str:
    """Return the directory containing the palettes.

    Returns:
        palettes_path (str): Path to the palettes folder.
    """
    return os.path.join(get_styles_path(), CONFIG['palettes_location'])


def get_style(style: str) -> str:
    """Get the data from the stylesheet.

    Args:
        style (str): The path to or name of a style file.

    Returns:
        style (str): The stylesheet data.
    """
    # Check if the style argument is a path to a file
    if os.path.exists(style):
        style_file = style

    # If not, look for the style locally
    else:
        styles_path = get_styles_path()
        style_file = os.path.join(styles_path, f'{style}.qss')
        if not os.path.exists(style_file):
            LOG.debug(f'No stylesheet exists at: {style_file}; using default')
            style_file = os.path.join(styles_path, DEFAULT_STYLE)

    with open(style_file, 'r') as inFile:
        style = inFile.read()

    return style


def get_palette(palette: str) -> list[str]:
    """Get the data from the pallette.

    Args:
        palette (str): The path to or name of a palette file.

    Returns:
        palettes (list): The palette data.
    """
    # Check if the palette argument is a path to a file
    if os.path.exists(palette):
        palette_file = palette

    # If not, look for the palette locally
    else:
        palettes_path = get_palettes_path()
        palette_file = os.path.join(palettes_path, f'{palette}.palette')
        if not os.path.exists(palette_file):
            LOG.debug(f'No palette exists at: {palette_file}; using default')
            palette_file = os.path.join(palettes_path, DEFAULT_PALETTE)

    with open(palette_file, 'r') as inFile:
        palettes = inFile.readlines()

    palettes.sort(key=len, reverse=True)

    return palettes


def get_stylesheet(
    style: Optional[str] = '', palette: Optional[str] = ''
) -> str:
    """Parse the stylesheet with the palette.

    Args:
        style (str): Name of the style
        palette (str): Name of the palette

    Return:
        stylesheet (str): The stylesheet to apply to the UI
    """
    style = get_style(style)
    palettes = get_palette(palette)

    for palette in palettes:
        attribute, color = palette.split('=')
        style = style.replace(attribute, color.strip())

    stylesheet = style.replace('@icons_path', get_icons_path())

    return stylesheet


def get_package_config() -> dict:
    """Return the package config.

    Returns:
        (dict): The package config.
    """
    return CONFIG


def find_fonts(
    font_folder: Optional[str] = None, families: Optional[list[str]] = None
) -> list:
    """Find fonts based on the given folder and given families.

    If not folder is given, look for fonts locally.
    If no families are given, look for all valid fonts.

    Args:
        font_folder (str): Path to a folder containing font files.
        families (list): List of font names.

    Returns:
        fonts_to_load (list): A list of the font files to load.
    """
    fonts_to_load = []
    if not font_folder:
        LOG.info('No font folder given, using package fonts.')
        return load_local_fonts(families)

    if not os.path.exists(font_folder):
        LOG.error(f'Font folder does not exist: {font_folder}')
        return None

    if not os.path.isdir(font_folder):
        LOG.error(f'Font folder path is not a folder: {font_folder}')
        return None

    for font in os.listdir(font_folder):
        if os.path.splitext(font)[1] not in CONFIG['font_types']:
            continue

        if families:
            for family in families:
                if family.lower() in font.lower():
                    fonts_to_load.append(font)
        else:
            fonts_to_load.append(font)

    return fonts_to_load


def load_local_fonts(families: Optional[list[str]] = None) -> list:
    """Load local fonts.

    If no families are given, look for all valid fonts.

    Args:
        families (list): List of font names.

    Returns:
        fonts_to_load (list): A list of the font files to load.
    """
    fonts_to_load = []

    font_folder = os.path.join(BASE_PATH, CONFIG['fonts_location'])

    font_folders = []
    for item in os.listdir(font_folder):
        folder_path = os.path.join(font_folder, item)
        if not os.path.isdir(folder_path):
            continue

        if families:
            if item.lower() not in families.lower():
                continue

        font_folders.append(folder_path)

    for folder in font_folders:
        for font in os.listdir(folder):
            fonts_to_load.append(os.path.join(folder, font))

    return fonts_to_load


def load_custom_fonts(
    font_folder: Optional[str] = None, families: Optional[list[str]] = None
) -> list[int]:
    """Load all the custom fonts found in the given folder.

    This adds the fonts to the QFontDatabase to be used later.

    It is recommended that you load each family seperately.

    Args:
        font_folder (str): Path to a folder containing font files.
        families (list): List of font names.

    Returns:
        font_ids (list): A list of the added font ids.
    """
    font_ids = []
    fonts_to_load = find_fonts(font_folder, families)

    for font in fonts_to_load:
        font_id = load_custom_font(os.path.abspath(font))
        if font_id:
            font_ids.append(font_id)

    return font_ids


def load_custom_font(font_file: str) -> int:
    """Load a custom font from a file.

    This adds the font to the QFontDatabase to be used later.

    Args:
        font_file (str): Path to a font file.

    Returns:
        font_id (int): The id of the font.
    """
    if not os.path.exists(font_file):
        LOG.error(f'Font file does not exist: {font_file}')
        return None

    if os.path.splitext(font_file)[1] not in CONFIG['font_types']:
        LOG.error(f'Font file is not an approved file type: {font_file}')
        LOG.error('Approved types are: {}'.format(CONFIG['font_types']))
        return None

    font_db = QtGui.QFontDatabase()
    font_id = font_db.addApplicationFont(font_file)

    return font_id


def move_to_center(window: QtWidgets.QWidget) -> None:
    """Move the window to the center of the screen.

    Args:
        window (QMainWindow or any QWidget): Any object that inherits QWidget
    """
    screen_center = calculate_center()
    window_center = QPoint(window.width() / 2, window.height() / 2)
    LOG.debug('window_center: {}'.format(window_center))
    LOG.debug('window_x: {}'.format(screen_center.x() - window_center.x()))
    LOG.debug('window_y: {}'.format(screen_center.y() - window_center.y()))

    window.move(
        screen_center.x() - window_center.x(),
        screen_center.y() - window_center.y(),
    )


def calculate_center() -> QPoint:
    """Calculate the center point of the active monitor.

    Returns:
        screen_center (QPoint): (center x position, center y position)
    """
    app = QtWidgets.QApplication.instance()

    if not app:
        raise RuntimeError('No currently running QApplication.')

    screen = app.primaryScreen()
    screen_resolution = screen.availableGeometry()
    LOG.debug('screen_resolution: {}'.format(screen_resolution))

    screen_center = QPoint(
        (screen_resolution.width() / 2) + screen_resolution.left(),
        (screen_resolution.height() / 2) + screen_resolution.top(),
    )

    LOG.debug(f'screen_center: {screen_center}')

    return screen_center


def find_icon(icon_name: str) -> str:
    """Get the path for an icon if it exists based on the name.

    Args:
        icon_name (str): Name of the icon.

    Returns:
        icon_path (str) or None: Path to the icon.
    """
    # Check if a path was given
    if '/' in icon_name:
        icon_path = icon_name

    # Look for the icon locally
    else:
        icon_path = os.path.join(get_icons_path(), icon_name)

    # Ensure the icon exists
    if not os.path.exists(icon_path):
        LOG.error(f'Unable to find icon: {icon_name}')
        return None

    return icon_path


def get_pixmap(icon_name: str) -> QtGui.QPixmap:
    """Get the icon if it exists from the name as a QPixmap.

    Args:
        icon_name (str): Name of the icon.

    Returns:
        (QPixmap) or None: Icon based on the name.
    """
    icon_path = find_icon(icon_name)

    if icon_path:
        return QtGui.QPixmap(icon_path)
    else:
        return None


def get_icon(icon_name: str) -> QtGui.QIcon:
    """Get the icon if it exists from the name as a QIcon.

    Args:
        icon_name (str): Name of the icon.

    Returns:
        (QIcon) or None: Icon based on the name.
    """
    pixmap = get_pixmap(icon_name)

    if pixmap:
        return QtGui.QIcon(pixmap)
    else:
        return None


def load_widget_from_file(path: str) -> QtWidgets.QWidget:
    """Load a widget from a .ui file.

    Args:
        path (str): Path to the .ui file.

    Returns:
        widget (QWidget) or None: The widget built from the file.
            If the file can't be loaded, returns None.
    """
    from PySide6.QtUiTools import QUiLoader
    from PySide6.QtCore import QFile

    # Attempt to load the file
    ui_file = QFile(path)
    is_open = ui_file.open(QFile.ReadOnly)
    if not is_open:
        LOG.error('Widget file cannot be loaded: {}'.format(path))
        return None

    LOG.debug('Loading widget from file: {}'.format(path))
    widget = QUiLoader().load(ui_file)
    ui_file.close()

    return widget
