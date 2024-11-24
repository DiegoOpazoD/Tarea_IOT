from real_menu import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets

def printHelloWorld():
    print("Hello World")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.connectBluetooth.clicked.connect(printHelloWorld)
    MainWindow.show()
    sys.exit(app.exec_())
    