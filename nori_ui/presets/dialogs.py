"""Dialog template."""

from PySide6 import QtCore, QtWidgets
from typing import Optional

import nori
import utils


class NDialog(nori.Nori):
    """Dialog class."""

    DEFAULT_MESSAGE_ICON = 'alert-circle-outline.png'

    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        title: Optional[str] = None,
        message_icon: Optional[str] = None,
        message: Optional[str] = None,
        widget: Optional[QtWidgets.QWidget] = None,
        style: Optional[str] = None,
        palette: Optional[str] = None,
    ) -> None:
        """Create a dialog based on Nori.

        Args:
            parent (QObject): The parent object.
            title (str): The title of the dialog.
            message_icon (str): The name of the icon to use with the message.
            message (str): Message to display in the dialog.
            widget (QWidget): A custom widget to add to the dialog.
            style (str): The name of the stylesheet to use.
                If nothing is provided, a default is used.
                'none' can also be provided to not apply any styling.
                    In the case of a child window, it will inherit the parents
                    style and palette.
            palette (str): The name of the palette to use.
                If none is provided, a default is used.

        Returns:
            None
        """
        self.style = style or 'none'
        self.palette = palette

        super(NDialog, self).__init__(
            parent=parent,
            title=title,
            as_popup=True,
            style=self.style,
            palette=self.palette,
        )

        self.title = title or self.DEFAULT_TITLE
        self.message_icon = message_icon or self.DEFAULT_MESSAGE_ICON
        self.message = message or ""
        self.widget = widget

        self.create_dialog()

        self.ok_button.setFocus()

        utils.move_to_center(self)

    def create_dialog(self) -> None:
        """Create the dialog."""
        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setMinimumWidth(300)
        self.central_layout = QtWidgets.QVBoxLayout()

        message_layout = QtWidgets.QHBoxLayout()
        message_layout.addStretch(1)

        icon_label = QtWidgets.QLabel()
        icon = utils.get_pixmap(self.message_icon)
        if icon:
            icon_label.setPixmap(
                icon.scaledToWidth(64, QtCore.Qt.SmoothTransformation)
            )
            message_layout.addWidget(icon_label)

        message_label = QtWidgets.QLabel(self.message)
        message_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        message_label.setMinimumWidth(200)
        message_label.setMaximumWidth(300)
        message_label.setWordWrap(True)
        message_label.setAlignment(
            QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter
        )
        message_layout.addWidget(message_label)
        message_layout.addStretch(1)
        self.central_layout.addLayout(message_layout)

        self.custom_widget_layout = QtWidgets.QVBoxLayout()
        self.central_layout.addLayout(self.custom_widget_layout)

        if self.widget:
            self.add_dialog_widget()
        else:
            self.central_layout.addStretch(1)

        h_line = QtWidgets.QFrame()
        h_line.setObjectName('button_seperator')
        h_line.setFrameShape(QtWidgets.QFrame.HLine)
        h_line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.central_layout.addWidget(h_line)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addStretch(1)
        self.add_ok_button()
        self.central_layout.addLayout(self.button_layout)

        self.central_widget.setLayout(self.central_layout)
        self.setCentralWidget(self.central_widget)

        utils.move_to_center(self)

    def add_dialog_widget(self) -> None:
        """Add the user-defined widget to the dialog."""
        self.custom_widget_layout.addWidget(self.widget)

    def add_ok_button(self) -> None:
        """Add the 'OK' button."""
        self.ok_button = QtWidgets.QPushButton('OK', self)
        self.ok_button.setMinimumWidth(100)
        self.ok_button.clicked.connect(self.ok_button_clicked)
        self.button_layout.addWidget(self.ok_button)

    def ok_button_clicked(self) -> None:
        """Close the window when the 'OK' button is clicked."""
        self.close()


class NErrorDialog(NDialog):
    """Error dialog class."""

    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        title: Optional[str] = None,
        message: Optional[str] = None,
        failure_message: Optional[str] = None,
    ) -> None:
        """Create an error dialog based on the MDialog class."""
        super(NErrorDialog, self).__init__(
            parent=parent,
            title=title,
            message_icon='alert-octagon-outline.png',
            message=message,
        )

        self.title = title or 'Error'
        self.message = message or ''
        self.failure_message = failure_message

        self.create_error_widget()
        self.add_dialog_widget()

    def create_error_widget(self) -> None:
        """Create the error widget."""
        self.widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        self.text_box = QtWidgets.QTextEdit()
        self.text_box.setMinimumWidth(200)
        self.text_box.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.text_box.setText(self.failure_message)
        self.text_box.setReadOnly(True)
        layout.addWidget(self.text_box)

        self.widget.setLayout(layout)
