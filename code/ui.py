from PyQt5 import QtCore, QtWidgets, uic

import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigCanvas,
                                                NavigationToolbar2QT as
                                                NaviBar)

mpl.use('Qt5Agg')


class MplCanvas(FigCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(self.fig)


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('main.ui', self)

        self.txt_a: QtWidgets.QDoubleSpinBox
        self.txt_m: QtWidgets.QDoubleSpinBox
        self.txt_rc0: QtWidgets.QDoubleSpinBox

        self.Button_Run: QtWidgets.QPushButton
        self.Button_Pause: QtWidgets.QPushButton
        self.Button_Redraw: QtWidgets.QPushButton

        self.canvas = MplCanvas(self)
        self.Canvas_Layout.addWidget(self.canvas)
        self.addToolBar(QtCore.Qt.TopToolBarArea, NaviBar(self.canvas, self))
