from PySide2.QtGui import QFont
from PySide2.QtCore import Slot
from PySide2.QtWidgets import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
import numpy as np
import sys
import re

allowed_words = [
    'x',
    '/',
    '+',
    '*',
    '^',
    '-'
]
replacements = {'^': '**'}

X_RANGE = (-1000, 1000)
DEFAULT_FUNCTION = "x"
DEFAULT_RANGE = (-10,10)

def convertStringToMathFunction(string):
    for word in re.findall('[a-zA-Z_]+', string):
        if word not in allowed_words:
            raise ValueError(
                f"'{word}' is Unknown expression.\nOnly functions of 'x' are allowed.\ne.g., 5*x^3 + 2/x - 1"
            )

    for str, mathFun in replacements.items():
        string = string.replace(str, mathFun)

    if "x" not in string:
        string = f"{string}+0*x"

    def func(x):
        return eval(string)

    return func

class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Master Micro")

        # Take Function From user
        self.function = QLineEdit()
        self.function.setText(DEFAULT_FUNCTION)
        self.func_label = QLabel(text="Function: ")

        # min and max values of x
        self.minValue = QDoubleSpinBox()
        self.maxValue = QDoubleSpinBox()
        self.minValue.setPrefix("Minmum Value of x: ")
        self.maxValue.setPrefix("Maxmum Value of x: ")
        self.minValue.setRange(*X_RANGE)
        self.maxValue.setRange(*X_RANGE)
        self.minValue.setValue(DEFAULT_RANGE[0])
        self.maxValue.setValue(DEFAULT_RANGE[1])

        # Plot Btn
        self.submit = QPushButton(text="plot")
        
        #  embadded plot to GUI
        self.view = FigureCanvas(Figure(figsize=(4,3)))
        self.axes = self.view.figure.subplots()

        #  layouts
        layout1 = QHBoxLayout()
        layout1.addWidget(self.func_label)
        layout1.addWidget(self.function)
        
        layout2 = QHBoxLayout()
        layout2.addWidget(self.minValue)
        layout2.addWidget(self.maxValue)

        layout3 = QHBoxLayout()
        layout3.addWidget(self.submit)

        # integrate all laouts together
        vlayout = QVBoxLayout()
        vlayout.addLayout(layout1)
        vlayout.addLayout(layout2)
        vlayout.addLayout(layout3)
        vlayout.addWidget(self.view)
        self.setLayout(vlayout)

        # Error msg
        self.error_dialog = QMessageBox()
        self.minValue.valueChanged.connect(lambda _: self.on_change(1))
        self.maxValue.valueChanged.connect(lambda _: self.on_change(2))
        self.submit.clicked.connect(lambda _: self.on_change(3))

        self.on_change(0)

    @Slot()
    def on_change(self, index):
        mn = self.minValue.value()
        mx = self.maxValue.value()
        
        if index == 1 and mn >= mx:
            self.minValue.setValue(mx-1)
            self.error_dialog.setWindowTitle("exceed 'X' Limits!")
            self.error_dialog.setText("minmum Value should be less than maxmum Value.")
            self.error_dialog.show()
            return

        if index == 2 and mx <= mn:
            self.maxValue.setValue(mn+1)
            self.error_dialog.setWindowTitle("exceed 'X' Limits!")
            self.error_dialog.setText("maxmum Value should be greater than minmum Value.")
            self.error_dialog.show()
            return

        x = np.linspace(mn, mx)
        try:
            y = convertStringToMathFunction(self.function.text())(x)
        except ValueError as e:
            self.error_dialog.setWindowTitle("Function Error!")
            self.error_dialog.setText(str(e))
            self.error_dialog.show()
            return

        self.axes.clear()
        self.axes.plot(x, y)
        self.view.draw()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    w = PlotWidget()
    w.show()
    sys.exit(app.exec_())
