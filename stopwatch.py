import sys
import csv
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QListWidget, QListWidgetItem, QInputDialog,
                             QDialog, QFormLayout, QStackedWidget)
from PyQt6.QtCore import QTimer, Qt, QElapsedTimer
from PyQt6.QtGui import QFont, QColor, QPalette

class Stopwatch(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.session_title = ""
        self.session_description = ""
        self.tasks = ["Wasting Time"]
        self.task_timers = {"Wasting Time": 0}
        self.current_task = None
        self.task_timer = QElapsedTimer()
        
    def initUI(self):
        self.setWindowTitle('Stopwatch')
        self.setGeometry(300, 300, 600, 800)
        
        # Set dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton, QLineEdit, QListWidget {
                background-color: #3d3d3d;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 10px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QListWidget::item:selected {
                background-color: #4d4d4d;
            }
        """)
        self.setContentsMargins(20, 20, 20, 20)
        
        # Create widgets
        self.time_label = QLabel('00:00:00')
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont('Arial', 36)
        font.setBold(True)
        self.time_label.setFont(font)
        
        self.start_stop_button = QPushButton('Start')
        self.split_button = QPushButton('Split')
        self.split_button.setEnabled(False)
        self.end_session_button = QPushButton('End Session')
        self.end_session_button.setEnabled(False)
        self.new_session_button = QPushButton('Start New Session')
        self.view_sessions_button = QPushButton('View Sessions')
        
        self.split_list = QListWidget()
        self.task_list = QListWidget()
        self.add_task_button = QPushButton('+')
        self.add_task_button.clicked.connect(self.addTask)
        
        # Create layouts
        button_layout1 = QHBoxLayout()
        button_layout1.addWidget(self.start_stop_button)
        button_layout1.addSpacing(10)
        button_layout1.addWidget(self.split_button)
        button_layout1.addSpacing(10)
        button_layout1.addWidget(self.end_session_button)
        
        button_layout2 = QHBoxLayout()
        button_layout2.addWidget(self.new_session_button)
        button_layout2.addWidget(self.view_sessions_button)
        
        split_layout = QVBoxLayout()
        split_layout.addWidget(QLabel("Splits"))
        split_layout.addWidget(self.split_list)
        
        task_layout = QVBoxLayout()
        task_layout.addWidget(QLabel("Tasks"))
        task_layout.addWidget(self.task_list)
        task_layout.addWidget(self.add_task_button)
        
        list_layout = QVBoxLayout()
        list_layout.addLayout(split_layout)
        list_layout.addLayout(task_layout)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.time_label)
        main_layout.addLayout(button_layout1)
        main_layout.addLayout(button_layout2)
        main_layout.addLayout(list_layout)
        
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
        self.end_session_button.clicked.connect(self.endSession)
        self.new_session_button.clicked.connect(self.newSession)
        self.view_sessions_button.clicked.connect(self.viewSessions)
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Set up keyboard shortcuts
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def startStop(self):
        if not self.running:
            if self.time == 0 and not self.session_title:
                self.getSessionInfo()
            if self.session_title:
                self.timer.start(10)  # Update every 10ms for smoother display
                self.running = True
                self.start_stop_button.setText('Stop')
                self.split_button.setEnabled(True)
                self.end_session_button.setEnabled(True)
                if self.current_task:
                    self.task_timer.start()
        else:
            self.timer.stop()
            self.running = False
            self.start_stop_button.setText('Start')
            self.split_button.setEnabled(False)
            self.end_session_button.setEnabled(True)
            if self.current_task:
                self.task_timers[self.current_task] += self.task_timer.elapsed()
        
    def updateTime(self):
        self.time += 10  # Increment by 10ms
        self.updateDisplay()
        self.updateTaskDurations()
        
    def updateDisplay(self):
        time_str = self.formatTime(self.time)
        self.time_label.setText(time_str)
        
    def split(self):
        current_split = self.time - self.split_time
        self.split_time = self.time
        split_str = self.formatDuration(current_split)
        total_str = self.formatDuration(self.time)
        
        description, ok = QInputDialog.getText(self, 'Split Description', 'Enter split description:')
        if ok:
            split_item = QListWidgetItem(f'Split {len(self.splits) + 1}: {split_str} (Total: {total_str}) - {description}')
            self.split_list.addItem(split_item)
            self.splits.append((current_split, self.time, description))
            split_item.setData(Qt.ItemDataRole.UserRole, description)
        
        self.split_list.itemDoubleClicked.connect(self.editSplitDescription)

    def editSplitDescription(self, item):
        current_text = item.text()
        split_parts = current_text.split(' - ')
        current_description = split_parts[-1] if len(split_parts) > 1 else ""
        
        new_description, ok = QInputDialog.getText(self, 'Edit Split Description', 'Enter new description:', text=current_description)
        if ok:
            new_text = f"{' - '.join(split_parts[:-1])} - {new_description}"
            item.setText(new_text)
            item.setData(Qt.ItemDataRole.UserRole, new_description)
            
            # Update the description in self.splits
            split_index = self.split_list.row(item)
            self.splits[split_index] = (*self.splits[split_index][:2], new_description)
        
    def endSession(self):
        self.timer.stop()
        self.running = False
        self.start_stop_button.setText('Start')
        self.split_button.setEnabled(False)
        self.end_session_button.setEnabled(False)
        
        if self.session_title:
            self.saveSession()
            self.time = 0
            self.split_time = 0
            self.splits = []
            self.split_list.clear()
            self.updateDisplay()
            self.session_title = ""
            self.session_description = ""
        
    def newSession(self):
        self.endSession()
        self.getSessionInfo()
        
    def formatTime(self, ms):
        hours, remainder = divmod(ms, 3600000)
        minutes, remainder = divmod(remainder, 60000)
        seconds, milliseconds = divmod(remainder, 1000)
        return f'{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}'

    def getSessionInfo(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("New Session")
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        title_input = QLineEdit()
        description_input = QLineEdit()
        form_layout.addRow("Session Title:", title_input)
        form_layout.addRow("Session Description:", description_input)
        layout.addLayout(form_layout)
        
        task_label = QLabel("Tasks:")
        layout.addWidget(task_label)
        
        task_list = QListWidget()
        layout.addWidget(task_list)
        
        add_task_button = QPushButton("Add Task")
        layout.addWidget(add_task_button)
        
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        def add_task():
            task, ok = QInputDialog.getText(dialog, "Add Task", "Enter task:")
            if ok and task:
                task_list.addItem(task)
        
        add_task_button.clicked.connect(add_task)
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.session_title = title_input.text()
            self.session_description = description_input.text()
            self.tasks = [task_list.item(i).text() for i in range(task_list.count())]
            if "Wasting Time" not in self.tasks:
                self.tasks.append("Wasting Time")
            self.task_timers = {task: 0 for task in self.tasks}  # Initialize task timers
            self.updateTaskList()

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

    def updateTaskList(self):
        self.task_list.clear()
        for task in self.tasks:
            item = QListWidgetItem(task)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setData(Qt.ItemDataRole.UserRole, task)
            self.task_list.addItem(item)
        
        if self.tasks and not self.current_task:
            self.selectTask(self.task_list.item(0))
        
        self.task_list.itemClicked.connect(self.selectTask)
        self.task_list.itemChanged.connect(self.taskChanged)
        

    def addTask(self):
        task, ok = QInputDialog.getText(self, "Add Task", "Enter new task:")
        if ok and task:
            self.tasks.append(task)
            self.task_timers[task] = 0
            self.updateTaskList()
            if not self.current_task:
                self.selectTask(self.task_list.item(self.task_list.count() - 1))

    def selectTask(self, item):
        if self.current_task:
            self.task_timers[self.current_task] += self.task_timer.elapsed()
            prev_items = self.task_list.findItems(self.current_task, Qt.MatchFlag.MatchContains)
            if prev_items:
                prev_item = prev_items[0]
                prev_item.setBackground(QColor(0, 0, 0, 0))
                prev_item.setText(prev_item.text().replace(" (working)", ""))
        
        self.current_task = item.text().split(' - ')[0]
        self.task_timer.restart()
        item.setBackground(QColor(144, 238, 144, 100))  # Light green
        item.setText(f"{self.current_task} - {self.formatDuration(self.task_timers[self.current_task])} (working)")
        
        self.updateTaskDurations()

    def updateTaskDurations(self):
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            task = item.data(Qt.ItemDataRole.UserRole)
            if task is not None and task in self.task_timers:
                duration = self.task_timers[task]
                if task == self.current_task and self.running:
                    duration += self.task_timer.elapsed()
                item.setText(f"{task} - {self.formatDuration(duration)}")

    def formatDuration(self, ms):
        seconds = ms // 1000
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours}h{minutes:02d}m{seconds:02d}s"
        elif minutes > 0:
            return f"{minutes}m{seconds:02d}s"
        else:
            return f"{seconds}s"

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.startStop()
        elif event.key() == Qt.Key.Key_Tab:
            self.split()
        elif event.key() == Qt.Key.Key_Escape:
            self.endSession()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            current_item = self.task_list.currentItem()
            if current_item:
                self.selectTask(current_item)
                current_item.setBackground(QColor(144, 238, 144, 100))  # Light green
                if current_item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                    current_item.setCheckState(Qt.CheckState.Checked)
        super().keyPressEvent(event)

    def taskChanged(self, item):
        if item.checkState() == Qt.CheckState.Checked:
            item.setBackground(QColor(144, 238, 144, 100))  # Light green
        else:
            item.setBackground(QColor(0, 0, 0, 0))  # Transparent

        # Update task name in self.tasks and self.task_timers
        old_task = item.data(Qt.ItemDataRole.UserRole)
        new_task = item.text().split(' - ')[0]
        if old_task != new_task:
            self.tasks[self.tasks.index(old_task)] = new_task
            self.task_timers[new_task] = self.task_timers.pop(old_task)
            item.setData(Qt.ItemDataRole.UserRole, new_task)
            if self.current_task == old_task:
                self.current_task = new_task

if __name__ == '__main__':
    app = QApplication(sys.argv)
    stopwatch = Stopwatch()
    stopwatch.show()
    sys.exit(app.exec())
