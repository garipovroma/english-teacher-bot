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
    conn.close()

def test_add_and_get_topic(database_service):
    database_service.add_topic('Verb Tenses', 'Practice using different verb tenses in English')
    topic = database_service.get_topic_by_name('Verb Tenses')
    assert topic == (1, 'Verb Tenses', 'Practice using different verb tenses in English')

    topic = database_service.get_topic_by_id(1)
    assert topic == (1, 'Verb Tenses', 'Practice using different verb tenses in English')

def test_add_and_get_exercises(database_service):
    database_service.add_topic('Verb Tenses', 'Practice using different verb tenses in English')
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
    exercises = database_service.get_exercises_by_topic_id(999)  # Nonexistent topic ID
    assert len(exercises) == 0

def test_add_multiple_topics(database_service):
    database_service.add_topic('Vocabulary Building', 'Expand your English vocabulary')
    database_service.add_topic('Grammar Fundamentals', 'Learn the basic grammar rules of English')

    topics = [
        database_service.get_topic_by_name('Vocabulary Building'),
        database_service.get_topic_by_name('Grammar Fundamentals')
    ]

    assert len(topics) == 2
    assert topics[0][1] == 'Vocabulary Building'
    assert topics[1][1] == 'Grammar Fundamentals'

def test_add_multiple_exercises(database_service):
    database_service.add_topic('Conversational English', 'Improve your English conversation skills')

    topic_id = database_service.get_topic_by_name('Conversational English')[0]

    database_service.add_exercise(topic_id, 'Exercise 1', 'Description for exercise 1')
    database_service.add_exercise(topic_id, 'Exercise 2', 'Description for exercise 2')

    exercises = database_service.get_exercises_by_topic_id(topic_id)
    assert len(exercises) == 2
    assert exercises[0][2] == 'Exercise 1'
    assert exercises[1][2] == 'Exercise 2'