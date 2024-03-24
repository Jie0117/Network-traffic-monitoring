import sys
import psutil
import subprocess
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QComboBox, QWidget, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import QTimer

class NetworkMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.last = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        self.total_bytes = 0  # 定義 total_bytes 變數
        self.daily_limit = 1024 * 1024 * 1024  # 默认每日流量上限为1GB
        self.current_date = datetime.now().date()
        self.reset_time = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=1)
        self.time_until_reset = self.reset_time - datetime.now()
        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self.monitor_network_usage)
        self.monitor_timer.start(1000)  # 每1秒执行一次
        self.reset_timer = QTimer(self)
        self.reset_timer.timeout.connect(self.check_reset_time)
        self.reset_timer.start(1000)  # 每1秒检查一次是否需要重置

    def initUI(self):
        self.setWindowTitle('Network Monitor')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.label1 = QLabel('Select Network Type:')
        self.dropdown1 = QComboBox()
        self.dropdown1.addItem('Wi-Fi')
        self.dropdown1.addItem('Ethernet')
        

        self.label2 = QLabel('Enter Daily Limit:')
        self.input = QLineEdit()
        self.dropdown2 = QComboBox()
        self.dropdown2.addItem('KB')
        self.dropdown2.addItem('MB')
        self.dropdown2.addItem('GB')
        self.dropdown2.addItem('TB')
        

        self.button = QPushButton('Set Limit')
        self.button.clicked.connect(self.set_daily_limit)

        self.label3 = QLabel('Current Usage: 0%')

        layout.addWidget(self.label1)
        layout.addWidget(self.dropdown1)
        layout.addWidget(self.label2)
        layout.addWidget(self.input)
        layout.addWidget(self.dropdown2)
        layout.addWidget(self.button)
        layout.addWidget(self.label3)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def set_daily_limit(self):
        limit_value = float(self.input.text())
        limit_unit = self.dropdown2.currentText()
        if limit_unit == 'KB':
            self.daily_limit = limit_value * 1024
        elif limit_unit == 'MB':
            self.daily_limit = limit_value * 1024 * 1024
        elif limit_unit == 'GB':
            self.daily_limit = limit_value * 1024 * 1024 * 1024
        elif limit_unit == 'TB':
            self.daily_limit = limit_value * 1024 * 1024 * 1024 * 1024
        #print(f'Daily limit set to {self.daily_limit} bytes')
        self.reset_daily_usage()

    def reset_daily_usage(self):
        subprocess.run(["netsh", "interface", "set", "interface", self.dropdown1.currentText(), "ENABLED"])
        self.current_date = datetime.now().date()
        self.reset_time = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=1)
        self.time_until_reset = self.reset_time - datetime.now()

    def check_reset_time(self):
        current_time = datetime.now()
        if current_time >= self.reset_time:
            self.reset_daily_usage()
            self.monitor_timer.start(1000)  # 重启监控定时器

    def monitor_network_usage(self):
        
        current_bytes_sent = psutil.net_io_counters().bytes_sent
        current_bytes_recv = psutil.net_io_counters().bytes_recv
        now = current_bytes_sent + current_bytes_recv
        self.total_bytes += float(now - self.last)
        #print(self.total_bytes)
        self.last = now
        usage_percent = (self.total_bytes / self.daily_limit) * 100

        if self.total_bytes > self.daily_limit:
            #print("Daily limit reached. Disconnecting network...")
            subprocess.run(["netsh", "interface", "set", "interface", self.dropdown1.currentText(), "DISABLED"])
            self.monitor_timer.stop()  # 停止监控定时器
            QMessageBox.warning(self, 'Daily Limit Reached', 'The daily network usage limit has been reached.')
        else:
            #print("Total bytes:", self.total_bytes)
            self.label3.setText(f'Current Usage: {usage_percent:.2f}%')

if __name__ == '__main__':
    app = QApplication([])
    monitor = NetworkMonitor()
    monitor.show()
    sys.exit(app.exec_())
