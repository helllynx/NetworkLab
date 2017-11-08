import sys
# from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget, QTableWidgetItem, QVBoxLayout, QLineEdit
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
from PyQt5 import QtCore
import PyQt5
import time

from pokcet_snif import receive_and_process


class Packet:
    def __init__(self, src_addr, dst_addr, prot, s_port, d_port, data):
        self.src_addr = src_addr
        self.dst_addr = dst_addr
        self.prot = prot
        self.s_port = s_port
        self.d_port = d_port
        self.data = data


class PacketSource(QObject):
    new_packet_signal = pyqtSignal(Packet)

    @pyqtSlot()
    def generate(self):
        while True:
            # src = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
            # dst = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
            # data = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(1024))
            # p = Packet(src, dst, data)
            # self.new_packet_signal.emit(p)
            time.sleep(1)
            src, dst, prot, s_port, d_port, data = receive_and_process()
            self.new_packet_signal.emit(Packet(src, dst, prot, s_port, d_port, data))


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = ''
        self.left = 0
        self.top = 0
        self.width = 900
        self.height = 650
        self.initUI()

        self.source_thread = QtCore.QThread(self)
        self.packet_source = PacketSource()
        self.packet_source.new_packet_signal.connect(self.new_packet)
        self.packet_source.moveToThread(self.source_thread)
        self.source_thread.started.connect(self.packet_source.generate)
        self.source_thread.start()

    def new_packet(self, packet):
        rowPosition = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rowPosition)

        src_item = QTableWidgetItem(packet.src_addr)
        dst_item = QTableWidgetItem(packet.dst_addr)
        prot = QTableWidgetItem(packet.prot)
        s_port = QTableWidgetItem(packet.s_port)
        d_port = QTableWidgetItem(packet.d_port)
        # put additional data in second item
        dst_item.packet_data = packet.data


        self.tableWidget.setItem(rowPosition, 0, src_item)
        self.tableWidget.setItem(rowPosition, 1, dst_item)
        self.tableWidget.setItem(rowPosition, 2, prot)
        self.tableWidget.setItem(rowPosition, 3, s_port)
        self.tableWidget.setItem(rowPosition, 4, d_port)


    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createTable()

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)

        self.textbox = QTextEdit(self)
        self.layout.addWidget(self.textbox)
        self.setLayout(self.layout)

        # Show widget
        self.show()

    def createTable(self):
        # Create table
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(5)

        self.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableWidget.setSizeAdjustPolicy(PyQt5.QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tableWidget.clicked.connect(self.on_click)
        self.tableWidget.resizeColumnsToContents()

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, PyQt5.QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, PyQt5.QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, PyQt5.QtWidgets.QHeaderView.Stretch)

    @pyqtSlot()
    def on_click(self):
        row = self.tableWidget.selectionModel().selectedRows()[0].row()
        self.textbox.setText(self.tableWidget.item(row, 1).packet_data)


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        ex = App()
        sys.exit(app.exec_())
    except KeyboardInterrupt:
            # pprint.pprint(packet_stats)
        pass