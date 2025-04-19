import sys
import time
import re
import os
import json
import threading
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QBrush
import pygame

# === LOAD CONFIG === #

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
SOUND_FILE = os.path.join(BASE_DIR, "notification.mp3")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

LOG_FILE = config.get("log_file")
CURRENCY_COLOR_MAP = config.get("currency_color_map", {})

# === UI + MONITORING === #

FONT_SIZE = 15

pattern = re.compile(r'@From .*?: Hi, I would like to buy your (.*) listed for (.*?) in')
pygame.mixer.init()

class TradeNotifier(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PoE Trade Notifier")
        self.setGeometry(100, 100, 600, 350)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self.layout = QVBoxLayout()
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Item", "Price"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        font = QFont()
        font.setPointSize(FONT_SIZE)
        self.table.setFont(font)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_trades)

        self.layout.addWidget(self.table)
        self.layout.addWidget(self.clear_button)
        self.setLayout(self.layout)
        self.show()

    def add_trade(self, item, price):
        self.table.insertRow(0)

        item_cell = QTableWidgetItem(item)
        price_cell = QTableWidgetItem(price)

        price_lower = price.lower()
        for key, color in CURRENCY_COLOR_MAP.items():
            if key in price_lower:
                brush = QBrush(QColor(color))
                price_cell.setForeground(brush)
                break

        self.table.setItem(0, 0, item_cell)
        self.table.setItem(0, 1, price_cell)

    def clear_trades(self):
        self.table.setRowCount(0)

    def play_sound(self):
        if os.path.exists(SOUND_FILE):
            pygame.mixer.music.load(SOUND_FILE)
            pygame.mixer.music.play()

def follow(file):
    file.seek(0, os.SEEK_END)
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.5)
            continue
        yield line

def monitor_logs(window):
    with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as logfile:
        loglines = follow(logfile)
        for line in loglines:
            match = pattern.search(line)
            if match:
                item, price = match.groups()
                window.play_sound()
                window.add_trade(item.strip(), price.strip())

def main():
    app = QApplication(sys.argv)
    notifier = TradeNotifier()

    thread = threading.Thread(target=monitor_logs, args=(notifier,), daemon=True)
    thread.start()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
