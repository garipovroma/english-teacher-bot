import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services import LlamaService


api_token = os.getenv('LLAMA_API_TOKEN')

if api_token is None:
    print("API token not found in environment variables. Please set LLAMA_API_TOKEN.")
    exit(1)

llama_service = LlamaService(api_token)

user_prompt = "Practice verb tenses with this exercise."

exercise = llama_service.generate_exercise(user_prompt)

print(exercise)