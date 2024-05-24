from enum import Enum
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from utils.prompts import (
    EXERCISE_PROMPT,
    QUESTION_ANSWER_PROMPT,
    SUMMARIZATION_PROMPT,
    THEORY_GENERATION_PROMPT,
    ASSESSMENT_PROMPT,
    TOPIC_SELECTION_PROMPT,
    EXERCISE_SYSTEM_PROMPT,
    QUESTION_ANSWER_SYSTEM_PROMPT,
    SUMMARIZATION_SYSTEM_PROMPT,
    THEORY_GENERATION_SYSTEM_PROMPT,
    ASSESSMENT_SYSTEM_PROMPT,
    TOPIC_SELECTION_SYSTEM_PROMPT
)

class Models(Enum):
    CLAUDE = 1
    LLAMA = 2

class LLMService:
    def __init__(self, api_token, temperature=1, model=Models.CLAUDE):
        self.chat_model = ChatAnthropic(temperature=temperature, model_name="claude-3-sonnet-20240229", api_key=api_token)
        self.output_parser = StrOutputParser()

    def generate_exercise(self, topic):
        system_message = EXERCISE_SYSTEM_PROMPT
        human_message = EXERCISE_PROMPT
        prompt = ChatPromptTemplate.from_messages([("system", system_message), ("human", human_message)])
        chain = prompt | self.chat_model | self.output_parser
        return chain.invoke({"topic_name": topic[1]})

    def assess_exercise_answer(self, topic, generated_exercise, user_answer):
        system_message = ASSESSMENT_SYSTEM_PROMPT
        human_message = ASSESSMENT_PROMPT
        prompt = ChatPromptTemplate.from_messages([("system", system_message), ("human", human_message)])
        chain = prompt | self.chat_model | self.output_parser
        return chain.invoke({
            "topic_name": topic[1],
            "generated_exercise": generated_exercise,
            "user_answer": user_answer
        })

    def answer_question(self, user_question):
        system_message = QUESTION_ANSWER_SYSTEM_PROMPT
        human_message = QUESTION_ANSWER_PROMPT
        prompt = ChatPromptTemplate.from_messages([("system", system_message), ("human", human_message)])
        chain = prompt | self.chat_model | self.output_parser
        return chain.invoke({"question": user_question})

    def summarize_text(self, text):
        system_message = SUMMARIZATION_SYSTEM_PROMPT
        human_message = SUMMARIZATION_PROMPT
        prompt = ChatPromptTemplate.from_messages([("system", system_message), ("human", human_message)])
        chain = prompt | self.chat_model | self.output_parser
        return chain.invoke({"text_to_summarize": text})

    def generate_grammar_theory(self, theory_topic):
        system_message = THEORY_GENERATION_SYSTEM_PROMPT
        human_message = THEORY_GENERATION_PROMPT
        prompt = ChatPromptTemplate.from_messages([("system", system_message), ("human", human_message)])
        chain = prompt | self.chat_model | self.output_parser
        return chain.invoke({"theory_topic": theory_topic})

    def get_closest_topic(self, topics, message):
        system_message = TOPIC_SELECTION_SYSTEM_PROMPT
        topics_str = "\n".join(list(map(lambda x: f"{x[0]}. {x[1]}", topics)))
        human_message = TOPIC_SELECTION_PROMPT
        prompt = ChatPromptTemplate.from_messages([("system", system_message), ("human", human_message)])
        chain = prompt | self.chat_model | self.output_parser
        return chain.invoke({"topics": topics_str, "message": message})
