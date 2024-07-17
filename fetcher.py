"Fetcher to get concepts from OpenConceptLab API and save them to a JSON file."
from datetime import datetime
import json
import requests

# Load the configuration settings from config.json
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Extract the configuration settings
FETCHER_BASE_URL = config.get('FETCHER_BASE_URL')

def fetch_all_concepts(url, file_path):
    " Fetch all concepts from the OpenConceptLab API and save them to a JSON file. "
    total_concepts = 0
    page = 1
    is_first_page = True

    while True:
        response = requests.get(f"{url}&page={page}", timeout=30)
        if response.status_code == 200:
            data = response.json()
            total_concepts += len(data)

            if not data:
                break

            with open(file_path, 'a', encoding='utf-8') as file:
                if is_first_page:
                    file.write("[\n")
                    is_first_page = False
                else:
                    file.write(",\n")
                for i, concept in enumerate(data):
                    concept_url = f"{FETCHER_BASE_URL}/concepts/{concept['id']}/"
                    concept_response = requests.get(concept_url, timeout=30)
                    if concept_response.status_code == 200:
                        concept_details = concept_response.json()
                        concept.update(concept_details)
                    json.dump(concept, file)
                    if i < len(data) - 1:
                        file.write(",\n")
            print(f"Total concepts found so far: {total_concepts}")
            page += 1
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            break

    with open(file_path, 'a', encoding='utf-8') as file:
        file.write("\n]")

    print(f"Total concepts found: {total_concepts}")
    return total_concepts

# URL of the API without the page parameter
API_URL = f"{FETCHER_BASE_URL}/concepts/?q=&limit=0"

# Save the fetched concepts to a JSON file with a timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
json_file_path = f"ocl_source_snapshots/MSF_Source_{timestamp}.json"

# Fetch and save total concepts incrementally
total_concepts_fetched = fetch_all_concepts(API_URL, json_file_path)
print(f"Total number of concepts: {total_concepts_fetched}")
print(f"Concepts saved to {json_file_path}")
