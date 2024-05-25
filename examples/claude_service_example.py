import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services import LLMService


api_token = os.getenv('ANTHROPIC_API_TOKEN')

if api_token is None:
    print("API token not found in environment variables. Please set LLAMA_API_TOKEN.")
    exit(1)

llama_service = LLMService(api_token, temperature=0.4)

user_prompt = "Verb tenses"

exercise = llama_service.generate_exercise(user_prompt)

print(exercise)