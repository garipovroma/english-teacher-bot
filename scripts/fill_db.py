import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.database_service import DatabaseService

def fill_db(db_file):
    db_service = DatabaseService(db_file)

    topics_csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'topics.csv'))
    topics_df = pd.read_csv(topics_csv_path)
    print(topics_df.columns)

    distinct_categories = topics_df['TOPIC_CATEGORY'].drop_duplicates()
    for category in distinct_categories:
        db_service.add_category(category)

    for index, row in topics_df.iterrows():
        topic = row['TOPIC']
        topic_category = row['TOPIC_CATEGORY']
        db_service.add_topic(topic, "EMPTY", topic_category)

    topics = db_service.get_all_topics()
    for topic in topics:
        topic_id = topic[0]
        for i in range(5):
            db_service.add_exercise(topic_id, f"Exercise {i+1}", "EMPTY")

    theory_cards_csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'theory_cards.csv'))
    theory_cards_df = pd.read_csv(theory_cards_csv_path)

    for index, row in theory_cards_df.iterrows():
        topic_name = row['TOPIC']
        theory = row['THEORY_CARD']
        
        topic = db_service.get_topic_by_name(topic_name)
        if topic:
            topic_id = topic[0]
            db_service.add_theory_card(topic_id, theory)

    print("Database filled and theory cards inserted successfully.")

if __name__ == "__main__":
    db_file = 'data.db'
    fill_db(db_file)
