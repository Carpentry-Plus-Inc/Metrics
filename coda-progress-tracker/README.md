# Coda Progress Tracker

A Streamlit dashboard for tracking and visualizing progress metrics from multiple Coda documents over time.

🚀 **[View Live Demo](https://your-app-name.streamlit.app)** (Update this after deployment)

## Features

- 📊 Fetch progress formulas from multiple Coda docs via API
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

### 3. Find Your Doc IDs

Your Coda doc ID is in the URL:
```
https://coda.io/d/_dABCDEFGH/...
                  ^^^^^^^^^^
                  This is your doc ID
```

## Usage

### Run the Streamlit App

```bash
streamlit run app.py
```

Then:
1. Enter your Coda API token in the sidebar
2. Enter your doc IDs (one per line)
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

1. **Formulas in Coda**: Create formulas in your Coda docs that calculate progress metrics (e.g., `Average([Hardware progress].[Progress])`)

2. **API Fetch**: The script fetches all formulas containing "progress" in their name from your specified docs

3. **Historical Storage**: Each fetch appends data to `progress_history.csv` with a timestamp

4. **Visualization**: The Streamlit app reads the CSV and creates interactive charts showing progress over time

## Data Format

The app stores data in CSV format:

| doc_name | metric | value | timestamp |
|----------|--------|-------|-----------|
| FFCUR - First Fiber Credit Union | Hardware modeling progress | 48.4375 | 2026-05-08 12:30:00 |
| Project B | Software development progress | 65.2 | 2026-05-08 12:30:00 |

## Tips

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
