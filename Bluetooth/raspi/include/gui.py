from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(200, 200, 600, 600)
        self.setWindowTitle("Bluetooth IOT")
        self.initUI()

    def initUI(self):
        self.label = QtWidgets.QLabel(self)
        self.label.setText("Hello world")
        self.label.move(300,300)

        self.b1 = QtWidgets.QPushButton(self)
        self.b1.setText("a")
        self.b1.clicked.connect(self.clicked)


    def clicked(self):
        self.label.setText("sexoooo")
        self.update()
    
    def update(self):
        self.label.adjustSize()

def main():
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())


main()