# Import the necessary libraries
import json
import requests
import pandas as pd

# Load the configuration settings from config.json
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Define the necessary variables
OCL_API_URL = config['OCL_API_URL']
SOURCE_ID = config['SOURCE_ID']
COLLECTION_ID = config['COLLECTION_ID']
OCL_TOKEN = config['OCL_TOKEN']
ORG_ID = config['ORG_ID']

ORG_ID = "MSFOCB"
SOURCE_ID = "Create"

# Headers for the API request
HEADERS = {
    "Authorization": f"Token {OCL_TOKEN}",
    "Content-Type": "application/json"
}

# Create the necessary OCL concepts for the provided CSV file
csv_file = "cleaned_concepts.csv"

# Create a function to check if a concept external ID already exists in OCL collection TEST - If not, add it as a reference 
def check_and_add_reference(concept_details):
    concept_id = concept_details["id"]
    url = f"https://api.openconceptlab.org/orgs/{ORG_ID}/collections/{COLLECTION_ID}/concepts/{concept_id}"
    response = requests.get(url, headers=HEADERS, timeout=30)
    if response.status_code == 200:
        print(f"Concept '{concept['name']}' already exists in OCL collection - Skipping")
    else:
        # Add the newly created concept to the OCL collection as a reference
        reference_query = {
            "data": {
                "expressions": [
                    concept_details["url"]
                ]
            },
            "cascade": {
                "method": "sourcetoconcepts",
                "cascade_levels": "*",
                "map_types": "Q-AND-A,CONCEPT-SET",
                "return_map_types": "*"
            }
        }
        collection_api_url = f"https://api.openconceptlab.org/orgs/{ORG_ID}/collections/{COLLECTION_ID}/references/?transformReferences=extensional"
        response = requests.put(collection_api_url, json=reference_query, headers=HEADERS)
        if response.status_code == 200:
            print(f"Concept '{concept['name']}' added to OCL collection as a reference")
        else:
            print(f"Failed to add concept '{concept['name']}' to OCL collection - Skipping reference")

def create_concepts(csv_file):
    concepts = []

    # Load the CSV file
    df = pd.read_csv(csv_file)

    # Iterate over each row in the CSV file
    for _, row in df.iterrows():
        concept = {
            "name":  row["Name"],
            "external_id": row["External ID"] if not pd.isnull(row["External ID"]) else None,
        }
        concepts.append(concept)

    return concepts, df

concepts, df = create_concepts(csv_file)


# Write a query to create each concept in OCL using Open Concept Lab API
for concept in concepts:
    source_query = {
    "concept_class": "Misc",
    "datatype": "N/A",
    "names": [
            {
                "name": concept["name"],
                "locale": "en",
                "locale_preferred": "true",
                "name_type": "Fully-Specified"
            }
        ]
    }
    # Make a POST request to the Open Concept Lab API to create the concept
    # If the concept creation is successful, update the column "External ID" with the OCL concept External ID in the CSV file
    # if column "External ID" is empty, create the OCL concept, otherwise skip the concept creation
    # Save the updated CSV file with the OCL concept External IDs if concept creation is successful
    if concept["external_id"] is None:
        source_api_url = f"https://api.openconceptlab.org/orgs/{ORG_ID}/sources/{SOURCE_ID}/concepts/"
        response = requests.post(source_api_url, json=source_query, headers=HEADERS)
        if response.status_code == 201:
            concept_details = response.json()
            concept["external_id"] = concept_details["external_id"]
            df.loc[df["Name"] == concept["name"], "External ID"] = concept["external_id"]
            # Update the CSV file with external IDs if concept creation is successful
            df.to_csv(csv_file, index=False)
            print(f"Concept '{concept['name']}' created successfully with External ID: {concept['external_id']}")
            check_and_add_reference(concept_details)
            
        else:
            print(f"Failed to create concept: {concept['name']}")
            print(f"Status code: {response.status_code}")
    else:
        print(f"Concept {concept['name']} already exists with external ID: {concept['external_id']}")

print("Concepts created and added successfully!")