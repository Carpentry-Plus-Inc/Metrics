import pandas as pd
import os
import sys
from dotenv import load_dotenv

PLUGIN_RESOURCES_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "cpi-timber-plugin", "CPI_TIMBER"))
if PLUGIN_RESOURCES_PATH not in sys.path:
    sys.path.append(PLUGIN_RESOURCES_PATH)

from resources.cpi_coda import CodaClient, CodaError

load_dotenv()

DATA_FILE = "progress_history.csv"
MILESTONES_FILE = "milestones.csv"

def fetch_coda_milestones(doc_id, api_token):
    """Fetch milestone data from Project Milestones table in a Coda doc"""
    try:
        milestones = CodaClient(api_token).fetch_milestones(doc_id)
        print(f"  Found {len(milestones)} milestones")
        return milestones
    except CodaError as e:
        print(f"Error fetching milestones from doc {doc_id}: {str(e)}")
        return []

def fetch_coda_formulas(doc_id, api_token):
    """Fetch all formulas from a Coda doc"""
    try:
        return CodaClient(api_token).fetch_progress_formulas(doc_id)
    except CodaError as e:
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
