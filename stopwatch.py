import sys
import csv
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QListWidget, QListWidgetItem, QInputDialog,
                             QDialog, QFormLayout, QStackedWidget)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont

class Stopwatch(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.session_title = ""
        self.session_description = ""
        
    def initUI(self):
        self.setWindowTitle('Stopwatch')
        self.setGeometry(300, 300, 500, 600)
        
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
            QLineEdit, QListWidget {
                background-color: #3d3d3d;
                color: #ffffff;
                border: none;
            }
        """)
        
        # Create widgets
        self.time_label = QLabel('00:00:00.000')
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setFont(QFont('Arial', 24))
        
        self.start_stop_button = QPushButton('Start')
        self.split_button = QPushButton('Split')
        self.split_button.setEnabled(False)
        self.new_session_button = QPushButton('Start New Session')
        self.view_sessions_button = QPushButton('View Sessions')
        
        self.split_list = QListWidget()
        
        # Create layouts
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_stop_button)
        button_layout.addWidget(self.split_button)
        button_layout.addWidget(self.new_session_button)
        button_layout.addWidget(self.view_sessions_button)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.time_label)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.split_list)
        
        self.setLayout(main_layout)
        
        # Set up timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTime)
        self.time = 0
        self.running = False
        self.split_time = 0
        self.splits = []
        
        # Connect buttons
        self.start_stop_button.clicked.connect(self.startStop)
        self.split_button.clicked.connect(self.split)
        self.new_session_button.clicked.connect(self.newSession)
        self.view_sessions_button.clicked.connect(self.viewSessions)
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
    def startStop(self):
        if not self.running:
            if self.time == 0 and not self.session_title:
                self.getSessionInfo()
            if self.session_title:
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
        
        description, ok = QInputDialog.getText(self, 'Split Description', 'Enter split description:')
        if ok:
            split_item = QListWidgetItem(f'Split {len(self.splits) + 1}: {split_str} (Total: {total_str}) - {description}')
            self.split_list.addItem(split_item)
            self.splits.append((current_split, self.time, description))
        
    def endSession(self):
        self.timer.stop()
        self.running = False
        self.start_stop_button.setText('Start')
        self.split_button.setEnabled(False)
        
        title, ok = QInputDialog.getText(self, 'Session Title', 'Enter session title:')
        if ok:
            description, ok = QInputDialog.getText(self, 'Session Description', 'Enter session description:')
            if ok:
                session_item = QListWidgetItem(f'Session: {title} - {description}')
                self.split_list.insertItem(0, session_item)
        
    def newSession(self):
        if self.running:
            self.timer.stop()
            self.running = False
        self.saveSession()
        self.time = 0
        self.split_time = 0
        self.splits = []
        self.split_list.clear()
        self.updateDisplay()
        self.session_title = ""
        self.session_description = ""
        self.start_stop_button.setText('Start')
        self.split_button.setEnabled(False)
        
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
    def getSessionInfo(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("New Session")
        layout = QFormLayout()
        title_input = QLineEdit()
        description_input = QLineEdit()
        layout.addRow("Session Title:", title_input)
        layout.addRow("Session Description:", description_input)
        buttons = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        layout.addRow(buttons)
        dialog.setLayout(layout)
        
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.session_title = title_input.text()
            self.session_description = description_input.text()
            self.split_list.addItem(f"Session: {self.session_title} - {self.session_description}")
    def saveSession(self):
        if self.session_title:
            filename = f"data/{self.session_title.replace(' ', '_')}.csv"
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Session Title", "Session Description", "Total Time"])
                writer.writerow([self.session_title, self.session_description, self.formatTime(self.time)])
                writer.writerow(["Split Number", "Split Time", "Total Time", "Description"])
                for i, (split_time, total_time, description) in enumerate(self.splits, 1):
                    writer.writerow([i, self.formatTime(split_time), self.formatTime(total_time), description])
    def viewSessions(self):
        sessions_dialog = QDialog(self)
        sessions_dialog.setWindowTitle("Saved Sessions")
        sessions_dialog.setGeometry(300, 300, 400, 300)
        
        sessions_list = QListWidget()
        details_label = QLabel("Select a session to view details")
        
        layout = QVBoxLayout()
        layout.addWidget(sessions_list)
        layout.addWidget(details_label)
        sessions_dialog.setLayout(layout)
        
        for filename in os.listdir('data'):
            if filename.endswith('.csv'):
                sessions_list.addItem(filename[:-4].replace('_', ' '))
        
        def show_session_details(item):
            filename = f"data/{item.text().replace(' ', '_')}.csv"
            with open(filename, 'r') as file:
                reader = csv.reader(file)
                session_info = next(reader)
                next(reader)  # Skip header row
                splits = list(reader)
            
            details = f"Session: {session_info[0]}\n"
            details += f"Description: {session_info[1]}\n"
            details += f"Total Time: {session_info[2]}\n\n"
            details += "Splits:\n"
            for split in splits:
                details += f"Split {split[0]}: {split[1]} (Total: {split[2]}) - {split[3]}\n"
            
            details_label.setText(details)
        
        sessions_list.itemClicked.connect(show_session_details)
        
        sessions_dialog.exec()
