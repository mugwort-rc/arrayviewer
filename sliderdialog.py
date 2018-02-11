from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QDialog

from ui.sliderdialog import Ui_SliderDialog


class SliderDialog(QDialog):

    valueChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_SliderDialog()
        self.ui.setupUi(self)
        self.ui.horizontalSlider.valueChanged.connect(self.valueChanged)
