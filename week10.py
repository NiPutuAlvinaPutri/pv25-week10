import sys
import csv
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog
)

class CRUDApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Book Manager - Ni Putu Alvina Putri (F1D022017)")
        self.setGeometry(100, 100, 800, 600)

        self.conn = sqlite3.connect("books.db")
        self.c = self.conn.cursor()
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                category TEXT,
                year INTEGER
            )
        """)
        self.conn.commit()

        self.initUI()
        self.load_data()

    def initUI(self):
        widget = QWidget()
        layout = QVBoxLayout()

        form_layout = QHBoxLayout()
        self.title_input = QLineEdit()
        self.category_input = QLineEdit()
        self.year_input = QLineEdit()

        form_layout.addWidget(QLabel("Title:"))
        form_layout.addWidget(self.title_input)
        form_layout.addWidget(QLabel("Category:"))
        form_layout.addWidget(self.category_input)
        form_layout.addWidget(QLabel("Year:"))
        form_layout.addWidget(self.year_input)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_data)
        form_layout.addWidget(self.save_button)

        layout.addLayout(form_layout)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by title...")
        self.search_input.textChanged.connect(self.search_data)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Category", "Year"])
        self.table.cellChanged.connect(self.edit_data)
        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_data)
        self.export_button = QPushButton("Export to CSV")
        self.export_button.clicked.connect(self.export_to_csv)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.export_button)

        layout.addLayout(button_layout)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def save_data(self):
        title = self.title_input.text()
        category = self.category_input.text()
        year = self.year_input.text()

        if title and category and year.isdigit():
            self.c.execute("INSERT INTO books (title, category, year) VALUES (?, ?, ?)",
                           (title, category, int(year)))
            self.conn.commit()
            self.clear_inputs()
            self.load_data()
        else:
            QMessageBox.warning(self, "Input Error", "Please enter valid data.")

    def clear_inputs(self):
        self.title_input.clear()
        self.category_input.clear()
        self.year_input.clear()

    def load_data(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        self.c.execute("SELECT * FROM books")
        for row_data in self.c.fetchall():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                if col == 0:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, col, item)
        self.table.blockSignals(False)

    def search_data(self):
        keyword = self.search_input.text()
        self.table.setRowCount(0)
        self.c.execute("SELECT * FROM books WHERE title LIKE ?", (f"%{keyword}%",))
        for row_data in self.c.fetchall():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, data in enumerate(row_data):
                self.table.setItem(row, col, QTableWidgetItem(str(data)))

    def edit_data(self, row, col):
        id_item = self.table.item(row, 0)
        new_value = self.table.item(row, col).text()
        field = ["id", "title", "category", "year"][col]
        if field == "year" and not new_value.isdigit():
            QMessageBox.warning(self, "Edit Error", "Year must be a number.")
            self.load_data()
            return
        self.c.execute(f"UPDATE books SET {field} = ? WHERE id = ?", (new_value, id_item.text()))
        self.conn.commit()

    def delete_data(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            id_item = self.table.item(selected_row, 0)
            self.c.execute("DELETE FROM books WHERE id = ?", (id_item.text(),))
            self.conn.commit()
            self.load_data()
        else:
            QMessageBox.warning(self, "Delete Error", "Please select a row to delete.")

    def export_to_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if path:
            with open(path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                headers = ["ID", "Title", "Category", "Year"]
                writer.writerow(headers)
                self.c.execute("SELECT * FROM books")
                for row in self.c.fetchall():
                    writer.writerow(row)
            QMessageBox.information(self, "Export Success", f"Data exported to {path}")

if __name__ == '__main__':
    from PyQt5.QtCore import Qt
    app = QApplication(sys.argv)
    window = CRUDApp()
    window.show()
    sys.exit(app.exec_())
