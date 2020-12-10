import sys
import pandas as pd
import matplotlib.pyplot  as plt
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import date, datetime, timedelta
import time, os
import decimal
from unipath import Path
import itertools
import json
from io import *

LOG_FILE_PATH = "/logs/"
CONFIG_FILE_PATH = "/config/"


def float_range(start, stop, step):
    while start < stop:
        yield float(start)
        start += decimal.Decimal(step)


class MsgBox(QDialog):

    def __init__(self, *args, title="", body=""):
        super(MsgBox, self).__init__()

        self.setWindowTitle(title)
        body_txt = QLabel(body)

        buttons = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        self.layout.addWidget(body_txt)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class mainApplication(QWidget):

    def __init__(self, parent=None):
        super(mainApplication, self).__init__(parent)

        self.directory_path = None
        self.car_files_txt = None
        self.car_files = []
        self.open_file_dialog_btn = None
        self.time_range_cb = None
        self.car_data = {}
        self.related_logs = []
        self.car_combo_box = None
        self.loops_available = []

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

    # LAYOUT RELATED FUNCTIONS

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

        self.car_combo_box = QComboBox()
        self.car_combo_box.currentIndexChanged.connect(lambda: self.get_log_files(self.car_combo_box.currentText()))
        formLayout.addRow('Car', self.car_combo_box)

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
        # TODO: accepted not working. had to go with clicked. but work in both buttons. need to check
        buttons.clicked.connect(self.initiate_analysis)
        leftLayout.addWidget(buttons)
        self.topLeftBox.setLayout(leftLayout)

    def topRight(self):
        layout = QVBoxLayout()
        current_path = self.read_from_saved_data()
        self.directory_path = QLineEdit(current_path if current_path else "")
        self.directory_path.setReadOnly(True)
        self.car_files_txt = QTextEdit("")
        self.car_files_txt.setReadOnly(True)
        layout.addWidget(QLabel("Current Path"))
        layout.addWidget(self.directory_path)
        layout.addWidget(QLabel("Selected CAR Files"))
        layout.addWidget(self.car_files_txt)
        self.topRightBox = QGroupBox()
        self.topRightBox.setLayout(layout)

    # LAYOUT RELATED FUNCTIONS :: END

    # ANALYSIS RELATED FUNCTIONS

    def clear_data(self):
        """Clear data before analysis initiation"""
        self.car_data = {}
        self.related_logs = []

    def initiate_analysis(self):
        """Begin Analysis"""
        self.clear_data()
        print(self.directory_path.text())
        print(self.car_files)
        print(self.time_range_cb.currentText())
        print(self.get_time_calculated())
        # self.read_files()
        self.get_car_data()
        # update car combo box
        self.car_combo_box.addItems([""])
        self.car_combo_box.addItems([key for key, value in self.car_data.items()])
        self.car_combo_box.update()

    def get_car_data(self):
        """Get cars' serial numbers as a list"""
        for car_file_path in self.car_files:
            car_file = open(car_file_path, 'r')
            for line in car_file.readlines():
                identifier = line.split(" ", 2)[0]
                if not identifier == "0":
                    self.car_data.update({
                        identifier: line.split("\n")[0]
                    })
        if not self.car_data:
            print("No car data found")
            # TODO: this is not working
            MsgBox(self, title="Error", body="No car data found")

    def get_points_time(self, car_data, loops):
        """Calculate In and Out time for each Loop point using Available loop data and Car file data"""
        points_time = []
        time_points = len(loops) * 2
        time_samp = car_data.split(" ")[2]
        end_dt_object = self.get_time_calculated_from_timestamp(time_samp)
        start_dt_object = end_dt_object - timedelta(seconds=int(car_data.split(" ")[time_points + 2]))
        car_data_points = car_data.split(" ")[3:time_points + 3]
        start_point_time = ''
        end_point_time = ''
        end_flag = False
        initial = 0
        for loop in loops:
            for point in range(initial, (initial+2)):
                if not end_flag:
                    start_point_time = start_dt_object + timedelta(seconds=int(car_data_points[point]))
                    end_flag = True
                else:
                    end_point_time = start_dt_object + timedelta(seconds=int(car_data_points[point]))
            points_time.append({loop['loop_id']: {"in_time": start_point_time.time(), "end_time": end_point_time.time()}})
            end_flag = False
            initial += 2
        return points_time

    def get_log_files(self, car_id):
        """Find corresponding log files for given car"""
        if car_id == "":
            return
        self.related_logs = []
        loops_available = self.read_config_file()
        car_data = self.car_data[car_id]
        points_time = self.get_points_time(car_data, loops_available)
        timestamp = car_data.split(" ")[2]
        dt_object = self.get_time_calculated_from_timestamp(timestamp)
        in_dt_object = dt_object - timedelta(seconds=int(car_data.split(" ")[len(loops_available) * 2 + (2)]))
        directory = self.read_from_saved_data() + LOG_FILE_PATH
        try:
            for files in os.walk(directory):
                for file in files[2]:
                    if ".log" in file:
                        log_file = open(directory + '/' + file, 'r')
                        lines = log_file.readlines()
                        if len(lines) > 0:
                            start_line_time = datetime.strptime(lines[0].split(": DEBUG")[0], "%Y-%b-%d %H:%M:%S.%f")
                            end_line_time = datetime.strptime(lines[len(lines) - 1].split(": DEBUG")[0],
                                                              "%Y-%b-%d %H:%M:%S.%f")
                            if start_line_time <= dt_object <= end_line_time and start_line_time <= in_dt_object <= end_line_time:
                                self.related_logs.append(directory + file)
                            elif start_line_time <= dt_object <= end_line_time:
                                self.related_logs.append(directory + file)
                            elif start_line_time <= in_dt_object <= end_line_time:
                                self.related_logs.append(directory + file)
        except:
            pass
        if not self.related_logs:
            print("No related log file(s) found")
            # TODO: this is not working
            MsgBox(self, title="Error", body="No related log file(s) found")
        else:
            data = ''
            columns = ["Date", "Time"]
            if not loops_available == '':
                for loop_point in loops_available:
                    columns.append("Actual" + '-' + str(loop_point["loop_id"]))
                    columns.append(loop_point["point_name"])
                    columns.append("Ref_Freq" + '-' + str(loop_point["loop_id"]))
                    columns.append("Arrival_Freq" + '-' + str(loop_point["loop_id"]))
                    columns.append("Dept_Freq" + '-' + str(loop_point["loop_id"]))
                    columns.append("Peak_Freq" + '-' + str(loop_point["loop_id"]))
                    columns.append("Bavg" + '-' + str(loop_point["loop_id"]))
                    columns.append("Pavg" + '-' + str(loop_point["loop_id"]))

            for related_log_path in self.related_logs:
                file = open(related_log_path, "rt")
                data += file.read()
            for chars in [': DEBUG: summit::ssbdriver::SSBConnector::getSSBData - Loop Data: ', ' - ']:
                data = data.replace(chars, " ")
            new_set = pd.read_table(StringIO(data), sep=" ", names=columns, index_col=False)
            new_set = new_set.dropna(how='any', axis=0)
            print(new_set)

    def read_config_file(self):
        """Reads Config file and gets Loop data"""
        self.loops_available = []
        current_path = self.read_from_saved_data()
        prev_dir = Path(current_path).parent
        file = open(prev_dir + '/configure.cfg', 'r')
        line_count = 0
        upper_boundary = []
        lower_boundary = []
        string_object = ''
        for line in file.readlines():
            line_count += 1
            if "plcontrol.json" in line:
                upper_boundary.append(line_count)  # gets the line value which contains plcontrol.json
            if 'rankdisplay.json' in line:
                lower_boundary.append(line_count)  # gets the line value which contains rankdisplay.json
        with open(prev_dir + '/configure.cfg', 'r') as text_file:
            for line in itertools.islice(text_file, upper_boundary[0], lower_boundary[0]-3):  # reads the lines between
                # upper and lower boundary
                string_object += "".join(line.split())
        json_object = json.loads(string_object)  # converts the string to json object
        for lop_object in json_object["pointLoopInfo"]:  # checks valid loops and appends to available loop list
            if not lop_object["point_name"] == '':
                self.loops_available.append(lop_object)
        return self.loops_available

    def get_time_calculated(self):
        """Gets epoch time with related to given time range"""
        current_date = datetime.today()
        epoch = int(time.mktime(time.strptime(str(current_date), '%Y-%m-%d %H:%M:%S.%f')))  # current datetime to epoch
        return self.get_time_calculated_from_timestamp(epoch)

    def get_time_calculated_from_timestamp(self, timestamp):
        """Gets epoch time from timestamp with related to given time range"""
        after_converting = datetime.utcfromtimestamp(float(timestamp))  # converts epoch time to datetime
        selected_time_range = self.time_range_cb.currentText()  # selected time range
        selected_time_range_obj = datetime.strptime(selected_time_range[1:], '%H:%M')
        if selected_time_range[0] == '-':
            valid_time = after_converting - timedelta(hours=selected_time_range_obj.time().hour,
                                                      minutes=selected_time_range_obj.time().minute)
        else:
            valid_time = after_converting + timedelta(hours=selected_time_range_obj.time().hour,
                                                      minutes=selected_time_range_obj.time().minute)
        return valid_time

    # ANALYSIS INITIATION FUNCTIONS :: END

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
