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
import glob
from io import *
import plotly.graph_objs as go
from plotly.subplots import make_subplots


LOG_FILE_PATH = "/logs/"
CONFIG_FILE_PATH = "/config/"


def float_range(start, stop, step):
    while start < stop:
        yield float(start)
        start += decimal.Decimal(step)


def perdelta(start, end, delta):
    curr = start
    while curr <= end:
        yield curr
        curr += delta


def get_second_range(start, end):
    stack = []
    for result in perdelta(start, end, timedelta(seconds=30)):
        stack.append(result)
    return stack


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
        self.dataframe = None
        self.points_time = None
        self.final_dataset_car_vs_time = None
        self.car_in_time = False
        self.car_out_time = False

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

    def showdialog(self, title, body):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText(body)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Cancel)
        msg.exec_()

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
        buttons.setStandardButtons(QDialogButtonBox.Apply)
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

    # DRAW GRAPH
    def draw_car_vs_time(self):
        fig = make_subplots(len(self.final_dataset_car_vs_time), 1, subplot_titles=[x["point_name"].replace("_", " ") for x in self.loops_available])
        for i in self.final_dataset_car_vs_time:
            temp_df = pd.DataFrame()
            temp_df['Datetime'] = pd.to_datetime(
                self.final_dataset_car_vs_time[i]["Date"] + " " + self.final_dataset_car_vs_time[i]["Time"])
            temp_df["Actual-" + str(i)] = self.final_dataset_car_vs_time[i]["Actual-" + str(i)].astype('str')

            fig.add_trace(go.Scatter(y=temp_df["Actual-" + str(i)],
                                     x=temp_df['Datetime'],
                                     name=i), i+1, 1)

        fig.update_xaxes(type='date', tickmode="linear", dtick=200, showgrid=False,rangeslider=dict(visible=True), rangeslider_thickness = 0.03)
        fig.update_yaxes(tickformat='digits', showgrid=False)
        fig.update_layout(height=3000, template='plotly',showlegend=False, title="Car vs Time - " + self.car_combo_box.currentText())
        fig.show()

    # DRAW GRAPH :: END

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
        self.get_car_data()
        # update car combo box
        self.car_combo_box.clear()
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
            self.showdialog(title="Error", body="No car data found")

    def get_points_time(self, car_data, loops):
        """Calculate In and Out time for each Loop point using Available loop data and Car file data"""
        points_time = {}
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
            for point in range(initial, (initial + 2)):
                if not end_flag:
                    start_point_time = start_dt_object + timedelta(seconds=int(car_data_points[point]))
                    end_flag = True
                else:
                    end_point_time = start_dt_object + timedelta(seconds=int(car_data_points[point]))
            points_time.update(
                {loop['loop_id']: {"in_time": start_point_time.time(), "end_time": end_point_time.time()}})
            end_flag = False
            initial += 2
        return points_time

    def get_log_files(self, car_id):
        """Find corresponding log files for given car"""
        # startTime = time.time()
        if car_id == "":
            return
        self.related_logs = []
        loops_available = self.read_config_file()
        car_data = self.car_data[car_id]
        self.points_time = self.get_points_time(car_data, loops_available)
        timestamp = car_data.split(" ")[2]
        dt_object = self.get_time_calculated_from_timestamp(timestamp)
        self.car_out_time = dt_object
        in_dt_object = dt_object - timedelta(seconds=int(car_data.split(" ")[len(loops_available) * 2 + (2)]))
        self.car_in_time = in_dt_object
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

        # log_file_df = pd.DataFrame()
        # try:
        #     for files in os.walk(directory):
        #         for file in files[2]:
        #             if ".log" in file:
        #                 with open(directory + '/' + file, 'r') as content:
        #                     df = content.read()


        # # log_file = open(directory + '/' + file, 'r')
        # lines = log_file.readlines()
        # if len(lines) > 0:
        #     start_line_time = datetime.strptime(lines[0].split(": DEBUG")[0], "%Y-%b-%d %H:%M:%S.%f")
        #     end_line_time = datetime.strptime(lines[len(lines) - 1].split(": DEBUG")[0],
        #                                       "%Y-%b-%d %H:%M:%S.%f")
        #     if start_line_time <= dt_object <= end_line_time and start_line_time <= in_dt_object <= end_line_time:
        #         self.related_logs.append(directory + file)
        #     elif start_line_time <= dt_object <= end_line_time:
        #         self.related_logs.append(directory + file)
        #     elif start_line_time <= in_dt_object <= end_line_time:
        #         self.related_logs.append(directory + file)
        # except:
        #     pass

        # # path = r'C:\DRO\DCL_rawdata_files'  # use your path
        # all_files = [x.replace("\\", "/") for x in glob.glob(os.path.join(directory) + "*.log*")]
        #
        # li = []
        #
        # df = pd.DataFrame()
        # for filename in all_files:
        #     # df = pd.read_table(filename,iterator=True, index_col=None, header=0)
        #     # li.append(df)
        #     for chunk in pd.read_table(filename, header=None,  chunksize=1000):
        #         df = pd.concat([df, chunk], ignore_index=True)
        # frame = pd.concat(li)
        # print(frame)
        # print(time.time() - startTime)

        if not self.related_logs:
            print("No related log file(s) found")
            self.showdialog(title="Error", body="No related log file(s) found")
        else:
            data = ''
            columns = ["Date", "Time"]
            dtypes = {'Date': 'str', 'Time': 'str'}
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

                    dtypes.update({"Actual" + '-' + str(loop_point["loop_id"]): 'str'})
                    dtypes.update({loop_point["point_name"]: 'str'})
                    dtypes.update({"Ref_Freq" + '-' + str(loop_point["loop_id"]): 'str'})
                    dtypes.update({"Arrival_Freq" + '-' + str(loop_point["loop_id"]): 'str'})
                    dtypes.update({"Dept_Freq" + '-' + str(loop_point["loop_id"]): 'str'})
                    dtypes.update({"Peak_Freq" + '-' + str(loop_point["loop_id"]): 'str'})
                    dtypes.update({"Bavg" + '-' + str(loop_point["loop_id"]): 'str'})
                    dtypes.update({"Pavg" + '-' + str(loop_point["loop_id"]): 'str'})

            for related_log_path in self.related_logs:
                file = open(related_log_path, "rt")
                data += file.read()
            for chars in [': DEBUG: summit::ssbdriver::SSBConnector::getSSBData - Loop Data: ', ' - ']:
                data = data.replace(chars, " ")
            new_set = pd.read_table(StringIO(data), sep=" ", names=columns, dtype=dtypes, index_col=False)
            new_set = new_set.dropna(how='any', axis=0)
            self.dataframe = new_set
            self.create_dataset_for_car_vs_time(new_set)
            self.draw_car_vs_time()
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
            for line in itertools.islice(text_file, upper_boundary[0],
                                         lower_boundary[0] - 3):  # reads the lines between
                # upper and lower boundary
                string_object += "".join(line.split())
        json_object = json.loads(string_object)  # converts the string to json object
        for lop_object in json_object["pointLoopInfo"]:  # checks valid loops and appends to available loop list
            if not lop_object["point_name"] == '':
                self.loops_available.append(lop_object)
        return self.loops_available

    def create_dataset_for_car_vs_time(self, dataset):
        """Generate dataset for car vs time graph"""
        if not self.points_time:
            print("Something wrong with point data.")
            self.showdialog(title="Error", body="no log data related to points were found")
            return
        final_dataset = {}
        time_col = self.dataframe['Time'].transform(lambda x: x + ".000000" if len(x.split(".")) <= 1 else x)
        tt = pd.to_datetime(time_col, format='%H:%M:%S.%f').dt.time

        for key, val in self.points_time.items():
            loopId = key
            in_time = val["in_time"]
            end_time = val["end_time"]

            filtered_df = dataset.loc[(tt >= in_time) & (tt <= end_time)]
            final_dataset.update({
                loopId: filtered_df
            })
        self.final_dataset_car_vs_time = final_dataset

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
        if path:
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
