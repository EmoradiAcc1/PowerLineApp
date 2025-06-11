from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import Qt

class NoWheelComboBox(QComboBox):
    def wheelEvent(self, event):
        # Ignore wheel events to prevent accidental value changes
        event.ignore()
