# Coda Progress Tracker

A Streamlit dashboard for tracking and visualizing progress metrics from multiple Coda documents over time.

🚀 **[View Live Demo](https://your-app-name.streamlit.app)** (Update this after deployment)

## Features

- � **Auto-discover docs by folder** - Automatically track all docs in a specific Coda folder (e.g., "CPI ACTIVE")
- �📊 Fetch progress formulas from multiple Coda docs via API
- 📈 Track historical progress data over time
- 📉 Interactive charts and visualizations
- 💾 Automatic CSV storage of historical data
- 🔄 Daily automated updates (optional)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Coda API Token

1. Go to https://coda.io/account
2. Scroll to "API Settings"
3. Generate a new API token
4. Copy the token (you'll need it for the app)

### 3. Configure Doc Discovery

You have two options:

**Option A: Auto-discover by Folder (Recommended)**
1. Set your folder name in `.streamlit/secrets.toml`:
   ```toml
   FOLDER_NAME = "CPI ACTIVE"
   ```
2. The app will automatically find and track all docs in that folder

**Option B: Manual Doc IDs**
1. Find your Coda doc ID in the URL:
   ```
   https://coda.io/d/_dABCDEFGH/...
                     ^^^^^^^^^^
                     This is your doc ID
   ```
2. Add them to `.streamlit/secrets.toml`:
   ```toml
   DOC_IDS = "doc1,doc2,doc3"
   ```

## Usage

### Run the Streamlit App

```bash
streamlit run app.py
```

Then:
1. Enter your Coda API token in the sidebar
2. Choose your doc discovery method:
   - **By Folder Name**: Enter "CPI ACTIVE" (or your folder name) and click "Find Folder & List Docs"
   - **Manual Doc IDs**: Enter doc IDs one per line
3. Click "Fetch Latest Data"
4. View your progress dashboard!

### Manual Data Fetch (Command Line)

You can also fetch data without running the app:

```bash
python fetch_data.py YOUR_API_TOKEN DOC_ID1 DOC_ID2 DOC_ID3
```

## Setting Up Daily Automated Updates

### Windows Task Scheduler

1. Open Task Scheduler
2. Create a new task:
   - **Trigger**: Daily at your preferred time (e.g., 9:00 AM)
   - **Action**: Start a program
   - **Program**: `python`
   - **Arguments**: `C:\Users\Dan\CascadeProjects\coda-progress-tracker\fetch_data.py YOUR_API_TOKEN DOC_ID1 DOC_ID2`
   - **Start in**: `C:\Users\Dan\CascadeProjects\coda-progress-tracker`

This will automatically fetch and store progress data daily.

## How It Works

1. **Folder Discovery** (Optional): The app uses the Coda API to:
   - List all folders in your workspace
   - Find the folder matching your specified name (e.g., "CPI ACTIVE")
   - Automatically get all docs within that folder

2. **Formulas in Coda**: Create formulas in your Coda docs that calculate progress metrics (e.g., `Average([Hardware progress].[Progress])`)

3. **API Fetch**: The script fetches all formulas containing "progress" in their name from your specified docs

4. **Historical Storage**: Each fetch appends data to `progress_history.csv` with a timestamp

5. **Visualization**: The Streamlit app reads the CSV and creates interactive charts showing progress over time

## Data Format

The app stores data in CSV format:

| doc_name | metric | value | timestamp |
|----------|--------|-------|-----------|
| FFCUR - First Fiber Credit Union | Hardware modeling progress | 48.4375 | 2026-05-08 12:30:00 |
| Project B | Software development progress | 65.2 | 2026-05-08 12:30:00 |

## Tips

- **Folder-based tracking**: When you add new docs to the "CPI ACTIVE" folder, they'll automatically be included in the next fetch
- Make sure your Coda formulas have "progress" in their name so they're automatically detected
- The app tracks changes over time, so run it daily to build historical data
- You can manually edit `progress_history.csv` if needed
- Export data as CSV from the app for further analysis

## Deployment to Streamlit Community Cloud

### Quick Deploy

1. **Push your code to GitHub** (see instructions below)
2. **Go to** https://share.streamlit.io/
3. **Click "New app"** and configure:
   - Repository: `Carpentry-Plus-Inc/Metrics`
   - Branch: `main`
   - Main file: `coda-progress-tracker/app.py`
4. **Add secrets** in Streamlit Cloud settings:
   ```toml
   CODA_API_TOKEN = "your_api_token"
   DOC_IDS = "doc1,doc2,doc3"
   ```
5. **Deploy!**

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

## Troubleshooting

**"No progress metrics found"**
- Ensure your formulas contain "progress" in their name
- Check that your API token has access to the docs
- Verify the doc IDs are correct

**"Error fetching from doc"**
- Check your API token is valid
- Ensure you have permission to access the doc
- Verify the doc ID format (should not include `_d` prefix)
