"Filter data needed for automatch script"

import json

# Define source and target file paths
SOURCE_FILE = "ocl_source_snapshots/MSF_Source_20240717_220327.json"
FILTERED_FILE = f"{SOURCE_FILE.split('.', maxsplit=1)[0]}_Filtered.json"

# Load the JSON file
with open(SOURCE_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)

# Extract the required fields
filtered_data = []
for concept in data:
    filtered_concept = {
        "uuid": concept.get("uuid"),
        "id": concept.get("id"),
        "external_id": concept.get("external_id"),
        "display_name": concept.get("display_name"),
        "datatype": concept.get("datatype"),
        "concept_class": concept.get("concept_class"),
        "display_locale": concept.get("display_locale"),
        "URL": concept.get("url"),
        "organization": concept.get("organization"),
        "source": concept.get("source"),
        "owner": concept.get("owner"),
        "extras": concept.get("extras"),
        "names": concept.get("names"),
        "descriptions": concept.get("descriptions"),
    }
    filtered_data.append(filtered_concept)

# Save the filtered data to a new JSON file
with open(FILTERED_FILE, "w", encoding="utf-8") as file:
    json.dump(filtered_data, file, indent=4)
