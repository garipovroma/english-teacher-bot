import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.database_service import DatabaseService
import sqlite3
import pytest

@pytest.fixture
def database_service():
    db_file = 'test.db'
    yield DatabaseService(db_file)
    os.remove(db_file)
    
def test_create_tables(database_service):
    database_service.create_tables()
    conn = sqlite3.connect(database_service.db_file)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = c.fetchall()
    assert ('topics',) in tables
    assert ('exercises',) in tables
    assert ('topic_categories',) in tables
    conn.close()

def test_add_and_get_category(database_service):
    category_id = database_service.add_category('Present and Past')
    assert category_id > 0  # Ensure a valid ID is returned

    # Checking if the category is correctly added
    conn = sqlite3.connect(database_service.db_file)
    c = conn.cursor()
    c.execute("SELECT * FROM topic_categories WHERE id = ?", (category_id,))
    category = c.fetchone()
    assert category == (category_id, 'Present and Past')
    conn.close()

def test_add_and_get_topic(database_service):
    category_id = database_service.add_category('Present and Past')
    database_service.add_topic('Verb Tenses', 'Practice using different verb tenses in English', category_id)
    topic = database_service.get_topic_by_name('Verb Tenses')
    assert topic == (1, 'Verb Tenses', 'Practice using different verb tenses in English', category_id)

    topic = database_service.get_topic_by_id(1)
    assert topic == (1, 'Verb Tenses', 'Practice using different verb tenses in English', category_id)

def test_add_and_get_exercises(database_service):
    category_id = database_service.add_category('Present and Past')
    database_service.add_topic('Verb Tenses', 'Practice using different verb tenses in English', category_id)
    topic = database_service.get_topic_by_name('Verb Tenses')
    topic_id = topic[0]

    database_service.add_exercise(topic_id, 'Exercise 1', 'Description for exercise 1')
    database_service.add_exercise(topic_id, 'Exercise 2', 'Description for exercise 2')

    exercises = database_service.get_exercises_by_topic_id(topic_id)
    assert len(exercises) == 2
    assert exercises[0] == (1, topic_id, 'Exercise 1', 'Description for exercise 1')
    assert exercises[1] == (2, topic_id, 'Exercise 2', 'Description for exercise 2')

def test_add_and_get_topic_not_found(database_service):
    topic = database_service.get_topic_by_name('Nonexistent Topic')
    assert topic is None

def test_add_and_get_exercises_not_found(database_service):
    exercises = database_service.get_exercises_by_topic_id(999)
    assert len(exercises) == 0

def test_get_all_topics(database_service):
    category_id = database_service.add_category('Present and Past')
    database_service.add_topic('Verb Tenses', 'Practice using different verb tenses in English', category_id)
    database_service.add_topic('Phrasal Verbs', 'Learn common phrasal verbs in English', category_id)

    topics = database_service.get_all_topics()
    assert len(topics) == 2
    assert topics[0] == (1, 'Verb Tenses', 'Practice using different verb tenses in English', category_id)
    assert topics[1] == (2, 'Phrasal Verbs', 'Learn common phrasal verbs in English', category_id)

def test_get_theory_card_by_topic_id(database_service):
    database_service.add_topic('Test Topic', 'Test description', 1)
    database_service.add_theory_card(1, 'Test theory')

    theory_card = database_service.get_theory_card_by_topic_id(1)
    assert theory_card[0] == 'Test theory'

def test_get_all_topics(database_service):
        category_id = database_service.add_category('Present and Past')
        database_service.add_topic('Verb Tenses', 'Practice using different verb tenses in English', category_id)
        database_service.add_topic('Phrasal Verbs', 'Learn common phrasal verbs in English', category_id)

        topics = database_service.get_all_topics()
        assert len(topics) ==  2
        assert topics[0] == (1, 'Verb Tenses')
        assert topics[1] == (2, 'Phrasal Verbs')

def test_add_and_get_theory_card(database_service):
    category_id = database_service.add_category('Grammar Rules')
    database_service.add_topic('Nouns and Pronouns', 'Detailed discussion on nouns and pronouns', category_id)
    topic = database_service.get_topic_by_name('Nouns and Pronouns')
    topic_id = topic[0]

    database_service.add_theory_card(topic_id, 'Theory about nouns and pronouns')
    
    conn = sqlite3.connect(database_service.db_file)
    c = conn.cursor()
    c.execute("SELECT * FROM theory_cards WHERE topic_id = ?", (topic_id,))
    theory_card = c.fetchone()
    assert theory_card == (1, topic_id, 'Theory about nouns and pronouns')
    conn.close()

def test_get_theory_cards_by_topic_id(database_service):
    category_id = database_service.add_category('Grammar Rules')
    database_service.add_topic('Verbs', 'Detailed discussion on verbs usage', category_id)
    topic = database_service.get_topic_by_name('Verbs')
    topic_id = topic[0]

    database_service.add_theory_card(topic_id, 'Theory on active verbs')
    database_service.add_theory_card(topic_id, 'Theory on passive verbs')

    conn = sqlite3.connect(database_service.db_file)
    c = conn.cursor()
    c.execute("SELECT theory FROM theory_cards WHERE topic_id = ?", (topic_id,))
    theories = c.fetchall()
    expected = [('Theory on active verbs',), ('Theory on passive verbs',)]
    assert theories == expected
    conn.close()

def test_theory_card_not_found(database_service):
    conn = sqlite3.connect(database_service.db_file)
    c = conn.cursor()
    c.execute("SELECT * FROM theory_cards WHERE topic_id = ?", (999,))
    theory_card = c.fetchone()
    assert theory_card is None
    conn.close()
