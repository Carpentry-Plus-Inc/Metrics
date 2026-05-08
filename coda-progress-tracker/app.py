import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file (local development)
load_dotenv()

# Helper function to get config from either .env or Streamlit secrets
def get_config(key, default=''):
    # Try Streamlit secrets first (for cloud deployment)
    if hasattr(st, 'secrets') and key in st.secrets:
        return st.secrets[key]
    # Fall back to environment variables (for local development)
    return os.getenv(key, default)

st.set_page_config(page_title="Coda Progress Tracker", layout="wide")

st.title("📊 Coda Project Progress Dashboard")

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
        st.error(f"Error fetching from doc {doc_id}: {str(e)}")
        return []

def save_progress_data(data):
    """Append new data to CSV"""
    df = pd.DataFrame(data)
    
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        try:
            existing_df = pd.read_csv(DATA_FILE)
            df = pd.concat([existing_df, df], ignore_index=True)
        except pd.errors.EmptyDataError:
            pass
    
    df.to_csv(DATA_FILE, index=False)
    return df

def load_progress_history():
    """Load historical progress data"""
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    return pd.DataFrame()

def load_milestones():
    """Load milestone data"""
    milestones_file = "milestones.csv"
    if os.path.exists(milestones_file):
        df = pd.read_csv(milestones_file)
        # Convert date columns to datetime
        if 'start_date' in df.columns:
            df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')
        if 'end_date' in df.columns:
            df['end_date'] = pd.to_datetime(df['end_date'], errors='coerce')
        return df
    return pd.DataFrame()

with st.sidebar:
    st.header("⚙️ Configuration")
    
    env_api_token = get_config('CODA_API_TOKEN', '')
    env_doc_ids = get_config('DOC_IDS', '')
    
    api_token = st.text_input(
        "Coda API Token", 
        value=env_api_token,
        type="password", 
        help="Get your API token from Coda Account Settings or set in .env file"
    )
    
    st.subheader("Document IDs")
    default_doc_ids = env_doc_ids.replace(',', '\n') if env_doc_ids else ''
    doc_ids_input = st.text_area(
        "Enter Doc IDs (one per line)",
        value=default_doc_ids,
        help="Find doc ID in the URL: coda.io/d/_d{DOC_ID} or set in .env file",
        height=150
    )
    
    doc_ids = [doc_id.strip() for doc_id in doc_ids_input.split('\n') if doc_id.strip()]
    
    if st.button("🔄 Fetch Latest Data", type="primary"):
        if not api_token:
            st.error("Please enter your Coda API token")
        elif not doc_ids:
            st.error("Please enter at least one doc ID")
        else:
            with st.spinner("Fetching data from Coda..."):
                all_data = []
                for doc_id in doc_ids:
                    data = fetch_coda_formulas(doc_id, api_token)
                    all_data.extend(data)
                
                if all_data:
                    save_progress_data(all_data)
                    st.success(f"✅ Fetched {len(all_data)} metrics from {len(doc_ids)} docs")
                    st.rerun()
                else:
                    st.warning("No progress metrics found")

st.header("📈 Current Progress")

df = load_progress_history()

if df.empty:
    st.info("👈 Configure your API token and doc IDs in the sidebar, then click 'Fetch Latest Data' to get started")
else:
    latest_df = df.sort_values('timestamp').groupby(['doc_name', 'metric']).last().reset_index()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Projects", df['doc_name'].nunique())
    with col2:
        st.metric("Total Metrics", df['metric'].nunique())
    with col3:
        avg_progress = latest_df['value'].mean()
        st.metric("Average Progress", f"{avg_progress:.1f}%")
    
    st.subheader("Latest Values")
    display_df = latest_df[['doc_name', 'metric', 'value', 'timestamp']].copy()
    display_df['value'] = display_df['value'].round(2)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.header("📊 Progress Over Time")
    
    project_options = df['doc_name'].unique().tolist()
    selected_project = st.selectbox(
        "Select project to plot",
        project_options,
        index=0
    )
    
    if selected_project:
        filtered_df = df[df['doc_name'] == selected_project]
        
        fig = px.line(
            filtered_df,
            x='timestamp',
            y='value',
            color='metric',
            title=f"Progress Trends - {selected_project}",
            labels={'value': 'Progress (%)', 'timestamp': 'Date', 'metric': 'Metric'},
            markers=True
        )
        
        # Load and add milestone markers
        milestones_df = load_milestones()
        
        if not milestones_df.empty:
            project_milestones = milestones_df[milestones_df['doc_name'] == selected_project]
            
            if not project_milestones.empty:
                st.info(f"📍 Showing {len(project_milestones)} milestone markers for {selected_project}")
                
                # Add vertical lines for milestone start dates
                for _, milestone in project_milestones.iterrows():
                    if pd.notna(milestone.get('start_date')):
                        fig.add_vline(
                            x=milestone['start_date'],
                            line_dash="dash",
                            line_color="green",
                            opacity=0.7,
                            annotation_text=f"▶ {milestone['phase']}",
                            annotation_position="top left",
                            annotation_font_size=10
                        )
                    
                    # Add vertical lines for milestone end dates
                    if pd.notna(milestone.get('end_date')):
                        fig.add_vline(
                            x=milestone['end_date'],
                            line_dash="dot",
                            line_color="red",
                            opacity=0.7,
                            annotation_text=f"◀ {milestone['phase']}",
                            annotation_position="top right",
                            annotation_font_size=10
                        )
            else:
                st.warning(f"No milestones found for {selected_project}")
        else:
            st.warning("No milestone data available. Run fetch_data.py to fetch milestones.")
        
        fig.update_yaxes(range=[0, 100])
        fig.update_layout(height=500, legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ))
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.header("📅 Historical Data")
    
    if st.checkbox("Show all historical records"):
        st.dataframe(
            df.sort_values('timestamp', ascending=False),
            use_container_width=True,
            hide_index=True
        )
    
    if st.button("📥 Download Data as CSV"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"coda_progress_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

st.divider()
st.caption("💡 Tip: Set up a daily scheduled task to run the data fetch automatically")
