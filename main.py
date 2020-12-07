import sys
import pandas as pd
import matplotlib.pyplot  as plt
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import date, datetime, timedelta
import time, os
import decimal


def float_range(start, stop, step):
    while start < stop:
        yield float(start)
        start += decimal.Decimal(step)


class mainApplication(QWidget):

    def __init__(self, parent=None):
        super(mainApplication, self).__init__(parent)

        self.car_files_txt = ""
        self.layoutMap = {}
        self.buttonMap = {}

        # Figure Bottom Left
        self.leftFigure = plt.figure(figsize=(15, 5))
        self.leftFigure.set_facecolor('0.915')
        self.leftComboBox = QComboBox()
        self.leftCanvas = FigureCanvas(self.leftFigure)

        # Figure Bottom Right
        self.rightFigure = plt.figure(figsize=(15, 5))
        self.rightFigure.set_facecolor('0.915')
        self.rightCanvas = FigureCanvas(self.rightFigure)

        # Main Figure
        #        self.setGeometry(600, 300, 1000, 600)

        self.topLeft()
        self.topRight()
        self.bottomLeft()
        self.bottomRight()

        self.mainLayout = QGridLayout()
        self.mainLayout.addWidget(self.topLeftBox, 1, 0)
        self.mainLayout.addWidget(self.topRightBox, 1, 1)
        self.mainLayout.addWidget(self.bottomLeftBox, 2, 0)
        self.mainLayout.addWidget(self.bottomRightBox, 2, 1)
        self.mainLayout.setRowStretch(1, 1)
        self.mainLayout.setRowStretch(2, 1)
        self.mainLayout.setColumnStretch(0, 1)
        self.mainLayout.setColumnStretch(1, 1)
        self.saveLayout(self.mainLayout, "main")

        self.setLayout(self.mainLayout)

        self.setWindowTitle("Title")
        QApplication.setStyle("Fusion")

    #        self.show()

    def bottomLeft(self):
        self.bottomLeftBox = QGroupBox("First Graph")

        # Create Full Screen Button
        self.leftFullScreenButton = QPushButton("Full Screen")
        self.leftFullScreenButton.setMaximumWidth(100)
        self.leftFullScreenButton.setMaximumHeight(20)
        self.saveButton(self.leftFullScreenButton)
        self.leftFullScreenButton.clicked.connect(self.swichFullScreenLeft)

        # Create Layout
        leftLayout = QVBoxLayout()
        formLayout = QFormLayout()
        formLayout.addRow('Car', QComboBox())
        leftLayout.addLayout(formLayout)
        leftLayout.addWidget(self.leftCanvas)
        # layout.addWidget(chooseButton)
        leftLayout.addWidget(self.leftFullScreenButton)
        leftLayout.addStretch(1)

        self.saveLayout(leftLayout, "full")

        # Add Layout to GroupBox
        self.bottomLeftBox.setLayout(leftLayout)

    def bottomRight(self):
        self.bottomRightBox = QGroupBox("Second Graph")

        # Create Select Button
        # chooseButton = QPushButton("Select")
        # chooseButton.setMaximumWidth(100)
        # chooseButton.setMaximumHeight(20)
        # self.saveButton(chooseButton)
        # chooseButton.clicked.connect(self.selectFunction)

        # Create Full Screen Button
        self.rightFullScreenButton = QPushButton("Full Screen")
        self.rightFullScreenButton.setMaximumWidth(100)
        self.rightFullScreenButton.setMaximumHeight(20)
        self.saveButton(self.rightFullScreenButton)
        self.rightFullScreenButton.clicked.connect(self.swichFullScreenRight)

        # Create Layout
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.rightCanvas)
        # rightLayout.addWidget(chooseButton)
        rightLayout.addWidget(self.rightFullScreenButton)
        rightLayout.addStretch(1)

        self.saveLayout(rightLayout, "full")

        # Add Layout to GroupBox
        self.bottomRightBox.setLayout(rightLayout)

    def selectFunction(self):
        # Select Data
        filePath, _ = QFileDialog.getOpenFileName(self, 'Open file', '/Data/')
        df = pd.read_csv(str(filePath))
        x = df.x.tolist()
        y = df.y.tolist()

        # Create Figure
        self.figure.clf()
        ax = self.figure.add_subplot(111)
        ax.plot(x, y)
        ax.set_facecolor('0.915')
        ax.set_title('Graphique')

        # Draw Graph
        self.canvas.draw()

    def saveLayout(self, obj, text):
        self.layoutMap[text] = obj

    def findLayout(self, text):
        return self.layoutMap[text]

    def saveButton(self, obj):
        self.buttonMap[obj.text()] = obj

    def findButton(self, text):
        return self.buttonMap[text]

    def swichFullScreenLeft(self):
        if self.sender().text() == "Full Screen":
            self.topLeftBox.hide()
            self.topRightBox.hide()
            self.bottomLeftBox.hide()
            self.bottomRightBox.hide()
            self.mainLayout.addWidget(self.bottomLeftBox, 0, 0, 1, 2)
            self.bottomLeftBox.show()
            self.leftFullScreenButton.setText("Exit Full Screen")

        else:
            self.bottomLeftBox.hide()
            self.topLeftBox.show()
            self.topRightBox.show()
            self.bottomRightBox.show()
            self.mainLayout.addWidget(self.bottomLeftBox, 2, 0)
            self.bottomLeftBox.show()
            self.leftFullScreenButton.setText("Full Screen")

    def swichFullScreenRight(self):
        if self.sender().text() == "Full Screen":
            self.topLeftBox.hide()
            self.topRightBox.hide()
            self.bottomLeftBox.hide()
            self.bottomRightBox.hide()
            self.mainLayout.addWidget(self.bottomRightBox, 0, 0, 1, 2)
            self.bottomRightBox.show()
            self.rightFullScreenButton.setText("Exit Full Screen")

        else:
            self.bottomRightBox.hide()
            self.topLeftBox.show()
            self.topRightBox.show()
            self.bottomLeftBox.show()
            self.mainLayout.addWidget(self.bottomRightBox, 2, 1)
            self.bottomRightBox.show()
            self.rightFullScreenButton.setText("Full Screen")

    def topLeft(self):
        self.time_range_cb = QComboBox()
        self.time_range_cb.addItems([("%s%d:%02d" % ("-" if x < 0 else "+", int(abs(x)), (abs(x) * 60) % 60)) for x in
                                     list(float_range(-12, 13, '0.5'))])

        self.open_file_dialog_btn = QPushButton('Set Path', self)
        self.open_file_dialog_btn.clicked.connect(self.open_file_dialog_btn_click)

        self.open_car_file_dialog_btn = QPushButton('Load Car Files', self)
        self.open_car_file_dialog_btn.clicked.connect(self.open_car_file_dialog_btn_click)

        self.topLeftBox = QGroupBox()
        leftLayout = QVBoxLayout()
        formLayout = QFormLayout()
        formLayout.addRow('Time Gap:', self.time_range_cb)
        formLayout.addRow('Directory Path:', self.open_file_dialog_btn)
        formLayout.addRow('Select Car Files:', self.open_car_file_dialog_btn)
        leftLayout.addLayout(formLayout)
        buttons = QDialogButtonBox()
        buttons.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        leftLayout.addWidget(buttons)
        self.topLeftBox.setLayout(leftLayout)

    def topRight(self):
        self.topRightBox = QTextEdit("")

    def open_file_dialog_btn_click(self):
        path = QFileDialog.getExistingDirectory(None, 'Select Directory for files')
        self.directory_path.setText(path)
        self.write_to_saved_data(path)

    def open_car_file_dialog_btn_click(self):
        files = QFileDialog.getOpenFileNames(None, 'Select CAR files', "", "CAR files (*.car *.CAR)")
        self.car_files = files[0]
        self.car_files_txt.setText("\n".join([x.split("/")[-1] for x in self.car_files]))

    @staticmethod
    def read_from_saved_data():
        data_file = open("saved_data.txt", "r")
        for x in data_file:
            if "PATH:" in x:
                return x.split("PATH:", 1)[1]

    @staticmethod
    def write_to_saved_data(path):
        data_file = open("saved_data.txt", "w")
        data_file.write("PATH:" + path)
        data_file.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = mainApplication()
    mainWindow.setGeometry(200, 100, 1000, 600)
    mainWindow.show()
    sys.exit(app.exec_())
