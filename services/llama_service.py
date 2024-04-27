from llamaapi import LlamaAPI
from langchain_experimental.llms import ChatLlamaAPI
from langchain_core.output_parsers import StrOutputParser
from utils.prompts import EXERCISE_PROMPT, QUESTION_ANSWER_PROMPT, SUMMARIZATION_PROMPT

class LlamaService:
    def __init__(self, api_token):
        self.llama_api = LlamaAPI(api_token)
        self.chat_model = ChatLlamaAPI(client=self.llama_api)
        self.output_parser = StrOutputParser()
        self.chain = self.chat_model | self.output_parser

    def generate_exercise(self, user_prompt):
        """
        Generate an English exercise based on the user prompt.
        
        Args:
            user_prompt (str): The user's prompt containing exercise information.
        
        Returns:
            str: The generated English exercise.
        """
        prompt = f"{EXERCISE_PROMPT}\n\nUser Prompt: {user_prompt}"
        return self.chain.invoke(prompt)

    def answer_question(self, user_question):
        """
        Generate a response to the user's question.
        
        Args:
            user_question (str): The user's question.
        
        Returns:
            str: The generated response.
        """
        prompt = f"{QUESTION_ANSWER_PROMPT}\n\nUser Question: {user_question}"
        return self.chain.invoke(prompt)

    def summarize_text(self, text):
        """
        Summarize the given text.
        
        Args:
            text (str): The text to be summarized.
        
        Returns:
            str: The generated summary.
        """
        prompt = f"{SUMMARIZATION_PROMPT}\n\nText to Summarize: {text}"
        return self.chat_model.summarize(prompt)