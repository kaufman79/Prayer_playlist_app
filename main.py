import sys
import sqlite3
import random
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout


# Database setup
def init_db():
    conn = sqlite3.connect("prayers.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS people (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        last_prayed TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS prayer_topics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        person_id INTEGER,
                        topic TEXT,
                        FOREIGN KEY (person_id) REFERENCES people(id))''')
    conn.commit()
    conn.close()


class PrayerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prayer App")
        self.setGeometry(100, 100, 400, 400)
        self.layout = QVBoxLayout()

        self.label_name = QLabel("Click Next to begin")
        self.label_topic = QLabel("")
        self.label_last_prayed = QLabel("")

        self.button_next = QPushButton("Next Prayer")
        self.button_next.clicked.connect(self.load_next_prayer)

        self.button_prayed = QPushButton("Mark as Prayed")
        self.button_prayed.clicked.connect(self.mark_as_prayed)

        self.name_input = QLineEdit()
        self.topic_input = QLineEdit()
        self.button_add = QPushButton("Add Prayer")
        self.button_add.clicked.connect(self.add_prayer)

        self.button_delete = QPushButton("Delete Prayer")
        self.button_delete.clicked.connect(self.delete_prayer)

        form_layout = QFormLayout()
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Prayer Topic:", self.topic_input)

        self.layout.addWidget(self.label_name)
        self.layout.addWidget(self.label_topic)
        self.layout.addWidget(self.label_last_prayed)
        self.layout.addWidget(self.button_next)
        self.layout.addWidget(self.button_prayed)
        self.layout.addLayout(form_layout)
        self.layout.addWidget(self.button_add)
        self.layout.addWidget(self.button_delete)

        self.setLayout(self.layout)
        self.current_prayer = None
        self.load_next_prayer()

    def get_prayers(self):
        conn = sqlite3.connect("prayers.db")
        cursor = conn.cursor()
        cursor.execute('''SELECT people.id, people.name, prayer_topics.topic, people.last_prayed 
                          FROM people 
                          JOIN prayer_topics ON people.id = prayer_topics.person_id''')
        prayers = cursor.fetchall()
        conn.close()
        return prayers

    def load_next_prayer(self):
        prayers = self.get_prayers()
        if prayers:
            self.current_prayer = random.choice(prayers)
            self.label_name.setText(f"{self.current_prayer[1]}")
            self.label_topic.setText(f"Prayer Request: {self.current_prayer[2]}")
            self.label_last_prayed.setText(
                f"Last Prayed: {self.current_prayer[3] if self.current_prayer[3] else 'Never'}")
        else:
            self.label_name.setText("No prayers available")
            self.label_topic.setText("")
            self.label_last_prayed.setText("")

    def mark_as_prayed(self):
        if self.current_prayer:
            conn = sqlite3.connect("prayers.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE people SET last_prayed = DATE('now') WHERE id = ?", (self.current_prayer[0],))
            conn.commit()
            conn.close()
            self.load_next_prayer()

    def add_prayer(self):
        name = self.name_input.text()
        topic = self.topic_input.text()
        if name and topic:
            conn = sqlite3.connect("prayers.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO people (name, last_prayed) VALUES (?, NULL)", (name,))
            person_id = cursor.lastrowid
            cursor.execute("INSERT INTO prayer_topics (person_id, topic) VALUES (?, ?)", (person_id, topic))
            conn.commit()
            conn.close()
            self.name_input.clear()
            self.topic_input.clear()
            self.load_next_prayer()

    def delete_prayer(self):
        if self.current_prayer:
            conn = sqlite3.connect("prayers.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM prayer_topics WHERE person_id = ?", (self.current_prayer[0],))
            cursor.execute("DELETE FROM people WHERE id = ?", (self.current_prayer[0],))
            conn.commit()
            conn.close()
            self.load_next_prayer()


if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    window = PrayerApp()
    window.show()
    sys.exit(app.exec())
