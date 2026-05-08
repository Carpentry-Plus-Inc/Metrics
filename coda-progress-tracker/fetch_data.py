import requests
import pandas as pd
from datetime import datetime
import os
import sys
from dotenv import load_dotenv

load_dotenv()

DATA_FILE = "progress_history.csv"

def fetch_coda_formulas(doc_id, api_token):
    """Fetch all formulas from a Coda doc"""
    headers = {'Authorization': f'Bearer {api_token}'}
    
    try:
        doc_response = requests.get(
            f'https://coda.io/apis/v1/docs/{doc_id}',
            headers=headers
        )
        doc_name = doc_response.json().get('name', 'Unknown Doc')
        
        formulas_response = requests.get(
            f'https://coda.io/apis/v1/docs/{doc_id}/formulas',
            headers=headers
        )
        
        formulas = formulas_response.json().get('items', [])
        
        results = []
        for formula in formulas:
            if 'progress' in formula['name'].lower():
                formula_id = formula['id']
                
                formula_detail_response = requests.get(
                    f'https://coda.io/apis/v1/docs/{doc_id}/formulas/{formula_id}',
                    headers=headers
                )
                
                formula_detail = formula_detail_response.json()
                
                # Extract value and parse if it's a string
                raw_value = formula_detail.get('value', 0)
                
                # If value is a string like "Hardware progress :48.4375", extract the number
                if isinstance(raw_value, str):
                    # Try to extract number from string
                    import re
                    numbers = re.findall(r'[-+]?\d*\.?\d+', raw_value)
                    value = float(numbers[-1]) if numbers else 0
                else:
                    value = raw_value
                
                results.append({
                    'doc_name': doc_name,
                    'metric': formula_detail.get('name', 'Unknown'),
                    'value': value,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return results
    except Exception as e:
        print(f"Error fetching from doc {doc_id}: {str(e)}")
        return []

def save_progress_data(data):
    """Append new data to CSV"""
    df = pd.DataFrame(data)
    
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        try:
            existing_df = pd.read_csv(DATA_FILE)
            df = pd.concat([existing_df, df], ignore_index=True)
        except pd.errors.EmptyDataError:
            print("Warning: Existing CSV was empty, creating new file")
    
    df.to_csv(DATA_FILE, index=False)
    print(f"Saved {len(data)} records to {DATA_FILE}")

if __name__ == "__main__":
    # Try to get from .env file first
    api_token = os.getenv('CODA_API_TOKEN')
    doc_ids_str = os.getenv('DOC_IDS', '')
    doc_ids = [d.strip() for d in doc_ids_str.split(',') if d.strip()]
    
    # Allow command line override
    if len(sys.argv) >= 3:
        api_token = sys.argv[1]
        doc_ids = sys.argv[2:]
    
    if not api_token:
        print("Error: No API token found.")
        print("Either set CODA_API_TOKEN in .env file or provide as argument:")
        print("Usage: python fetch_data.py <API_TOKEN> <DOC_ID1> [DOC_ID2] [DOC_ID3] ...")
        sys.exit(1)
    
    if not doc_ids:
        print("Error: No doc IDs found.")
        print("Either set DOC_IDS in .env file or provide as arguments:")
        print("Usage: python fetch_data.py <API_TOKEN> <DOC_ID1> [DOC_ID2] [DOC_ID3] ...")
        sys.exit(1)
    
    print(f"Fetching data from {len(doc_ids)} docs...")
    
    all_data = []
    for doc_id in doc_ids:
        print(f"Fetching from doc: {doc_id}")
        data = fetch_coda_formulas(doc_id, api_token)
        all_data.extend(data)
        print(f"  Found {len(data)} progress metrics")
    
    if all_data:
        save_progress_data(all_data)
        print(f"\n✅ Successfully fetched {len(all_data)} total metrics")
    else:
        print("\n⚠️ No progress metrics found")
