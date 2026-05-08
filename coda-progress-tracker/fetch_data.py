import requests
import pandas as pd
from datetime import datetime
import os
import sys
from dotenv import load_dotenv

load_dotenv()

DATA_FILE = "progress_history.csv"
MILESTONES_FILE = "milestones.csv"

def fetch_coda_milestones(doc_id, api_token):
    """Fetch milestone data from Project Milestones table in a Coda doc"""
    headers = {'Authorization': f'Bearer {api_token}'}
    
    try:
        # Get doc name
        doc_response = requests.get(
            f'https://coda.io/apis/v1/docs/{doc_id}',
            headers=headers
        )
        doc_name = doc_response.json().get('name', 'Unknown Doc')
        
        # List all tables to find Project Milestones
        tables_response = requests.get(
            f'https://coda.io/apis/v1/docs/{doc_id}/tables',
            headers=headers
        )
        
        tables = tables_response.json().get('items', [])
        milestone_table = None
        
        # Find the Project Milestones table
        for table in tables:
            if 'milestone' in table['name'].lower():
                milestone_table = table
                break
        
        if not milestone_table:
            print(f"  No Project Milestones table found in {doc_name}")
            return []
        
        table_id = milestone_table['id']
        
        # Fetch rows from the milestones table
        rows_response = requests.get(
            f'https://coda.io/apis/v1/docs/{doc_id}/tables/{table_id}/rows',
            headers=headers
        )
        
        rows = rows_response.json().get('items', [])
        
        milestones = []
        for row in rows:
            # Phase name is in the row's 'name' field
            phase = row.get('name', 'Unknown Phase')
            
            values = row.get('values', {})
            
            # Extract start date and end date from values
            # Values are keyed by column IDs, we need to find date columns
            start_date = None
            end_date = None
            
            # Get all values as a list to find dates
            for col_id, value in values.items():
                # Skip if it's a complex object (like row reference)
                if isinstance(value, dict) and '@type' in value:
                    continue
                
                # Check if it's a date string (ISO format)
                if isinstance(value, str) and 'T' in value and ':' in value:
                    # First date found is likely start date
                    if start_date is None:
                        start_date = value
                    # Second date found is likely end date
                    elif end_date is None:
                        end_date = value
            
            if phase and (start_date or end_date):
                milestones.append({
                    'doc_name': doc_name,
                    'phase': phase,
                    'start_date': start_date,
                    'end_date': end_date
                })
        
        print(f"  Found {len(milestones)} milestones")
        return milestones
        
    except Exception as e:
        print(f"Error fetching milestones from doc {doc_id}: {str(e)}")
        return []

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

def save_milestones_data(data):
    """Save milestone data to CSV (overwrite each time)"""
    df = pd.DataFrame(data)
    df.to_csv(MILESTONES_FILE, index=False)
    print(f"Saved {len(data)} milestones to {MILESTONES_FILE}")

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
    all_milestones = []
    
    for doc_id in doc_ids:
        print(f"Fetching from doc: {doc_id}")
        
        # Fetch progress metrics
        data = fetch_coda_formulas(doc_id, api_token)
        all_data.extend(data)
        print(f"  Found {len(data)} progress metrics")
        
        # Fetch milestones
        milestones = fetch_coda_milestones(doc_id, api_token)
        all_milestones.extend(milestones)
    
    if all_data:
        save_progress_data(all_data)
        print(f"✅ Successfully fetched {len(all_data)} total metrics")
    else:
        print("⚠️ No progress data fetched")
    
    if all_milestones:
        save_milestones_data(all_milestones)
        print(f"✅ Successfully fetched {len(all_milestones)} total milestones")
    else:
        print("⚠️ No milestone data fetched")
