# Load the json file generated_form_schemas/F01-MHPSS_Baseline.json and extract all the concept keys and their corresponding UUIDs.
# Check if each UUID exists in the OpenMRS database using the API call "http://localhost/openmrs/ws/rest/v1/concept/{uuid}".
# Update the status of each ID in a CSV file called "concept_status.csv".

import json
import requests
import csv
import time

def find_key_in_json(data, key):
    found_values = []
    
    if isinstance(data, dict):
        for k, v in data.items():
            if k == key:
                found_values.append((k, v))
            found_values.extend(find_key_in_json(v, key))
    
    elif isinstance(data, list):
        for item in data:
            found_values.extend(find_key_in_json(item, key))
    
    return found_values
def main():
    # Load the json file
    with open('generated_form_schemas/F01-MHPSS_Baseline.json', 'r') as f:
        data = json.load(f)

    # Extract concept keys and UUIDs
    concept_uuids = find_key_in_json(data, "concept")

    # Update the status of each ID in a CSV file
    with open('concept_status.csv', 'w', newline='') as csvfile:
        fieldnames = ['uuid', 'status', 'name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for concept_key, uuid in concept_uuids:
            # Make API call to check status and give time to OpenMRS to respond
            response = requests.get(f'http://localhost/openmrs/ws/rest/v1/concept/{uuid}', auth=('admin', 'Admin123'))
            if response.status_code == 200:
                # Get value of key 'display' from response
                name = response.json().get('display')
                writer.writerow({'uuid': uuid, 'status': 'Exists', 'name': name})
                print(f'Concept {name} with UUID {uuid} exists in the OpenMRS database')
            else:
                name = 'not found'
                writer.writerow({'uuid': uuid, 'status': 'Not found'})
                print(f'Error checking concept with UUID {uuid}: {response.status_code}')
    print('Concept status updated successfully!')

if __name__ == '__main__':
    main()