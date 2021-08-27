"""Switch Widget."""

from PyQt5 import QtCore, QtWidgets

from utils import LOG


class Switch(QtWidgets.QSlider):
    """Custom Switch widget based on a QSlider."""

    VALID_SWITCH_TYPES = ['round', 'square']

    def __init__(self, type=None):
        """Init.

        Args:
            parent (QObject): The parent object.
            type (str): The type of switch.
                Can either be 'round' (default) or 'square'.

        Returns:
            None
        """
        super(Switch, self).__init__(QtCore.Qt.Horizontal)

        self.type = type
        if self.type not in self.VALID_SWITCH_TYPES:
            LOG.debug(
                'Switch type \'{}\' invalid; should be one of: {}'.format(
                    self.type, '\', \''.join(self.VALID_SWITCH_TYPES)
                )
            )
            self.type = 'round'

        self.setObjectName('{}_switch'.format(self.type))
        self.setRange(0, 10)
        self.setMaximumWidth(60)

        self.previous_value = self.value()

        self.sliderReleased.connect(self.on_slider_change)

    def on_slider_change(self):
        """Change the slider position based on the interaction.

        If the slider is clicked on, snap the slider to the opposite side.
        If the slider is moved, snap the slider to the nearest edge.
        """
        current_value = self.value()
        max = self.maximum()
        min = self.minimum()
        half = (max - min) / 2
        has_changed = current_value != self.previous_value

        if current_value == min and not has_changed:
            new_value = max

        elif current_value == min and has_changed:
            new_value = min

        elif current_value == max and not has_changed:
            new_value = min

        elif current_value == max and has_changed:
            new_value = max

        elif current_value <= half:
            new_value = min

        else:
            new_value = max

        self.setValue(new_value)
        self.setSliderPosition(new_value)
        self.previous_value = new_value

    def get_state(self):
        """Return the state of the switch.

        The switch can only be at maximum or minimum values.

        Args:
            None

        Returns:
            state (bool): True if the switch is "on" (at maximum value),
                otherwise False (at minimum value).
        """
        if self.value() == self.maximum():
            state = True
        else:
            state = False

        return state
