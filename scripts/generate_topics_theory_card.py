import sys
import os
import pandas as pd
from tqdm import tqdm

# Append the path to import from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the required service
from services import LlamaService

def generate_theory_cards(api_token):
    # Create an instance of the LlamaService
    llama_service = LlamaService(api_token)

    # Load topics from CSV
    topics_csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'topics.csv'))
    topics_df = pd.read_csv(topics_csv_path)

    # Prepare DataFrame to store the generated theory cards
    theory_cards_df = pd.DataFrame(columns=['TOPIC', 'THEORY_CARD'])

    # Generate a theory card for each topic
    for index, row in tqdm(topics_df.iterrows(), total=topics_df.shape[0], desc="Generating theory cards"):
        topic = row['TOPIC']
        theory_card = llama_service.generate_grammar_theory(topic)
        theory_cards_df = theory_cards_df.append({'TOPIC': topic, 'THEORY_CARD': theory_card}, ignore_index=True)

    # Save the generated theory cards to a new CSV file
    theory_cards_df.to_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'theory_cards.csv')), index=False)

    print("Theory cards generated and saved successfully.")

if __name__ == "__main__":
    api_token = os.getenv('LLAMA_API_TOKEN')
    if api_token is None:
        print("API token not found in environment variables. Please set LLAMA_API_TOKEN.")
        sys.exit(1)

    generate_theory_cards(api_token)
