import sys
import os

from services.database_service import DatabaseService

db_service = DatabaseService('english_topics.db')

topics = [
    ('Verb Tenses', 'Practice using different verb tenses in English'),
    ('Vocabulary Building', 'Expand your English vocabulary'),
    ('Grammar Fundamentals', 'Learn the basic grammar rules of English'),
    ('Conversational English', 'Improve your English conversation skills'),
    ('Writing Techniques', 'Develop your English writing skills')
]

for name, description in topics:
    db_service.add_topic(name, description)

for topic_name, _ in topics:
    topic = db_service.get_topic_by_name(topic_name)
    topic_id = topic[0]

    exercises = [
        (f"Exercise 1 for {topic_name}", "Description for exercise 1"),
        (f"Exercise 2 for {topic_name}", "Description for exercise 2"),
        (f"Exercise 3 for {topic_name}", "Description for exercise 3"),
        (f"Exercise 4 for {topic_name}", "Description for exercise 4"),
        (f"Exercise 5 for {topic_name}", "Description for exercise 5"),
    ]

    for exercise_name, exercise_description in exercises:
        db_service.add_exercise(topic_id, exercise_name, exercise_description)

print("English topics and exercises added to the database.")