import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_token = os.getenv('CODA_API_TOKEN')
doc_ids_str = os.getenv('DOC_IDS', '')
doc_ids = [d.strip() for d in doc_ids_str.split(',') if d.strip()]

if not api_token or not doc_ids:
    print("Error: Missing API token or doc IDs in .env file")
    exit(1)

headers = {'Authorization': f'Bearer {api_token}'}

for doc_id in doc_ids:
    print(f"\n=== Doc ID: {doc_id} ===")
    
    # Get doc name
    doc_response = requests.get(
        f'https://coda.io/apis/v1/docs/{doc_id}',
        headers=headers
    )
    
    if doc_response.status_code != 200:
        print(f"Error: {doc_response.status_code} - {doc_response.text}")
        continue
    
    doc_name = doc_response.json().get('name', 'Unknown')
    print(f"Doc Name: {doc_name}")
    
    # Get all formulas
    formulas_response = requests.get(
        f'https://coda.io/apis/v1/docs/{doc_id}/formulas',
        headers=headers
    )
    
    if formulas_response.status_code != 200:
        print(f"Error fetching formulas: {formulas_response.status_code} - {formulas_response.text}")
        continue
    
    formulas = formulas_response.json().get('items', [])
    
    print(f"\nFound {len(formulas)} total formulas:")
    for i, formula in enumerate(formulas, 1):
        print(f"{i}. Name: '{formula['name']}'")
        print(f"   Value: {formula.get('value', 'N/A')}")
        print()
