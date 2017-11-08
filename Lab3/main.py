import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

from rawsock import send_packet

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'IP traffic generator'
        self.left = 10
        self.top = 10
        self.width = 400
        self.height = 200
        self.initUI()


    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)


        #Labels
        self.layout_sip = QLabel('Source ip', self)
        self.layout_sip.move(5,15)

        self.layout_sp = QLabel('Source port', self)
        self.layout_sp.move(5,45)

        self.layout_dip = QLabel('Destination ip', self)
        self.layout_dip.move(5,75)

        self.layout_dp = QLabel('Destination port', self)
        self.layout_dp.move(5,105)




        # Source ip
        self.sip_textbox = QLineEdit(self)
        self.sip_textbox.move(100, 20)
        self.sip_textbox.resize(200, 20)

        # Source port
        self.sp_textbox = QLineEdit(self)
        self.sp_textbox.move(100, 50)
        self.sp_textbox.resize(60, 20)


        # Destination ip
        self.dip_textbox = QLineEdit(self)
        self.dip_textbox.move(100, 80)
        self.dip_textbox.resize(200, 20)

        # Destination port
        self.dp_textbox = QLineEdit(self)
        self.dp_textbox.move(100, 110)
        self.dp_textbox.resize(60, 20)




        # Create a button in the window
        self.button = QPushButton('Send', self)
        self.button.move(20, 160)

        # connect button to function on_click
        self.button.clicked.connect(self.on_click)
        self.show()

    @pyqtSlot()
    def on_click(self):
        try:
            send_packet(self.sip_textbox.text(), self.sp_textbox.text(), self.dip_textbox.text(), self.dp_textbox.text())
        except:
            QMessageBox.question(self, 'ERROR!', "Bad Input Data!", QMessageBox.Ok,
                             QMessageBox.Ok)
            self.sip_textbox.setText("")
            self.sp_textbox.setText("")
            self.dip_textbox.setText("")
            self.dp_textbox.setText("")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
