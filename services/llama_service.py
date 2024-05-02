from llamaapi import LlamaAPI
from langchain_experimental.llms import ChatLlamaAPI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from utils.prompts import EXERCISE_PROMPT, QUESTION_ANSWER_PROMPT, SUMMARIZATION_PROMPT, THEORY_GENERATION_PROMPT

class LlamaService:
    def __init__(self, api_token, temperature=1):
        self.llama_api = LlamaAPI(api_token)
        self.chat_model = ChatLlamaAPI(client=self.llama_api, temperature=temperature)
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
        prompt_template = PromptTemplate.from_template(EXERCISE_PROMPT)
        prompt = prompt_template.format(exercise_goal=user_prompt)
        return self.chain.invoke(prompt)

    def answer_question(self, user_question):
        """
        Generate a response to the user's question.
        
        Args:
            user_question (str): The user's question.
        
        Returns:
            str: The generated response.
        """
        prompt_template = PromptTemplate.from_template(QUESTION_ANSWER_PROMPT)
        prompt = prompt_template.format(question=user_question)
        return self.chain.invoke(prompt)

    def summarize_text(self, text):
        """
        Summarize the given text.
        
        Args:
            text (str): The text to be summarized.
        
        Returns:
            str: The generated summary.
        """
        prompt_template = PromptTemplate.from_template(SUMMARIZATION_PROMPT)
        prompt = prompt_template.format(text_to_summarize=text)
        return self.chain.invoke(prompt)

    def generate_grammar_theory(self, theory_topic):
        """
        Generate a comprehensive English grammar theory card.
        
        Args:
            theory_info (dict): A dictionary containing the theory information.
        
        Returns:
            str: The generated grammar theory card.
        """
        
        prompt_template = PromptTemplate.from_template(THEORY_GENERATION_PROMPT)
        prompt = prompt_template.format(theory_topic=theory_topic)
        return self.chain.invoke(prompt)