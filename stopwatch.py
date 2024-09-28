import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QPalette, QColor

class Stopwatch(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Stopwatch')
        self.setGeometry(300, 300, 400, 500)
        
        # Set dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: none;
                padding: 10px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QTextEdit {
                background-color: #3d3d3d;
                color: #ffffff;
                border: none;
            }
        """)
        
        # Create widgets
        self.time_label = QLabel('00:00:00.000')
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setFont(QFont('Arial', 24))
        
        self.split_label = QLabel('Last Split: 00:00:00.000')
        self.split_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.start_stop_button = QPushButton('Start')
        self.split_button = QPushButton('Split')
        self.split_button.setEnabled(False)
        
        self.description = QTextEdit()
        self.description.setPlaceholderText("Describe what was done in this time...")
        
        # Create layouts
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_stop_button)
        button_layout.addWidget(self.split_button)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.time_label)
        main_layout.addWidget(self.split_label)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.description)
        
        self.setLayout(main_layout)
        
        # Set up timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTime)
        self.time = 0
        self.running = False
        self.split_time = 0
        
        # Connect buttons
        self.start_stop_button.clicked.connect(self.startStop)
        self.split_button.clicked.connect(self.split)
        
    def startStop(self):
        if not self.running:
            self.timer.start(1)
            self.running = True
            self.start_stop_button.setText('Stop')
            self.split_button.setEnabled(True)
        else:
            self.timer.stop()
            self.running = False
            self.start_stop_button.setText('Start')
            self.split_button.setEnabled(False)
        
    def updateTime(self):
        self.time += 1
        self.updateDisplay()
        
    def updateDisplay(self):
        time_str = self.formatTime(self.time)
        self.time_label.setText(time_str)
        
    def split(self):
        current_split = self.time - self.split_time
        self.split_time = self.time
        split_str = self.formatTime(current_split)
        total_str = self.formatTime(self.time)
        self.split_label.setText(f'Last Split: {split_str} (Total: {total_str})')
        
    def formatTime(self, ms):
        hours, remainder = divmod(ms, 3600000)
        minutes, remainder = divmod(remainder, 60000)
        seconds, milliseconds = divmod(remainder, 1000)
        return f'{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}'

if __name__ == '__main__':
    app = QApplication(sys.argv)
    stopwatch = Stopwatch()
    stopwatch.show()
    sys.exit(app.exec())
