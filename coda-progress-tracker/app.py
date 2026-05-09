import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv
from streamlit_echarts import st_echarts

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
        
        return milestones
        
    except Exception as e:
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

def save_milestones_data(data):
    """Save milestone data to CSV (overwrite each time)"""
    milestones_file = "milestones.csv"
    df = pd.DataFrame(data)
    df.to_csv(milestones_file, index=False)

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
                all_milestones = []
                
                for doc_id in doc_ids:
                    # Fetch progress metrics
                    data = fetch_coda_formulas(doc_id, api_token)
                    all_data.extend(data)
                    
                    # Fetch milestones
                    milestones = fetch_coda_milestones(doc_id, api_token)
                    all_milestones.extend(milestones)
                
                # Save progress data
                if all_data:
                    save_progress_data(all_data)
                
                # Save milestone data
                if all_milestones:
                    save_milestones_data(all_milestones)
                
                # Show results
                if all_data or all_milestones:
                    metrics_msg = f"{len(all_data)} metrics" if all_data else "0 metrics"
                    milestones_msg = f"{len(all_milestones)} milestones" if all_milestones else "0 milestones"
                    st.success(f"✅ Fetched {metrics_msg} and {milestones_msg} from {len(doc_ids)} docs")
                    st.rerun()
                else:
                    st.warning("No data found")

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
    
    # Matrix Mini Bar Chart - Project Overview
    st.header("📊 Project Progress Overview")
    
    # Prepare data for matrix chart
    projects = latest_df['doc_name'].unique().tolist()
    matrix_data = []
    
    for idx, project in enumerate(projects):
        project_metrics = latest_df[latest_df['doc_name'] == project]
        values = project_metrics['value'].tolist()
        matrix_data.append({
            "name": project,
            "value": values,
            "height": 20
        })
    
    # Get all unique metrics for the legend
    all_metrics = latest_df['metric'].unique().tolist()
    
    # Create matrix mini bar chart option
    matrix_option = {
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
            "formatter": "{b}<br/>{a}: {c}%"
        },
        "grid": {
            "left": "25%",
            "right": "10%",
            "top": "5%",
            "bottom": "5%"
        },
        "xAxis": {
            "type": "value",
            "max": 100,
            "splitLine": {"show": False},
            "axisLabel": {"formatter": "{value}%"}
        },
        "yAxis": {
            "type": "category",
            "data": projects,
            "axisLine": {"show": False},
            "axisTick": {"show": False},
            "splitLine": {"show": False}
        },
        "series": []
    }
    
    # Add a series for each metric
    for metric_idx, metric in enumerate(all_metrics):
        series_data = []
        for project_idx, project in enumerate(projects):
            project_metric = latest_df[(latest_df['doc_name'] == project) & (latest_df['metric'] == metric)]
            if not project_metric.empty:
                value = project_metric['value'].iloc[0]
                series_data.append([value, project_idx])
            else:
                series_data.append([0, project_idx])
        
        matrix_option["series"].append({
            "name": metric,
            "type": "bar",
            "stack": "total",
            "data": series_data,
            "label": {
                "show": True,
                "position": "inside",
                "formatter": "{c}%",
                "fontSize": 10
            }
        })
    
    # Add legend
    matrix_option["legend"] = {
        "data": all_metrics,
        "top": "bottom"
    }
    
    st_echarts(options=matrix_option, height="300px")
    
    st.header("📈 Progress Over Time")
    
    project_options = df['doc_name'].unique().tolist()
    selected_project = st.selectbox(
        "Select project to plot",
        project_options,
        index=0
    )
    
    if selected_project:
        filtered_df = df[df['doc_name'] == selected_project]
        
        # Prepare data for ECharts
        metrics = filtered_df['metric'].unique()
        series_data = []
        
        for metric in metrics:
            metric_df = filtered_df[filtered_df['metric'] == metric].sort_values('timestamp')
            data_points = [
                [row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'), row['value']] 
                for _, row in metric_df.iterrows()
            ]
            series_data.append({
                "name": metric,
                "type": "line",
                "smooth": True,
                "symbol": "circle",
                "symbolSize": 8,
                "data": data_points
            })
        
        # Load milestone markers
        milestones_df = load_milestones()
        milestone_marks = []
        
        if not milestones_df.empty:
            project_milestones = milestones_df[milestones_df['doc_name'] == selected_project]
            
            if not project_milestones.empty:
                st.info(f"📍 Showing {len(project_milestones)} milestone markers for {selected_project}")
                
                for _, milestone in project_milestones.iterrows():
                    if pd.notna(milestone.get('start_date')):
                        start_date = pd.to_datetime(milestone['start_date']).strftime('%Y-%m-%d')
                        milestone_marks.append({
                            "xAxis": start_date,
                            "lineStyle": {"color": "#10b981", "type": "dashed", "width": 2},
                            "label": {"formatter": f"▶ {milestone['phase']}", "position": "insideStartTop"}
                        })
                    
                    if pd.notna(milestone.get('end_date')):
                        end_date = pd.to_datetime(milestone['end_date']).strftime('%Y-%m-%d')
                        milestone_marks.append({
                            "xAxis": end_date,
                            "lineStyle": {"color": "#ef4444", "type": "dotted", "width": 2},
                            "label": {"formatter": f"◀ {milestone['phase']}", "position": "insideEndBottom"}
                        })
        
        # ECharts option configuration
        option = {
            "title": {
                "text": f"Progress Trends - {selected_project}",
                "left": "center",
                "textStyle": {"fontSize": 20}
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "cross"}
            },
            "legend": {
                "data": list(metrics),
                "top": 40,
                "right": 20
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "15%",
                "containLabel": True
            },
            "toolbox": {
                "feature": {
                    "dataZoom": {"yAxisIndex": "none"},
                    "restore": {},
                    "saveAsImage": {}
                }
            },
            "xAxis": {
                "type": "time",
                "boundaryGap": False,
                "axisLabel": {"rotate": 45}
            },
            "yAxis": {
                "type": "value",
                "min": 0,
                "max": 100,
                "axisLabel": {"formatter": "{value}%"}
            },
            "dataZoom": [
                {
                    "type": "slider",
                    "start": 0,
                    "end": 100,
                    "height": 30,
                    "bottom": 10
                },
                {
                    "type": "inside",
                    "start": 0,
                    "end": 100
                }
            ],
            "series": series_data,
            "markLine": {
                "data": milestone_marks,
                "symbol": "none"
            } if milestone_marks else {}
        }
        
        st_echarts(options=option, height="600px")
    
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
