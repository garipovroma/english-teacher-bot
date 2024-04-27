import sqlite3

class DatabaseService:
    def __init__(self, db_file):
        self.db_file = db_file
        self.create_tables()

    def create_tables(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        c.execute("""CREATE TABLE IF NOT EXISTS topics (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT
                )""")

        c.execute("""CREATE TABLE IF NOT EXISTS exercises (
                    id INTEGER PRIMARY KEY,
                    topic_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    FOREIGN KEY (topic_id) REFERENCES topics(id)
                )""")

        conn.commit()
        conn.close()

    def get_topic_by_name(self, name):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        c.execute("SELECT * FROM topics WHERE name = ?", (name,))
        topic = c.fetchone()

        conn.close()
        return topic

    def get_topic_by_id(self, topic_id):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        c.execute("SELECT * FROM topics WHERE id = ?", (topic_id,))
        topic = c.fetchone()

        conn.close()
        return topic

    def add_topic(self, name, description):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        c.execute("INSERT INTO topics (name, description) VALUES (?, ?)", (name, description))
        conn.commit()
        conn.close()

    def get_exercises_by_topic_id(self, topic_id):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        c.execute("SELECT * FROM exercises WHERE topic_id = ?", (topic_id,))
        exercises = c.fetchall()

        conn.close()
        return exercises

    def add_exercise(self, topic_id, name, description):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        c.execute("INSERT INTO exercises (topic_id, name, description) VALUES (?, ?, ?)", (topic_id, name, description))
        conn.commit()
        conn.close()