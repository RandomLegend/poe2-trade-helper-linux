import sys
import time
import re
import os
import json
import threading
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QDialog, QDialogButtonBox, QLineEdit,
    QLabel, QHBoxLayout, QMenuBar, QColorDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QBrush
import pygame

# === CONFIG PATH SETUP === #
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "poe-trade-notifier")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
SOUND_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification.mp3")

# === INIT AUDIO + PATTERN === #
pygame.mixer.init()
FONT_SIZE = 15
pattern = re.compile(r'@From .*?: Hi, I would like to buy your (.*) listed for (.*?) in')


# === MAIN WINDOW === #

class TradeNotifier(QWidget):
    def __init__(self):
        super().__init__()
        self.log_file = ""
        self.currency_color_map = {}
        self.monitor_thread = None
        self.monitoring_active = False

        self.load_settings()
        self.init_ui()

        if self.log_file:
            self.restart_monitoring()

    def init_ui(self):
        self.setWindowTitle("PoE Trade Notifier")
        self.setGeometry(100, 100, 600, 350)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Menu bar
        self.menu_bar = QMenuBar(self)
        settings_menu = self.menu_bar.addMenu("Settings")
        open_settings_action = settings_menu.addAction("Configure")
        open_settings_action.triggered.connect(self.open_settings_dialog)
        main_layout.setMenuBar(self.menu_bar)

        # Trade table
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

        main_layout.addWidget(self.table)
        main_layout.addWidget(self.clear_button)
        self.show()

    def open_settings_dialog(self):
        dialog = SettingsDialog(self.log_file, self.currency_color_map)
        if dialog.exec():
            self.log_file, self.currency_color_map = dialog.get_settings()
            self.save_settings()
            self.restart_monitoring()

    def add_trade(self, item, price):
        self.table.insertRow(0)
        item_cell = QTableWidgetItem(item)
        price_cell = QTableWidgetItem(price)

        price_lower = price.lower()
        for key, color in self.currency_color_map.items():
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

    def restart_monitoring(self):
        self.monitoring_active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self.monitor_logs, daemon=True)
        self.monitor_thread.start()

    def monitor_logs(self):
        try:
            with open(self.log_file, "r", encoding="utf-8", errors="ignore") as logfile:
                logfile.seek(0, os.SEEK_END)
                while self.monitoring_active:
                    line = logfile.readline()
                    if not line:
                        time.sleep(0.5)
                        continue
                    match = pattern.search(line)
                    if match:
                        item, price = match.groups()
                        self.play_sound()
                        self.add_trade(item.strip(), price.strip())
        except Exception as e:
            print(f"[Monitor Error]: {e}")

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.log_file = data.get("log_file", "")
                    self.currency_color_map = data.get("currency_color_map", {})
            except Exception as e:
                print(f"Failed to load config: {e}")

    def save_settings(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        data = {
            "log_file": self.log_file,
            "currency_color_map": self.currency_color_map
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")


# === SETTINGS DIALOG === #

class SettingsDialog(QDialog):
    def __init__(self, current_log_file, current_map):
        super().__init__()
        self.setWindowTitle("Configure Settings")
        self.setModal(True)
        self.setMinimumWidth(500)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Log file path input
        path_layout = QHBoxLayout()
        self.log_path_input = QLineEdit(current_log_file)
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_log_file)
        path_layout.addWidget(QLabel("Log File Path:"))
        path_layout.addWidget(self.log_path_input)
        path_layout.addWidget(browse_button)
        self.layout.addLayout(path_layout)

        # Currency color map table
        self.color_table = QTableWidget(0, 2)
        self.color_table.setHorizontalHeaderLabels(["Currency (keyword)", "Color"])
        self.color_table.horizontalHeader().setStretchLastSection(True)
        self.color_table.cellDoubleClicked.connect(self.edit_color_cell)

        self.layout.addWidget(QLabel("Currency Color Map:"))
        self.layout.addWidget(self.color_table)

        for currency, color in current_map.items():
            self.add_row(currency, color)

        button_layout = QHBoxLayout()
        add_row_btn = QPushButton("Add Row")
        add_row_btn.clicked.connect(lambda: self.add_row("", ""))
        del_row_btn = QPushButton("Delete Selected")
        del_row_btn.clicked.connect(self.delete_selected_rows)
        button_layout.addWidget(add_row_btn)
        button_layout.addWidget(del_row_btn)
        self.layout.addLayout(button_layout)

        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def browse_log_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Log File")
        if file_path:
            self.log_path_input.setText(file_path)

    def add_row(self, currency, color):
        row = self.color_table.rowCount()
        self.color_table.insertRow(row)
        self.color_table.setItem(row, 0, QTableWidgetItem(currency))
        color_item = QTableWidgetItem(color)
        color_item.setForeground(QBrush(QColor(color)))
        self.color_table.setItem(row, 1, color_item)

    def delete_selected_rows(self):
        selected = self.color_table.selectedRanges()
        for r in reversed(selected):
            for row in range(r.topRow(), r.bottomRow() + 1):
                self.color_table.removeRow(row)

    def edit_color_cell(self, row, column):
        if column != 1:
            return
        current_item = self.color_table.item(row, column)
        current_color = QColor(current_item.text()) if current_item else QColor("white")
        color = QColorDialog.getColor(current_color, self, "Choose Color")
        if color.isValid():
            current_item.setText(color.name())
            current_item.setForeground(QBrush(color))

    def get_settings(self):
        log_path = self.log_path_input.text().strip()
        color_map = {}
        for row in range(self.color_table.rowCount()):
            currency_item = self.color_table.item(row, 0)
            color_item = self.color_table.item(row, 1)
            if currency_item and color_item:
                key = currency_item.text().strip().lower()
                val = color_item.text().strip()
                if key:
                    color_map[key] = val
        return log_path, color_map


# === MAIN ENTRY === #

def main():
    app = QApplication(sys.argv)
    notifier = TradeNotifier()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
