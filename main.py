import sys
import decimal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication, QFileDialog, QTextEdit, QLineEdit, QHBoxLayout, QComboBox, QLabel
from datetime import date, datetime, timedelta
import time, os


def float_range(start, stop, step):
  while start < stop:
    yield float(start)
    start += decimal.Decimal(step)

class Application(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'SSB Analyser'
        self.left = 500
        self.top = 200
        self.width = 500
        self.height = 200
        self.directory_path = None
        self.car_files_txt = None
        self.car_files = []
        self.open_file_dialog_btn = None
        self.time_range_cb = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Create textbox
        current_path = self.read_from_saved_data()
        self.directory_path = QLineEdit(current_path if current_path else "")
        self.directory_path.setReadOnly(True)
        self.directory_path.move(0, 20)
        self.directory_path.resize(280, 40)

        # Create a button in the window
        self.open_file_dialog_btn = QPushButton('Set Path', self)
        self.open_file_dialog_btn.clicked.connect(self.open_file_dialog_btn_click)

        # path and button layout
        hbox = QHBoxLayout()
        hbox.addSpacing(50)
        hbox.addWidget(self.directory_path)
        hbox.addWidget(self.open_file_dialog_btn)
        hbox.addSpacing(50)

        # Create carfile display
        self.car_files_txt = QTextEdit("")
        self.car_files_txt.setReadOnly(True)
        # Create car file dialog button in the window
        open_car_file_dialog_btn = QPushButton('Load Car Files', self)
        open_car_file_dialog_btn.clicked.connect(self.open_car_file_dialog_btn_click)

        # time range combo box
        cb_lable = QLabel("Time Gap: ")
        self.time_range_cb = QComboBox()
        # self.time_range_cb.lineEdit().setAlignment
        self.time_range_cb.addItems([("%s%d:%02d" % ("-" if x < 0 else "+",int(abs(x)), (abs(x)*60) % 60)) for x in list(float_range(-12, 13, '0.5'))])

        # box for car file and range
        car_file_box = QHBoxLayout()
        car_file_box.addSpacing(50)
        car_file_box.addWidget(self.car_files_txt)
        car_file_box.addWidget(open_car_file_dialog_btn)
        car_file_box.addSpacing(20)
        car_file_box.addWidget(cb_lable)
        car_file_box.addWidget(self.time_range_cb)
        car_file_box.addSpacing(50)


        generate_analysis_btn = QPushButton('Analyse', self)
        generate_analysis_btn.clicked.connect(self.initiate_analysis)
        generate_analysis_btn.setGeometry(200, 150, 500, 40)

        # Analysis button layout
        hbox_for_analysis = QHBoxLayout()
        hbox_for_analysis.addStretch(1)
        hbox_for_analysis.addWidget(generate_analysis_btn)
        hbox_for_analysis.addStretch(1)



        # main Layout
        vbox = QVBoxLayout()
        vbox.addLayout(car_file_box)
        vbox.addLayout(hbox)
        vbox.addLayout(hbox_for_analysis)

        self.setLayout(vbox)
        self.show()

    def get_time_calculated(self):
        """Gets epoch time with related to given time range"""
        valid_time = ''
        current_date = datetime.today()
        epoch = int(time.mktime(time.strptime(str(current_date), '%Y-%m-%d %H:%M:%S.%f')))  # current datetime to epoch
        after_converting = datetime.utcfromtimestamp(float(epoch))  # converts epoch time to datetime
        selected_time_range = self.time_range_cb.currentText()  # selected time range
        selected_time_range_obj = datetime.strptime(selected_time_range[1:], '%H:%M')
        if selected_time_range[0] == '-':
            valid_time = after_converting - timedelta(hours=selected_time_range_obj.time().hour,
                                                      minutes=selected_time_range_obj.time().minute)
        else:
            valid_time = after_converting + timedelta(hours=selected_time_range_obj.time().hour,
                                                      minutes=selected_time_range_obj.time().minute)
        return valid_time

    def read_files(self):
        """Reads Car and Log files from the directories"""
        directory = self.read_from_saved_data()
        for car_file_path in self.car_files:
            car_file = open(car_file_path, 'r')
            for line in car_file:
                for files in os.walk(directory):
                    for file in files[2]:
                        log_file = open(directory + '/' + file, 'r')
                        print(log_file.readline())  # analysis logic comes here


    def initiate_analysis(self):
        print(self.directory_path.text())
        print(self.car_files)
        print(self.time_range_cb.currentText())
        print(self.get_time_calculated())
        # self.read_files()


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
    application = Application()
    sys.exit(app.exec_())

