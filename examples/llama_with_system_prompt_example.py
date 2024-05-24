from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate

# Initialize the OpenAI LLM with ChatLlamaAPI (assuming OpenAI interface is compatible with ChatLlamaAPI)
llm = OpenAI(model="ChatLlamaAPI")

# Create a system message prompt template
system_message_template = SystemMessagePromptTemplate(
    prompt_text="You are a helpful assistant trained to answer questions using Langchain."
)




# Create a human message prompt template
human_message_template = HumanMessagePromptTemplate(
    prompt_text="{input_text}"
)

# Create a chat prompt template that includes both system and human messages
chat_prompt = ChatPromptTemplate(
    system_message_prompt_template=system_message_template,
    human_message_prompt_template=human_message_template
)

# Initialize the LLM chain with the chat prompt and LLM
llm_chain = LLMChain(
    prompt_template=chat_prompt,
    llm=llm
)

# Input text from the user
input_text = "Can you explain the concept of Langchain?"

# Run the chain with the input text
response = llm_chain.run(input_text)

# Print the response
print(response)
