"Filter data needed for automatch script"
import json

# Define source and target file paths
SOURCE_FILE = 'ocl_source_snapshots/MSF_Source_20240717_165221.json'
FILTERED_FILE = f"{SOURCE_FILE.split('.', maxsplit=1)[0]}_Filtered.json"

# Initialize an empty list to hold the filtered data
filtered_data = []

# Open the source file and read it incrementally
with open(SOURCE_FILE, 'r', encoding='utf-8') as file:
    for line in file:
        try:
            # Parse each line as a JSON object
            concept = json.loads(line.strip(',\n'))  # Handle potential trailing commas and newlines
            # Extract the required fields
            filtered_concept = {
                'uuid': concept.get('uuid'),
                'id': concept.get('id'),
                'external_id': concept.get('external_id'),
                'display_name': concept.get('display_name'),
                'datatype': concept.get('datatype'),
                'concept_class': concept.get('concept_class'),
                'display_locale': concept.get('display_locale'),
                'URL': concept.get('url'),
                'organization': concept.get('organization'),
                'source': concept.get('source'),
                'owner': concept.get('owner'),
                'extras': concept.get('extras'),
                'descriptions': concept.get('descriptions')
            }
            # Append the filtered concept to the list
            filtered_data.append(filtered_concept)
        except json.JSONDecodeError:
            continue  # Skip lines that cannot be parsed

# Save the filtered data to a new JSON file
with open(FILTERED_FILE, 'w', encoding='utf-8') as file:
    json.dump(filtered_data, file, indent=4)

print(f"Filtered data saved to {FILTERED_FILE}")
