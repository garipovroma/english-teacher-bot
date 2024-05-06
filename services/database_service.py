import sqlite3

class DatabaseService:
    def __init__(self, db_file):
        self.db_file = db_file
        self.create_tables()

    def create_tables(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        c.execute("""CREATE TABLE IF NOT EXISTS topic_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )""")

        c.execute("""CREATE TABLE IF NOT EXISTS topics (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    category_id INTEGER NOT NULL,
                    FOREIGN KEY (category_id) REFERENCES topic_categories(id)
                )""")

        c.execute("""CREATE TABLE IF NOT EXISTS exercises (
                    id INTEGER PRIMARY KEY,
                    topic_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    FOREIGN KEY (topic_id) REFERENCES topics(id)
                )""")
        
        c.execute("""CREATE TABLE IF NOT EXISTS theory_cards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_id INTEGER,
                    theory TEXT NOT NULL,
                    FOREIGN KEY (topic_id) REFERENCES topics(id)
                )""")

        conn.commit()
        conn.close()

    def add_category(self, name):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("INSERT INTO topic_categories (name) VALUES (?) ON CONFLICT(name) DO NOTHING", (name,))
        conn.commit()
        category_id = c.lastrowid
        conn.close()
        return category_id

    def add_topic(self, name, description, category_id):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("INSERT INTO topics (name, description, category_id) VALUES (?, ?, ?)", (name, description, category_id))
        conn.commit()
        conn.close()
    
    def get_theory_card_by_topic_id(self, topic_id):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        c.execute("SELECT theory FROM theory_cards WHERE topic_id = ?", (topic_id,))
        card = c.fetchone()

        conn.close()
        return card

    def get_all_topics(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        c.execute("SELECT (id, name) FROM topics")
        topics = c.fetchall()

        conn.close()
        return topics

    def get_topic_by_name(self, name):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("INSERT INTO theory_cards (topic_id, theory) VALUES (?, ?)", (topic_id, theory))
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

    def get_all_topics(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        c.execute("SELECT * FROM topics")
        topics = c.fetchall()

        conn.close()
        return topics