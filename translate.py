"""
A script to add translations names to concepts in OCL based on a metadata file in Excel.
"""

import json
import os
import re
import time
import uuid
import openpyxl
import requests
import pandas as pd
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

# Ignore potential warnings related to opening large Excel files
openpyxl.reader.excel.warnings.simplefilter(action="ignore")

# Load the configuration settings from config.json
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# Define the necessary variables
OCL_API_URL = config["OCL_API_URL"]
SOURCE_ID = config["SOURCE_ID"]
COLLECTION_ID = config["COLLECTION_ID"]
OCL_TOKEN = config["OCL_TOKEN"]
ORG_ID = config["ORG_ID"]

ORG_ID = "MSF"
SOURCE_ID = "MSF"
COLLECTION_ID = "MentalHealth"

# Headers for the API request
HEADERS = {"Authorization": f"Token {OCL_TOKEN}", "Content-Type": "application/json"}

# Extract the configuration settings
METADATA_FILE = os.getenv("METADATA_FILEPATH")
# Adjust header to start from row 2
option_sets = pd.read_excel(METADATA_FILE, sheet_name="OptionSets", header=1)
# List of sheets to process
SHEETS = os.getenv("SHEETS_TO_PREVIEW", "F06-PHQ-9").split(",")
# Add sheet "optionSets" to the list of sheets to process
SHEETS.append("OptionSets")

print(SHEETS)

# Load the OCL concepts from ocl_source_snapshots/MSF_Source_20240830_163943.json
OCL_CONCEPTS_FILE = "ocl_source_snapshots/MSF_Source_20240830_163943.json"
with open(OCL_CONCEPTS_FILE, "r", encoding="utf-8") as file:
    ocl_concepts = json.load(file)

# List all the external IDs found in column "External ID" in the metadata
# Add their corresponding translation from the column "Translation" in the metadata
# Then get their corresponding concepts ID using the ocl_concepts
translation_dict = {}
for sheet_name in SHEETS:
    data = pd.read_excel(METADATA_FILE, sheet_name=sheet_name, header=1)
    for _, row in data.iterrows():
        # Check the external ID in the column "External ID" of the metadata
        external_id = row["External ID"]
        translation = str(row["Translation"])  # Convert translation to string
        # If the external ID is found and the translation is not null or NaN or nan
        if (
            external_id
            and translation
            and not pd.isna(translation)
            and translation.lower() != "nan"
        ):
            # Get the concept ID using the ocl_concepts
            concept_id = next(
                (c["id"] for c in ocl_concepts if c["external_id"] == external_id), None
            )
            if concept_id:
                print(
                    f"Updating {external_id} with translation {translation} -> {concept_id}"
                )
                # Add the translation, concept ID and external ID to the translation_dict
                translation_dict[external_id] = {
                    "translation": translation,
                    "concept_id": concept_id,
                    "external_id": external_id,
                }
    print(f"Translation dictionary for sheet {sheet_name} created.")
# Count the number of translations added to the translation_dict
print(f"Total translations added: {len(translation_dict)}")

# filter all entries to only keep one with the concept ID 2473
# translation_dict = {k: v for k, v in translation_dict.items() if v['external_id'] == '1a8bf24f-4f36-4971-aad9-ae77f3525738'}
# print(f'Translation dictionary after filtering: {len(translation_dict)}')

# save the translation_dict to a csv file
translation_dict_file = "translation_dict.csv"
pd.DataFrame(list(translation_dict.values())).to_csv(translation_dict_file, index=False)
print(f"Translation dictionary saved to {translation_dict_file}")

# For each concept ID in the translation_dict, check if the AR translation is already present in OCL source using this URL https://api.openconceptlab.org/orgs/MSFOCG/sources/Create/concepts/{conceptID}/names/
# If there is no AR translation, add it to the OCL concepts using the same URL with a post method
for external_id, translation_info in translation_dict.items():
    concept_id = translation_info["concept_id"]
    translation = translation_info["translation"]
    print(f"Checking AR translation {translation} for {concept_id}...")
    url = f"https://api.openconceptlab.org/orgs/MSF/sources/MSF/concepts/{concept_id}/names/"
    response = requests.get(url, headers=HEADERS, timeout=30)
    if response.status_code == 200:
        # Get the names of the concepts
        names = response.json()
        # Check if any of the names has a locale of 'ar'
        ar_translation_present = any(name["locale"] == "ar" for name in names)
        print(
            f"AR translation for {external_id} is already present: {ar_translation_present}"
        )
        if not ar_translation_present:
            # If AR translation is not present, add it to the OCL concepts
            data = {"name": translation, "locale": "ar", "name_type": "Fully-Specified"}
            print(f"Adding AR translation {translation} for {concept_id}...")
            response = requests.post(url, headers=HEADERS, json=data, timeout=30)
            if response.status_code == 201:
                print(f"Added AR translation {translation} for {concept_id}")
            else:
                print(
                    f"Failed to add AR translation {translation} for {concept_id}: Status code {response.status_code}"
                )
