"""Script to verify OCL collection concepts exist in OpenMRS with detailed external ID comparison."""

import json
import csv
from datetime import datetime
import requests

# Load configuration
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# OCL Configuration
OCL_API_URL = config["OCL_API_URL"]
OCL_TOKEN = config.get("OCL_TOKEN")  # Will need to be added to config.json
ORG_ID = "MSFOCG"  # Organization ID for Iraq-Mosul collection
COLLECTION_ID = "iraq-mosul"  # Collection ID

# OpenMRS Configuration
OPENMRS_URL = "http://msf-ocg-openmrs3-dev.westeurope.cloudapp.azure.com/openmrs"
OPENMRS_AUTH = ("admin", "Admin123")  # From checker.py

# Headers for OCL API
OCL_HEADERS = {
    "Authorization": f"Token {OCL_TOKEN}",
    "Content-Type": "application/json"
}

def fetch_collection_concepts():
    """Fetch all concepts from the specified OCL collection with detailed information."""
    concepts = []
    page = 1
    
    while True:
        url = f"{OCL_API_URL}/orgs/{ORG_ID}/collections/{COLLECTION_ID}/concepts/?page={page}&limit=100&verbose=true"
        response = requests.get(url, headers=OCL_HEADERS, timeout=30)
        
        if response.status_code != 200:
            print(f"Failed to fetch concepts from OCL. Status code: {response.status_code}")
            if response.status_code == 401:
                print("Authentication failed. Please check your OCL_TOKEN in config.json")
            break
            
        data = response.json()
        if not data:
            break
            
        concepts.extend(data)
        print(f"Fetched {len(data)} concepts from page {page}")
        page += 1
        
    return concepts

def check_concept_in_openmrs(concept_id, check_type="uuid"):
    """Check if a concept exists in OpenMRS by UUID or external_id."""
    url = f"{OPENMRS_URL}/ws/rest/v1/concept/{concept_id}"
    try:
        response = requests.get(url, auth=OPENMRS_AUTH, timeout=30)
        if response.status_code == 200:
            concept_data = response.json()
            return True, concept_data.get("display"), concept_data
        else:
            return False, "Not found", None
    except requests.RequestException as e:
        print(f"Error checking concept {concept_id}: {str(e)}")
        return False, "Error", None

def search_concept_by_external_id(external_id):
    """Search for concept in OpenMRS using external_id in mappings."""
    url = f"{OPENMRS_URL}/ws/rest/v1/concept?q={external_id}"
    try:
        response = requests.get(url, auth=OPENMRS_AUTH, timeout=30)
        if response.status_code == 200:
            results = response.json().get("results", [])
            for result in results:
                # Check if any mapping matches the external_id
                concept_detail_url = f"{OPENMRS_URL}/ws/rest/v1/concept/{result['uuid']}?v=full"
                detail_response = requests.get(concept_detail_url, auth=OPENMRS_AUTH, timeout=30)
                if detail_response.status_code == 200:
                    concept_data = detail_response.json()
                    mappings = concept_data.get("mappings", [])
                    for mapping in mappings:
                        if mapping.get("code") == external_id:
                            return True, concept_data.get("display"), concept_data
            return False, "Not found by external_id", None
    except requests.RequestException as e:
        print(f"Error searching concept by external_id {external_id}: {str(e)}")
        return False, "Error", None

def main():
    """Main execution function."""
    print("Fetching concepts from OCL collection...")
    concepts = fetch_collection_concepts()
    print(f"Found {len(concepts)} concepts in OCL collection")
    
    if not concepts:
        print("No concepts found. Please check your OCL_TOKEN and collection access.")
        return
    
    # Prepare results
    results = []
    missing_concepts = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("\nChecking concepts in OpenMRS...")
    for i, concept in enumerate(concepts, 1):
        print(f"Processing concept {i}/{len(concepts)}")
        
        # Extract concept identifiers
        concept_uuid = concept.get("uuid")
        external_id = concept.get("external_id")
        concept_name = concept.get("display_name") or concept.get("name")
        concept_id = concept.get("id")
        
        # Try multiple identification methods
        found = False
        openmrs_name = "Not found"
        openmrs_data = None
        check_method = ""
        
        # Method 1: Check by UUID
        if concept_uuid:
            found, openmrs_name, openmrs_data = check_concept_in_openmrs(concept_uuid, "uuid")
            if found:
                check_method = "UUID"
        
        # Method 2: Check by external_id if UUID failed
        if not found and external_id:
            found, openmrs_name, openmrs_data = check_concept_in_openmrs(external_id, "external_id")
            if found:
                check_method = "External_ID_Direct"
        
        # Method 3: Search by external_id in mappings if direct check failed
        if not found and external_id:
            found, openmrs_name, openmrs_data = search_concept_by_external_id(external_id)
            if found:
                check_method = "External_ID_Mapping"
        
        status = "Present" if found else "Missing"
        
        result = {
            "ocl_concept_id": concept_id,
            "ocl_uuid": concept_uuid,
            "ocl_external_id": external_id,
            "ocl_name": concept_name,
            "openmrs_name": openmrs_name,
            "status": status,
            "check_method": check_method,
            "openmrs_uuid": openmrs_data.get("uuid") if openmrs_data else ""
        }
        
        results.append(result)
        
        if not found:
            missing_concepts.append(result)
            print(f"  MISSING: {concept_name} (External ID: {external_id}, UUID: {concept_uuid})")
        else:
            print(f"  FOUND: {concept_name} -> {openmrs_name} (via {check_method})")
    
    # Save detailed results to CSV
    output_file = f"ocl_openmrs_detailed_check_{timestamp}.csv"
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["ocl_concept_id", "ocl_uuid", "ocl_external_id", "ocl_name", 
                     "openmrs_name", "status", "check_method", "openmrs_uuid"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # Save missing concepts to separate CSV
    missing_file = f"missing_concepts_{timestamp}.csv"
    with open(missing_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["ocl_concept_id", "ocl_uuid", "ocl_external_id", "ocl_name"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for concept in missing_concepts:
            writer.writerow({
                "ocl_concept_id": concept["ocl_concept_id"],
                "ocl_uuid": concept["ocl_uuid"],
                "ocl_external_id": concept["ocl_external_id"],
                "ocl_name": concept["ocl_name"]
            })
    
    # Print detailed summary
    total = len(results)
    present = sum(1 for r in results if r["status"] == "Present")
    missing = sum(1 for r in results if r["status"] == "Missing")
    
    print(f"\n" + "="*60)
    print(f"DETAILED COMPARISON RESULTS")
    print(f"="*60)
    print(f"Results saved to: {output_file}")
    print(f"Missing concepts saved to: {missing_file}")
    print(f"\nSUMMARY:")
    print(f"Total concepts checked: {total}")
    print(f"Present in OpenMRS: {present}")
    print(f"Missing from OpenMRS: {missing}")
    print(f"Success rate: {(present/total*100):.1f}%")
    
    if missing_concepts:
        print(f"\nMISSING CONCEPTS ({len(missing_concepts)}):")
        print("-" * 60)
        for concept in missing_concepts[:10]:  # Show first 10
            print(f"• {concept['ocl_name']}")
            print(f"  External ID: {concept['ocl_external_id']}")
            print(f"  UUID: {concept['ocl_uuid']}")
            print()
        
        if len(missing_concepts) > 10:
            print(f"... and {len(missing_concepts) - 10} more (see {missing_file})")

if __name__ == "__main__":
    main()
