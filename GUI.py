from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtCore import Qt, QTimer
import sys
import asyncio
from bleak import BleakClient
import struct
from queue import Queue
import joblib
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.label = QLabel("NORMAL", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.label)

        font = QFont()
        font.setPointSize(100)
        self.label.setFont(font)

        self.setWindowTitle("Fall Detection")
        self.setGeometry(100, 100, 400, 300)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_file)
        self.timer.start(100) 

    def keyPressEvent(self, event):
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('red'))
        self.setPalette(palette)
        
        self.label.setText("FALL")
        self.label.setStyleSheet("color: white")

    def check_file(self):
        try:
            with open("./FallDetected.txt", "r") as file:
                data = file.read().strip()
                if data == "0":
                    palette = self.palette()
                    palette.setColor(QPalette.Window, QColor('gray'))
                    self.setPalette(palette)

                    self.label.setText("NORMAL")
                    self.label.setStyleSheet("color: black")
                elif data == "1":
                    palette = self.palette()
                    palette.setColor(QPalette.Window, QColor('red'))
                    self.setPalette(palette)
        
                    self.label.setText("FALL")
                    self.label.setStyleSheet("color: white")
                else:
                    print("Unknown data value:", data)
        except FileNotFoundError:
            print("Data.txt file not found")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()