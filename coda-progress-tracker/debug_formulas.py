import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

api_token = os.getenv('CODA_API_TOKEN')
doc_ids_str = os.getenv('DOC_IDS', '')
doc_ids = [d.strip() for d in doc_ids_str.split(',') if d.strip()]

headers = {'Authorization': f'Bearer {api_token}'}

for doc_id in doc_ids:
    print(f"\n=== Doc ID: {doc_id} ===")
    
    formulas_response = requests.get(
        f'https://coda.io/apis/v1/docs/{doc_id}/formulas',
        headers=headers
    )
    
    print(f"Status Code: {formulas_response.status_code}")
    print(f"\nFull Response:")
    print(json.dumps(formulas_response.json(), indent=2))
