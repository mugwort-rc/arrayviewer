from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QFileDialog

from ui.arrayopendialog import Ui_ArrayOpenDialog


class ArrayOpenDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ArrayOpenDialog()
        self.ui.setupUi(self)
        self.model = QStringListModel([
            "int32",
            "int64",
            "float",
        ], self.ui.comboBoxType)
        self.ui.comboBoxType.setModel(self.model)

    @pyqtSlot()
    def on_toolButtonFilepath_clicked(self):
        filepath, ext = QFileDialog.getOpenFileName(self)
        if not filepath:
            return
        self.ui.lineEditFilepath.setText(filepath)

    @staticmethod
    def getOpenFileName(parent, *args, **kwargs):
        dialog = ArrayOpenDialog(parent)
        if dialog.exec_() != QDialog.Accepted:
            return None, (None, None), None
        filepath = dialog.ui.lineEditFilepath.text()
        width = dialog.ui.spinBoxWidth.value()
        height = dialog.ui.spinBoxHeight.value()
        fmt = dialog.ui.comboBoxType.currentText()
        return filepath, (height, width), fmt
