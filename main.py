import math
import threading

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import sys
import serial.tools.list_ports

v_z = 340.3
broj_decimala = 4

event = threading.Event()
event.set()
h = 0


def calculate_distance(vrijeme, v_z):
    s = ((v_z*vrijeme)/2)/10000
    return s


def temperature_correction(temperatura, vrijeme):
    v_z_kor = 331.3+0.606*temperatura
    s = calculate_distance(vrijeme, v_z_kor)
    return s


def geometry_correction(h, v_z, vrijeme):
    s = calculate_distance(vrijeme, v_z)
    d = math.sqrt(s ** 2 - h ** 2)
    return d


def geo_and_temp_correction(temperatura, vrijeme, h):
     s = temperature_correction(temperatura, vrijeme)
     d = math.sqrt(s ** 2 - h ** 2)
     return d


class Worker(QObject):
    connection_error = pyqtSignal()
    set_data = pyqtSignal(float, int)

    def do_work(self):
        while(1):
            running = True
            error = False

            while (running):
                ports = serial.tools.list_ports.comports()

                STM_port = ''
                for port in ports:
                    try:
                        if str(port).index("STMicroelectronics STLink Virtual COM Port"):
                            STM_port = port.device
                    except Exception:
                        STM_port = ''

                try:
                    serialInst = serial.Serial()

                    serialInst.baudrate = 9600
                    serialInst.port = STM_port
                    serialInst.open()

                    error = False
                except Exception:
                    if not error:
                        self.connection_error.emit()

                    error = True

                else:
                    while (running):
                        try:
                            if serialInst.in_waiting:
                                packet = serialInst.readline()

                                message = packet.decode('utf').rstrip('\n')
                                data = message.split("; ")

                                self.set_data.emit(float(data[1]), int(data[0]))



                        except Exception:
                            self.connection_error.emit()
                            error = True


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setFixedSize(720, 170)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Definiranje fonta
        group_font = QtGui.QFont()
        group_font.setPointSize(14)

        label_font = QtGui.QFont()
        label_font.setPointSize(12)

        # Group udaljenost
        self.udaljenost = QtWidgets.QGroupBox(self.centralwidget)
        self.udaljenost.setGeometry(QtCore.QRect(10, 0, 270, 150))
        self.udaljenost.setFont(group_font)

        # Udaljenost label
        self.label_temperaturna = QtWidgets.QLabel(self.udaljenost)
        self.label_temperaturna.setGeometry(QtCore.QRect(10, 60, 131, 21))
        self.label_temperaturna.setFont(label_font)
        self.label_temperaturna.setObjectName("label_temperaturna")

        self.label_obje_korekcije = QtWidgets.QLabel(self.udaljenost)
        self.label_obje_korekcije.setGeometry(QtCore.QRect(16, 120, 120, 20))
        self.label_obje_korekcije.setFont(label_font)
        self.label_obje_korekcije.setObjectName("label_obje_korekcije")

        self.label_geometrijska = QtWidgets.QLabel(self.udaljenost)
        self.label_geometrijska.setGeometry(QtCore.QRect(10, 90, 131, 21))
        self.label_geometrijska.setFont(label_font)
        self.label_geometrijska.setObjectName("label_geometrijska")

        self.label_bez_korekcije = QtWidgets.QLabel(self.udaljenost)
        self.label_bez_korekcije.setGeometry(QtCore.QRect(30, 30, 101, 21))
        self.label_bez_korekcije.setFont(label_font)
        self.label_bez_korekcije.setObjectName("label_bez_korekcije")

        # Udaljenost text
        self.text_obje_korekcije = QtWidgets.QLineEdit(self.udaljenost)
        self.text_obje_korekcije.setGeometry(QtCore.QRect(150, 120, 113, 22))
        self.text_obje_korekcije.setEnabled(False)

        self.text_temperaturna = QtWidgets.QLineEdit(self.udaljenost)
        self.text_temperaturna.setGeometry(QtCore.QRect(150, 60, 113, 22))
        self.text_temperaturna.setEnabled(False)

        self.text_geometrijska = QtWidgets.QLineEdit(self.udaljenost)
        self.text_geometrijska.setGeometry(QtCore.QRect(150, 90, 113, 22))
        self.text_geometrijska.setEnabled(False)

        self.text_bez_korekcije = QtWidgets.QLineEdit(self.udaljenost)
        self.text_bez_korekcije.setGeometry(QtCore.QRect(150, 30, 113, 22))
        self.text_bez_korekcije.setEnabled(False)

        # Grupa brzina zvuka
        self.brzina_zvuka = QtWidgets.QGroupBox(self.centralwidget)
        self.brzina_zvuka.setGeometry(QtCore.QRect(290, 0, 280, 90))
        self.brzina_zvuka.setFont(group_font)

        # Brzina zvuka label
        self.label_vz_temp = QtWidgets.QLabel(self.brzina_zvuka)
        self.label_vz_temp.setGeometry(QtCore.QRect(10, 30, 91, 21))
        self.label_vz_temp.setFont(label_font)

        self.label_vz_trenutna = QtWidgets.QLabel(self.brzina_zvuka)
        self.label_vz_trenutna.setGeometry(QtCore.QRect(10, 60, 141, 21))
        self.label_vz_trenutna.setFont(label_font)

        # Brzina zvuka text
        self.text_trenutna = QtWidgets.QLineEdit(self.brzina_zvuka)
        self.text_trenutna.setGeometry(QtCore.QRect(150, 60, 113, 22))
        self.text_trenutna.setEnabled(False)

        self.text_temp = QtWidgets.QLineEdit(self.brzina_zvuka)
        self.text_temp.setGeometry(QtCore.QRect(150, 30, 113, 22))
        self.text_temp.setEnabled(False)

        # Grupa T i R razmak
        self.T_R_razmak = QtWidgets.QGroupBox(self.centralwidget)
        self.T_R_razmak.setGeometry(QtCore.QRect(290, 90, 281, 61))
        self.T_R_razmak.setFont(group_font)

        self.text_udaljenost = QtWidgets.QLineEdit(self.T_R_razmak)
        self.text_udaljenost.setGeometry(QtCore.QRect(199, 25, 71, 25))
        self.text_udaljenost.setEnabled(False)
        self.text_udaljenost.setText("0 mm")

        self.slider_udaljenost = QtWidgets.QSlider(self.T_R_razmak)
        self.slider_udaljenost.setGeometry(QtCore.QRect(10, 30, 181, 20))
        self.slider_udaljenost.setMaximum(70)
        self.slider_udaljenost.setOrientation(QtCore.Qt.Horizontal)
        self.slider_udaljenost.valueChanged.connect(self.sliderChanged)
        self.slider_udaljenost.sliderReleased.connect(self.sliderRelese)

        # Grupa temperatura
        self.temperatura = QtWidgets.QGroupBox(self.centralwidget)
        self.temperatura.setGeometry(QtCore.QRect(580, 0, 131, 151))
        self.temperatura.setFont(group_font)

        self.text_bmp = QtWidgets.QLineEdit(self.temperatura)
        self.text_bmp.setGeometry(QtCore.QRect(30, 120, 80, 25))
        self.text_bmp.setEnabled(False)

        self.porgress_temp = QtWidgets.QProgressBar(self.temperatura)
        self.porgress_temp.setGeometry(QtCore.QRect(60, 30, 21, 81))
        self.porgress_temp.setMinimum(10)
        self.porgress_temp.setMaximum(40)
        self.porgress_temp.setTextVisible(False)
        self.porgress_temp.setOrientation(QtCore.Qt.Vertical)

        # Menu bar
        MainWindow.setCentralWidget(self.centralwidget)
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
        self.udaljenost.setTitle(_translate("MainWindow", "Udaljenost"))
        self.label_temperaturna.setText(_translate("MainWindow", "S temperaturnom"))
        self.label_obje_korekcije.setText(_translate("MainWindow", "S obje korekcije"))
        self.label_geometrijska.setText(_translate("MainWindow", "S geometrijskom"))
        self.label_bez_korekcije.setText(_translate("MainWindow", "Bez korekcije"))
        self.brzina_zvuka.setTitle(_translate("MainWindow", "Brzina zvuka"))
        self.label_vz_temp.setText(_translate("MainWindow", "Vz - 15.5°C"))
        self.label_vz_trenutna.setText(_translate("MainWindow", "Vz - trenutna temp"))
        self.T_R_razmak.setTitle(_translate("MainWindow", "T i R razmak"))
        self.temperatura.setTitle(_translate("MainWindow", "Temperatura"))

    def sliderChanged(self):
        self.text_udaljenost.setText(f"{self.slider_udaljenost.value()} mm")

    def sliderRelese(self):
        if event.is_set():
            event.clear()

            global h
            h = int(self.slider_udaljenost.value())/10

            event.set()

    def no_connection(self):
        self.text_obje_korekcije.setText("None")
        self.text_temperaturna.setText("None")
        self.text_geometrijska.setText("None")
        self.text_bez_korekcije.setText("None")
        self.text_trenutna.setText("None")
        self.text_temp.setText("None")
        self.text_bmp.setText("None")
        self.porgress_temp.setProperty("value", 0)

    def set_data(self, temperatura, udaljenost):
        if event.is_set():
            event.clear()

            # Calculate udaljenost
            udaljenost_bez_korekcije = calculate_distance(udaljenost, v_z)
            udaljenost_s_temp_korekcijom = temperature_correction(temperatura, udaljenost)
            udaljenost_s_geo_korekcijom = geometry_correction(h, v_z, udaljenost)
            udaljenost_s_obje_korekcije = geo_and_temp_correction(temperatura, udaljenost, h)

            # Set temperatura
            self.text_bmp.setText("{:.2f}".format(temperatura) + ' °C')
            self.porgress_temp.setProperty("value", temperatura)

            # Set udaljenosti
            self.text_bez_korekcije.setText("{:.2f}".format(udaljenost_bez_korekcije) + ' cm')
            self.text_temperaturna.setText("{:.2f}".format(udaljenost_s_temp_korekcijom) + ' cm')
            self.text_geometrijska.setText("{:.2f}".format(udaljenost_s_geo_korekcijom) + ' cm')
            self.text_obje_korekcije.setText("{:.2f}".format(udaljenost_s_obje_korekcije) + ' cm')

            # Set brzina zvuka
            v_z_kor = 331.3 + 0.606 * temperatura
            self.text_trenutna.setText("{:.2f}".format(v_z_kor) + ' m/s')
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