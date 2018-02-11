from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog

from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtGui import QPixmap

from ui.mainwindow import Ui_MainWindow

from arrayopendialog import ArrayOpenDialog
from sliderdialog import SliderDialog

from PIL import Image
from PIL.ImageQt import ImageQt
import numpy as np


class ArrayImage(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._img_gen = Image8bitGenerator()

    def setImage(self, img):
        self.original = img
        self.updatePixmap()

    def updatePixmap(self):
        self.image = ImageQt(self._img_gen(self.original))
        self.pixmap = QPixmap.fromImage(self.image)
        self.clear()
        self.addPixmap(self.pixmap)

    def setFunction(self, method):
        self._img_gen = method
        self.updatePixmap()


class ImageGenerator:
    def __call__(self, array):
        raise NotImplementedError


class Image8bitGenerator(ImageGenerator):
    def apply(self, array):
        return array

    def array_to_8bit(self, array):
        maximum = array.max()
        new_image = self.apply(array)
        if array.dtype.name.endswith("int8"):
            return np.array(new_image, dtype=np.uint8)
        return np.array(np.clip(new_image / maximum * 256, 0, 0xff), dtype=np.uint8)

    def __call__(self, array):
        return Image.fromarray(self.array_to_8bit(array))


class Image8bitBrightnessGenerator(Image8bitGenerator):
    def __init__(self, x):
        self.x = x

    def apply(self, array):
        return array * self.x


class BindWheelEvent:
    def __init__(self, view1, view2):
        self.view1 = view1
        self.view2 = view2

    def bind(self):
        self.bindHorizontal(self.view1, self.view2)
        self.bindVertical(self.view1, self.view2)

    def unbind(self):
        self.unbindHorizontal(self.view1, self.view2)
        self.unbindVertical(self.view1, self.view2)

    def bindHorizontal(self, view1, view2):
        bar1 = view1.horizontalScrollBar()
        bar2 = view2.horizontalScrollBar()
        self.bindScrollBar(bar1, bar2)

    def bindVertical(self, view1, view2):
        bar1 = view1.verticalScrollBar()
        bar2 = view2.verticalScrollBar()
        self.bindScrollBar(bar1, bar2)

    def bindScrollBar(self, bar1, bar2):
        bar1.valueChanged.connect(bar2.setValue)
        bar2.valueChanged.connect(bar1.setValue)

    def unbindHorizontal(self, view1, view2):
        bar1 = view1.horizontalScrollBar()
        bar2 = view2.horizontalScrollBar()
        self.unbindScrollBar(bar1, bar2)

    def unbindVertical(self, view1, view2):
        bar1 = view1.verticalScrollBar()
        bar2 = view2.verticalScrollBar()
        self.unbindScrollBar(bar1, bar2)

    def unbindScrollBar(self, bar1, bar2):
        bar1.valueChanged.disconnect(bar2.setValue)
        bar2.valueChanged.disconnect(bar1.setValue)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.sceneOrigin = ArrayImage(self.ui.graphicsViewOrigin)
        self.scene = ArrayImage(self.ui.graphicsView)
        self.ui.graphicsViewOrigin.setScene(self.sceneOrigin)
        self.ui.graphicsView.setScene(self.scene)

        self.wheelBind = BindWheelEvent(
            self.ui.graphicsViewOrigin,
            self.ui.graphicsView,
        )
        self.wheelBind.bind()

        self.slider = SliderDialog(self)
        self.slider.valueChanged.connect(self.slider_valueChanged)

    def setImage(self, img):
        self.sceneOrigin.setImage(img)
        self.scene.setImage(img)

    @pyqtSlot()
    def on_actionOpen_triggered(self):
        filepath, shape, dtype = ArrayOpenDialog.getOpenFileName(self)
        if not filepath:
            return
        dtype = {
            "int32": "<i4",
            "int64": "<i8",
            "float": "<f8",
        }[dtype]
        img = np.fromfile(filepath, dtype=dtype)
        img.shape = shape
        self.setImage(img)

    @pyqtSlot()
    def on_actionBrightness_triggered(self):
        self.slider.show()

    @pyqtSlot(int)
    def slider_valueChanged(self, value):
        self.scene.setFunction(Image8bitBrightnessGenerator(value / 250))
