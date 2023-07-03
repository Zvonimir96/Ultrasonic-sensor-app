import math
import threading

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import sys
import serial.tools.list_ports

v_z = 340.3
broj_decimala = 4
h = 0

event = threading.Event()
event.set()


def calculate_distance(vrijeme, v_z):
    s = ((v_z*vrijeme)/2)/10000
    return s


def temperature_correction(temperature, vrijeme):
    v_z_kor = 331.3+0.606*temperature
    s = calculate_distance(vrijeme, v_z_kor)
    return s


def geometry_correction(h, v_z, vrijeme):
    s = calculate_distance(vrijeme, v_z)
    d = math.sqrt(s ** 2 - h ** 2)
    return d


def geo_and_temp_correction(temperature, vrijeme, h):
     s = temperature_correction(temperature, vrijeme)
     d = math.sqrt(s ** 2 - h ** 2)
     return d


class Worker(QObject):
    connection_error = pyqtSignal()
    set_data = pyqtSignal(float, int)

    def do_work(self):
        while(True):
            running = True
            error = False

            while (running):
                ports = serial.tools.list_ports.comports()

                # Find STM32 serial port by its name
                STM_port = ''
                for port in ports:
                    try:
                        if str(port).index("STMicroelectronics STLink Virtual COM Port"):
                            STM_port = port.device
                            break
                    except Exception:
                        STM_port = ''

                try:
                    # Set serial communication parameters
                    serialInst = serial.Serial()

                    serialInst.baudrate = 9600
                    serialInst.port = STM_port
                    serialInst.open()

                    error = False
                except Exception:
                    if not error:
                        # Display error message
                        self.connection_error.emit()

                    error = True

                else:
                    # Serial communication is set up correctly
                    while (running):
                        try:
                            if serialInst.in_waiting:
                                packet = serialInst.readline()

                                # Read and decode data
                                message = packet.decode('utf').rstrip('\n')
                                data = message.split("; ")

                                # Display data
                                self.set_data.emit(float(data[1]), int(data[0]))

                        except Exception:
                            # Display error message
                            self.connection_error.emit()
                            error = True


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setFixedSize(720, 170)

        self.central_widget = QtWidgets.QWidget(MainWindow)
        self.central_widget.setObjectName("centralwidget")

        # Font
        group_font = QtGui.QFont()
        group_font.setPointSize(14)

        label_font = QtGui.QFont()
        label_font.setPointSize(12)

        # Group distance
        self.distance = QtWidgets.QGroupBox(self.central_widget)
        self.distance.setGeometry(QtCore.QRect(10, 0, 270, 150))
        self.distance.setFont(group_font)

        # Distance label
        self.label_temperature = QtWidgets.QLabel(self.distance)
        self.label_temperature.setGeometry(QtCore.QRect(10, 60, 131, 21))
        self.label_temperature.setFont(label_font)
        self.label_temperature.setObjectName("label_temperaturna")

        self.label_both_corrections = QtWidgets.QLabel(self.distance)
        self.label_both_corrections.setGeometry(QtCore.QRect(16, 120, 120, 20))
        self.label_both_corrections.setFont(label_font)
        self.label_both_corrections.setObjectName("label_obje_korekcije")

        self.label_geometry_correction = QtWidgets.QLabel(self.distance)
        self.label_geometry_correction.setGeometry(QtCore.QRect(10, 90, 131, 21))
        self.label_geometry_correction.setFont(label_font)
        self.label_geometry_correction.setObjectName("label_geometrijska")

        self.label_without_corrcetion = QtWidgets.QLabel(self.distance)
        self.label_without_corrcetion.setGeometry(QtCore.QRect(30, 30, 101, 21))
        self.label_without_corrcetion.setFont(label_font)
        self.label_without_corrcetion.setObjectName("label_bez_korekcije")

        # Distance text
        self.text_both_corrections = QtWidgets.QLineEdit(self.distance)
        self.text_both_corrections.setGeometry(QtCore.QRect(150, 120, 113, 22))
        self.text_both_corrections.setEnabled(False)

        self.text_temperature = QtWidgets.QLineEdit(self.distance)
        self.text_temperature.setGeometry(QtCore.QRect(150, 60, 113, 22))
        self.text_temperature.setEnabled(False)

        self.text_geometry_correction = QtWidgets.QLineEdit(self.distance)
        self.text_geometry_correction.setGeometry(QtCore.QRect(150, 90, 113, 22))
        self.text_geometry_correction.setEnabled(False)

        self.text_without_corrcetion = QtWidgets.QLineEdit(self.distance)
        self.text_without_corrcetion.setGeometry(QtCore.QRect(150, 30, 113, 22))
        self.text_without_corrcetion.setEnabled(False)

        # Group sound speed
        self.sound_speed = QtWidgets.QGroupBox(self.central_widget)
        self.sound_speed.setGeometry(QtCore.QRect(290, 0, 280, 90))
        self.sound_speed.setFont(group_font)

        # Sound speed label
        self.label_vz_temp = QtWidgets.QLabel(self.sound_speed)
        self.label_vz_temp.setGeometry(QtCore.QRect(10, 30, 91, 21))
        self.label_vz_temp.setFont(label_font)

        self.label_vz_current = QtWidgets.QLabel(self.sound_speed)
        self.label_vz_current.setGeometry(QtCore.QRect(10, 60, 141, 21))
        self.label_vz_current.setFont(label_font)

        # Sound speed text
        self.text_vz_current = QtWidgets.QLineEdit(self.sound_speed)
        self.text_vz_current.setGeometry(QtCore.QRect(150, 60, 113, 22))
        self.text_vz_current.setEnabled(False)

        self.text_temp = QtWidgets.QLineEdit(self.sound_speed)
        self.text_temp.setGeometry(QtCore.QRect(150, 30, 113, 22))
        self.text_temp.setEnabled(False)

        # Group T i R space
        self.T_R_space = QtWidgets.QGroupBox(self.central_widget)
        self.T_R_space.setGeometry(QtCore.QRect(290, 90, 281, 61))
        self.T_R_space.setFont(group_font)

        self.text_distance = QtWidgets.QLineEdit(self.T_R_space)
        self.text_distance.setGeometry(QtCore.QRect(199, 25, 71, 25))
        self.text_distance.setEnabled(False)
        self.text_distance.setText("0 mm")

        self.slider_distance = QtWidgets.QSlider(self.T_R_space)
        self.slider_distance.setGeometry(QtCore.QRect(10, 30, 181, 20))
        self.slider_distance.setMaximum(70)
        self.slider_distance.setOrientation(QtCore.Qt.Horizontal)
        self.slider_distance.valueChanged.connect(self.slider_changed)
        self.slider_distance.sliderReleased.connect(self.slider_release)

        # Group temperature
        self.temperature = QtWidgets.QGroupBox(self.central_widget)
        self.temperature.setGeometry(QtCore.QRect(580, 0, 131, 151))
        self.temperature.setFont(group_font)

        self.text_bmp = QtWidgets.QLineEdit(self.temperature)
        self.text_bmp.setGeometry(QtCore.QRect(30, 120, 80, 25))
        self.text_bmp.setEnabled(False)

        self.porgress_temp = QtWidgets.QProgressBar(self.temperature)
        self.porgress_temp.setGeometry(QtCore.QRect(60, 30, 21, 81))
        self.porgress_temp.setMinimum(10)
        self.porgress_temp.setMaximum(40)
        self.porgress_temp.setTextVisible(False)
        self.porgress_temp.setOrientation(QtCore.Qt.Vertical)

        # Menu bar
        MainWindow.setCentralWidget(self.central_widget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 714, 21))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # QThred
        self.worker = Worker()
        self.worker_thread = QThread()

        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.do_work)
        self.worker.connection_error.connect(self.no_connection)
        self.worker.set_data.connect(self.set_data)

        self.worker_thread.start()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Senzori - mjerenje udaljenosti ultrazvučnog senzora"))
        self.distance.setTitle(_translate("MainWindow", "Udaljenost"))
        self.label_temperature.setText(_translate("MainWindow", "S temperaturnom"))
        self.label_both_corrections.setText(_translate("MainWindow", "S obje korekcije"))
        self.label_geometry_correction.setText(_translate("MainWindow", "S geometrijskom"))
        self.label_without_corrcetion.setText(_translate("MainWindow", "Bez korekcije"))
        self.sound_speed.setTitle(_translate("MainWindow", "Brzina zvuka"))
        self.label_vz_temp.setText(_translate("MainWindow", "Vz - 15.5°C"))
        self.label_vz_current.setText(_translate("MainWindow", "Vz - trenutna temp"))
        self.T_R_space.setTitle(_translate("MainWindow", "T i R razmak"))
        self.temperature.setTitle(_translate("MainWindow", "temperature"))

    def slider_changed(self):
        self.text_distance.setText(f"{self.slider_distance.value()} mm")

    def slider_release(self):
        if event.is_set():
            event.clear()

            global h
            h = int(self.slider_distance.value())/10

            event.set()

    def no_connection(self):
        self.text_both_corrections.setText("None")
        self.text_temperature.setText("None")
        self.text_geometry_correction.setText("None")
        self.text_without_corrcetion.setText("None")
        self.text_vz_current.setText("None")
        self.text_temp.setText("None")
        self.text_bmp.setText("None")
        self.porgress_temp.setProperty("value", 0)

    def set_data(self, temperature, udaljenost):
        if event.is_set():
            event.clear()

            # Calculate distance
            distance_without_correction = calculate_distance(udaljenost, v_z)
            distance_with_temperature_correction = temperature_correction(temperature, udaljenost)
            distance_with_geometry_correction = geometry_correction(h, v_z, udaljenost)
            distance_with_corrections = geo_and_temp_correction(temperature, udaljenost, h)

            # Set temperature
            self.text_bmp.setText("{:.2f}".format(temperature) + ' °C')
            self.porgress_temp.setProperty("value", temperature)

            # Set distance
            self.text_without_corrcetion.setText("{:.2f}".format(distance_without_correction) + ' cm')
            self.text_temperature.setText("{:.2f}".format(distance_with_temperature_correction) + ' cm')
            self.text_geometry_correction.setText("{:.2f}".format(distance_with_geometry_correction) + ' cm')
            self.text_both_corrections.setText("{:.2f}".format(distance_with_corrections) + ' cm')

            # Set sound speed
            v_z_kor = 331.3 + 0.606 * temperature
            self.text_vz_current.setText("{:.2f}".format(v_z_kor) + ' m/s')
            self.text_temp.setText("{:.2f}".format(v_z) + ' m/s')

            event.set()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    MainWindow.setWindowIcon(QtGui.QIcon('icon.png'))
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    MainWindow.show()
    sys.exit(app.exec_())