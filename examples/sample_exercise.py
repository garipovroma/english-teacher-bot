import os
from llamaapi import LlamaAPI
from langchain_experimental.llms import ChatLlamaAPI
from langchain_core.output_parsers import StrOutputParser

# Read the API token from the environment variable
api_token = os.getenv('LLAMA_API_TOKEN')

if api_token is None:
    print("API token not found in environment variables. Please set LLAMA_API_TOKEN.")
    exit(1)

# Initialize the LlamaAPI client
llama = LlamaAPI(api_token)

# Initialize the ChatLlamaAPI model
model = ChatLlamaAPI(client=llama)

chain = (
    model 
    | StrOutputParser()
)

# Define a prompt to generate an English exercise
output = chain.invoke("Generate an English exercise for practicing verb tenses.")

# Print the generated English exercise
print("Generated English Exercise:")
print(output)