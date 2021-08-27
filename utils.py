"""Utilities for the base window UI."""

import os

from PyQt5 import QtGui, QtCore, QtWidgets

from setup import LOCAL_PATH, LOG, CONFIG

DEFAULT_STYLE = 'default'
DEFAULT_PALETTE = 'default'


def get_application_window():
    """Get the top level window for the current application.

    Returns:
        (QObject): The main window of the application.
    """
    return QtWidgets.QApplication.activeWindow()


def get_app_instance():
    """Get the application instance if one exists.

    Args:
        None

    Returns:
        app (QApplication): The application instance or None
    """
    return QtWidgets.QApplication.instance()


def create_app_instance():
    """Create an app instance.

    Args:
        None

    Returns:
        (QApplication): The application instance.
    """
    instance = get_app_instance()
    if not instance:
        return QtWidgets.QApplication([])
    else:
        return instance


def get_icons_path():
    """Return the directory containing the icons.

    Args:
        None

    Returns:
        icons_path (str): Path to the icons folder.
    """
    return os.path.join(
        os.path.dirname(__file__), CONFIG['icons_location']
    )


def get_styles_path():
    """Return the directory containing the styles.

    Args:
        None

    Returns:
        styles_path (str): Path to the styles folder.
    """
    return os.path.join(
        os.path.dirname(__file__), CONFIG['styles_location']
    )


def get_palettes_path():
    """Return the directory containing the palettes.

    Args:
        None

    Returns:
        palettes_path (str): Path to the palettes folder.
    """
    return os.path.join(
        get_styles_path(), CONFIG['palettes_location']
    )


def get_style(style):
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
        style_file = os.path.join(styles_path, style + '.qss')
        if not os.path.exists(style_file):
            LOG.debug(
                'No stylesheet exists at: {}; using default'.format(style_file)
            )
            style_file = os.path.join(styles_path, DEFAULT_STYLE)

    with open(style_file, 'r') as inFile:
        style = inFile.read()

    return style


def get_palette(palette):
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
        palette_file = os.path.join(
            palettes_path, palette + '.palette'
        )
        if not os.path.exists(palette_file):
            LOG.debug(
                'No palette exists at: {}; using default'.format(palette_file))
            palette_file = os.path.join(palettes_path, DEFAULT_PALETTE)

    with open(palette_file, 'r') as inFile:
        palettes = inFile.readlines()

    palettes.sort(key=len, reverse=True)

    return palettes


def get_stylesheet(style="", palette=""):
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


def get_package_config():
    """Return the package config.

    Args:
        None

    Returns:
        (dict): The package config.
    """
    return CONFIG


def find_fonts(font_folder=None, families=None):
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
        LOG.info("No font folder given, using package fonts.")
        return load_local_fonts(families)

    if not os.path.exists(font_folder):
        LOG.error("Font folder does not exist: {}".format(font_folder))
        return None

    if not os.path.isdir(font_folder):
        LOG.error("Font folder path is not a folder: {}".format(font_folder))
        return None

    for font in os.listdir(font_folder):
        if os.path.splitext(font)[1] not in CONFIG["font_types"]:
            continue

        if families:
            for family in families:
                if family.lower() in font.lower():
                    fonts_to_load.append(font)
        else:
            fonts_to_load.append(font)

    return fonts_to_load


def load_local_fonts(families=None):
    """Load local fonts.

    If no families are given, look for all valid fonts.

    Args:
        families (list): List of font names.

    Returns:
        fonts_to_load (list): A list of the font files to load.
    """
    fonts_to_load = []

    font_folder = os.path.join(
        LOCAL_PATH, CONFIG['fonts_location']
    )

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


def load_custom_fonts(font_folder=None, families=None):
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
    fonts_to_load = find_fonts()

    for font in fonts_to_load:
        font_id = load_custom_font(os.path.abspath(font))
        if font_id:
            font_ids.append(font_id)

    return font_ids


def load_custom_font(font_file):
    """Load a custom font from a file.

    This adds the font to the QFontDatabase to be used later.

    Args:
        font_file (str): Path to a font file.

    Returns:
        font_id (int): The id of the font.
    """
    if not os.path.exists(font_file):
        LOG.error("Font file does not exist: {}".format(font_file))
        return None

    if os.path.splitext(font_file)[1] not in CONFIG["font_types"]:
        LOG.error(
            "Font file is not an approved file type: {}".format(font_file)
        )
        LOG.error(
            "Approved types are: {}".format(CONFIG["font_types"])
        )
        return None

    font_db = QtGui.QFontDatabase()
    font_id = font_db.addApplicationFont(font_file)

    return font_id


def move_to_center(window):
    """Move the window to the center of the screen.

    Args:
        window (QMainWindow or any QWidget): Any object that inherits QWidget

    Returns:
        None
    """
    screen_center = calculate_center()
    window_center = QtCore.QPoint(window.width() / 2, window.height() / 2)
    LOG.debug("window_center: {}".format(window_center))
    LOG.debug("window_x: {}".format(screen_center.x() - window_center.x()))
    LOG.debug("window_y: {}".format(screen_center.y() - window_center.y()))

    window.move(
        screen_center.x() - window_center.x(),
        screen_center.y() - window_center.y()
    )


def calculate_center():
    """Calculate the center point of the active monitor.

    Args:
        None

    Returns:
        center (QPoint): (center x position, center y position)
    """
    app = QtWidgets.QApplication.instance()

    if not app:
        raise RuntimeError('No currently running QApplication.')

    screen = app.desktop().screenNumber(app.desktop().cursor().pos())
    screen_resolution = app.desktop().screenGeometry(screen)
    LOG.debug("screen_resolution: {}".format(screen_resolution))

    screen_center = QtCore.QPoint(
        (screen_resolution.width() / 2) + screen_resolution.left(),
        (screen_resolution.height() / 2) + screen_resolution.top())

    LOG.debug("screen_center: {}".format(screen_center))

    return screen_center


def find_icon(icon_name):
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
        LOG.error("Unable to find icon: {}".format(icon_name))
        return None

    return icon_path


def get_pixmap(icon_name):
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


def get_icon(icon_name):
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


def load_widget_from_file(path):
    """Load a widget from a .ui file.

    Args:
        path (str): Path to the .ui file.

    Returns:
        widget (QWidget) or None: The widget built from the file.
            If the file can't be loaded, returns None.
    """
    from PyQt5.QtUiTools import QUiLoader

    # Attempt to load the file
    ui_file = QtCore.QFile(path)
    is_open = ui_file.open(QtCore.QFile.ReadOnly)
    if not is_open:
        LOG.error('Widget file cannot be loaded: {}'.format(path))
        return None

    LOG.debug('Loading widget from file: {}'.format(path))
    widget = QUiLoader().load(ui_file)
    ui_file.close()

    return widget
