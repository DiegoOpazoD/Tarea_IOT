# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'menu.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QTimer
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from db_utils import *


class Canvas (FigureCanvas):
    def __init__(self, parent, time, variables, title, value):
        fig, self.axis = plt.subplots(figsize=(4,3), dpi=100)
        super().__init__(fig)
        self.setParent(parent)
        self.axis.plot(time, variables)
        self.axis.set_xlabel('Time')
        self.axis.set_ylabel(value)
        self.axis.set_title(title)
        self.setFixedSize(600,400)


class Ui_MainWindow(object):
    def __init__(self, MainWindow):
        self.setupUi(MainWindow)  

        self.timer = QTimer(MainWindow)  
        self.timer.timeout.connect(lambda : self.plot_graph("batt"))


    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(640, 480)

        self.currentGraph = ""

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setGeometry(QtCore.QRect(10, 10, 600, 450))
        self.stackedWidget.setObjectName("stackedWidget")

        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.gridLayoutWidget = QtWidgets.QWidget(self.page)

        self.gridLayoutWidget.setGeometry(QtCore.QRect(170, 150, 271, 131))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")

        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")

        self.tempButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.tempButton.setObjectName("tempButton")

        self.gridLayout.addWidget(self.tempButton, 2, 0, 1, 1)

        self.rmsButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.rmsButton.setObjectName("rmsButton")

        self.gridLayout.addWidget(self.rmsButton, 4, 2, 1, 1)

        self.yAmplitudeButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.yAmplitudeButton.setObjectName("yAmplitudeButton")

        self.gridLayout.addWidget(self.yAmplitudeButton, 3, 1, 1, 1)

        self.xAmplitudeButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.xAmplitudeButton.setObjectName("xAmplitudeButton")

        self.gridLayout.addWidget(self.xAmplitudeButton, 2, 1, 1, 1)

        self.batteryButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.batteryButton.setObjectName("batteryButton")

        self.gridLayout.addWidget(self.batteryButton, 0, 0, 1, 1)

        self.humButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.humButton.setObjectName("humButton")

        self.gridLayout.addWidget(self.humButton, 4, 0, 1, 1)

        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.xFreqButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.xFreqButton.setObjectName("xFreqButton")

        self.gridLayout_2.addWidget(self.xFreqButton, 0, 0, 1, 1)

        self.gridLayout.addLayout(self.gridLayout_2, 0, 2, 1, 1)

        self.zFreqButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.zFreqButton.setObjectName("zFreqButton")
        
        self.gridLayout.addWidget(self.zFreqButton, 3, 2, 1, 1)

        self.presButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.presButton.setObjectName("presButton")

        self.gridLayout.addWidget(self.presButton, 3, 0, 1, 1)

        self.coButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.coButton.setObjectName("coButton")
        
        self.gridLayout.addWidget(self.coButton, 0, 1, 1, 1)

        self.zAmplitudeButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.zAmplitudeButton.setObjectName("zAmplitudeButton")

        self.gridLayout.addWidget(self.zAmplitudeButton, 4, 1, 1, 1)

        self.yFreqButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.yFreqButton.setObjectName("yFreqButton")

        self.gridLayout.addWidget(self.yFreqButton, 2, 2, 1, 1)
        
        self.menuLabel = QtWidgets.QLabel(self.page)
        self.menuLabel.setGeometry(QtCore.QRect(290, 120, 31, 16))
        self.menuLabel.setObjectName("menuLabel")

        self.editProtocolButton = QtWidgets.QPushButton(self.page)
        self.editProtocolButton.setGeometry(QtCore.QRect(270, 325, 75, 23))
        self.editProtocolButton.setObjectName("editProtocolButton")

        self.connectBluetooth = QtWidgets.QPushButton(self.page)
        self.connectBluetooth.setGeometry(QtCore.QRect(255, 350, 115, 23))
        self.connectBluetooth.setObjectName("connectBluetooth")

        self.disconnectBluetooth = QtWidgets.QPushButton(self.page)
        self.disconnectBluetooth.setGeometry(QtCore.QRect(255, 375, 115, 23))
        self.disconnectBluetooth.setObjectName("disconnectBluetooth")

        self.changeESP = QtWidgets.QPushButton(self.page)
        self.changeESP.setGeometry(QtCore.QRect(255, 400, 115, 23))
        self.changeESP.setCheckable(True)
        self.changeESP.setObjectName("changeESP")


        self.stackedWidget.addWidget(self.page)

        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")

        self.protocolLabel = QtWidgets.QLabel(self.page_2)
        self.protocolLabel.setGeometry(QtCore.QRect(295, 180, 47, 14))
        self.protocolLabel.setObjectName("protocolLabel")

        self.protocolLineEdit = QtWidgets.QLineEdit(self.page_2)
        self.protocolLineEdit.setGeometry(QtCore.QRect(250, 200, 131, 20))
        self.protocolLineEdit.setObjectName("protocolLineEdit")

        self.updateButton = QtWidgets.QPushButton(self.page_2)
        self.updateButton.setGeometry(QtCore.QRect(275, 220, 75, 23))
        self.updateButton.setObjectName("updateButton")

        self.protocolButton = QtWidgets.QPushButton(self.page_2)
        self.protocolButton.setGeometry(QtCore.QRect(240, 245, 150, 23))
        self.protocolButton.setCheckable(True)
        self.protocolButton.setObjectName("protocolButton")

        self.back2Button = QtWidgets.QPushButton(self.page_2)
        self.back2Button.setGeometry(QtCore.QRect(275, 270, 75, 23))
        self.back2Button.setObjectName("back2Button")

        self.errorLabel = QtWidgets.QLabel(self.page_2)
        self.errorLabel.setGeometry(QtCore.QRect(237, 295, 47, 14))
        self.errorLabel.setStyleSheet("color: red")
        self.errorLabel.setObjectName("errorLabel")
        self.errorLabel.hide()

        self.stackedWidget.addWidget(self.page_2)

        self.page_12 = QtWidgets.QWidget()
        self.page_12.setObjectName("page_12")

        self.backButton = QtWidgets.QPushButton(self.page_12)
        self.backButton.setGeometry(QtCore.QRect(270, 425, 75, 23))
        self.backButton.setObjectName("backButton")

        self.graph_layout = QtWidgets.QVBoxLayout(self.page_12)

        self.stackedWidget.addWidget(self.page_12)

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 640, 22))
        self.menubar.setObjectName("menubar")

        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")

        MainWindow.setStatusBar(self.statusbar)

        self.conexion_db = conectar_db()
        """ while not self.conexion_db:
            print("Base de datos no conectada, reintentando conexion")
            time.sleep(3)
            self.conexion_db = conectar_db() """


        self.backButton.clicked.connect(self.goBack)
        self.back2Button.clicked.connect(self.goBack)
        self.tempButton.clicked.connect(lambda:self.loadGraph("temp"))
        self.rmsButton.clicked.connect(lambda:self.loadGraph("rms"))
        self.coButton.clicked.connect(lambda:self.loadGraph("co"))
        self.xAmplitudeButton.clicked.connect(lambda:self.loadGraph("amp_x"))
        self.yAmplitudeButton.clicked.connect(lambda:self.loadGraph("amp_y"))
        self.zAmplitudeButton.clicked.connect(lambda:self.loadGraph("amp_z"))
        self.xFreqButton.clicked.connect(lambda:self.loadGraph("freq_x"))
        self.yFreqButton.clicked.connect(lambda:self.loadGraph("freq_y"))
        self.zFreqButton.clicked.connect(lambda:self.loadGraph("freq_z"))
        self.humButton.clicked.connect(lambda:self.loadGraph("hum"))
        self.presButton.clicked.connect(lambda:self.loadGraph("pres"))
        self.batteryButton.clicked.connect(lambda:self.loadGraph("batt"))
        self.editProtocolButton.clicked.connect(self.goEdit)
        self.updateButton.clicked.connect(self.updateConfactiva)
        self.protocolButton.clicked.connect(self.contToDisc)
        self.changeESP.clicked.connect(self.swapESP)

        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.tempButton.setText(_translate("MainWindow", "Temperature"))
        self.rmsButton.setText(_translate("MainWindow", "RMS"))
        self.yAmplitudeButton.setText(_translate("MainWindow", "Y Amplitude"))
        self.xAmplitudeButton.setText(_translate("MainWindow", "X Amplitude"))
        self.batteryButton.setText(_translate("MainWindow", "Battery"))
        self.humButton.setText(_translate("MainWindow", "Humidity"))
        self.xFreqButton.setText(_translate("MainWindow", "X Fequency"))
        self.zFreqButton.setText(_translate("MainWindow", "Z Frequency"))
        self.presButton.setText(_translate("MainWindow", "Pressure"))
        self.coButton.setText(_translate("MainWindow", "Co"))
        self.zAmplitudeButton.setText(_translate("MainWindow", "Z Amplitude"))
        self.yFreqButton.setText(_translate("MainWindow", "Y Frequency"))
        self.menuLabel.setText(_translate("MainWindow", "Menú"))
        self.editProtocolButton.setText(_translate("MainWindow", "Edit Protocol"))
        self.protocolLabel.setText(_translate("MainWindow", "Protocol"))
        self.connectBluetooth.setText(_translate("MainWindow", "Connect Bluetooth"))
        self.disconnectBluetooth.setText(_translate("MainWindow", "Disconnect Bluetooth"))
        self.errorLabel.setText(_translate("MainWindow", "Please introduce a valid protocol"))
        self.updateButton.setText(_translate("MainWindow", "Update"))
        self.protocolButton.setText(_translate("MainWindow", "Continuous to Discontinuous"))
        self.backButton.setText(_translate("MainWindow", "Back"))
        self.back2Button.setText(_translate("MainWindow", "Back"))
        self.changeESP.setText(_translate("MainWindow", "Change ESP"))


    def goBack(self):
        self.currentGraph = ""
        self.timer.stop()
        self.errorLabel.hide()
        self.stackedWidget.setCurrentIndex(0)


    def goEdit(self):
        self.stackedWidget.setCurrentIndex(1)


    def goGraph(self):
        self.stackedWidget.setCurrentIndex(2)

    def contToDisc(self):
        if (self.protocolButton.isCheckable()):
            #Need to add functions to the db
            self.protocolButton.setStyleSheet("background-color : lightgrey")
        else: 
            self.protocolButton.setStyleSheet("background-color : white")

        self.protocolButton.setCheckable(not self.protocolButton.isCheckable())

    def swapESP(self): 
        if (self.changeESP.isCheckable()):
            self.changeESP.setStyleSheet("background-color : lightgrey")
        else: 
            self.changeESP.setStyleSheet("background-color : white")

        self.changeESP.setCheckable(not self.changeESP.isCheckable())

    def updateConfactiva(self):
        protocol = self.protocolLineEdit.text()
        toggled = self.protocolButton.isCheckable()
        self.protocolLineEdit.clear()

        match protocol:
            case "p0" | "0" | "P0":
                update_conf_activa(self.conexion_db, 1 if toggled else 6)
                self.errorLabel.hide()
            case "p1" | "1" | "P1":
                update_conf_activa(self.conexion_db, 2 if toggled else 7)
                self.errorLabel.hide()
            case "p2" | "2" | "P2":
                update_conf_activa(self.conexion_db, 3 if toggled else 8)
                self.errorLabel.hide()
            case "p3" | "3" | "P3":
                update_conf_activa(self.conexion_db, 4 if toggled else 9)
                self.errorLabel.hide()
            case _:
                self.errorLabel.show()
                self.errorLabel.adjustSize()


    def loadGraph(self, graph_type: str):
        self.currentGraph = graph_type
        self.plot_graph(graph_type)
        self.stackedWidget.setCurrentIndex(2)


    def plot_graph(self, graph_type):

        self.timer.start(1000)
        
        match graph_type:
            case "batt":
                times, values = get_batt_history(self.conexion_db)
                title = "Time vs Battery"
                value = "Battery"
            case "temp":
                times, values = get_temp_history(self.conexion_db)
                title = "Time vs Temperature"
                value = "Temperature"
            case "pres":
                times, values = get_pres_history(self.conexion_db)
                title = "Time vs Pressure"
                value = "Pressure"
            case "hum":
                times, values = get_hum_history(self.conexion_db)
                title = "Time vs Humidity"
                value = "Humidity"
            case "co":
                times, values = get_co_history(self.conexion_db)
                title = "Time vs Co"
                value = "Co"
            case "amp_x":
                times, values = get_amp_x_history(self.conexion_db)
                title = "Time vs X-Amplitude"
                value = "X-Amplitude"
            case "amp_y":
                times, values = get_amp_y_history(self.conexion_db)
                title = "Time vs Y-Amplitude"
                value = "Y-Amplitude"
            case "amp_z":
                times, values = get_amp_z_history(self.conexion_db)
                title = "Time vs Z-Amplitude"
                value = "Z-Amplitude"
            case "freq_x":
                times, values = get_freq_x_history(self.conexion_db)
                title = "Time vs X-Frequency"
                value = "X-Frequency"
            case "freq_y":
                times, values = get_freq_y_history(self.conexion_db)
                title = "Time vs Y-Frequency"
                value = "Y-Frequency"
            case "freq_z":
                times, values = get_freq_z_history(self.conexion_db)
                title = "Time vs Z-Frequency"
                value = "Z-Frequency"
            case "rms":
                times, values = get_rms_history(self.conexion_db)
                title = "Time vs RMS"
                value = "RMS"

        for i in reversed(range(self.graph_layout.count())):
            widget = self.graph_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Add the new plot
        chart = Canvas(self.page_12, times, values, title, value)
        self.graph_layout.addWidget(chart)


    def connectBluetooth(self):
        update_gui_conf(1)
    
    def disconnectBluetooth(self):
        update_gui_conf(0)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())