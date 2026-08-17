# Supabase Project Dashboard

A Streamlit dashboard that integrates Coda project discovery with Supabase data visualization. Automatically discovers projects from your Coda ACTIVE folder and displays data from Supabase for each project.

🚀 **[View Live Demo](https://your-app-name.streamlit.app)** (Update this after deployment)

## Features

- 📁 **Auto-discover projects** - Automatically fetches all docs from your Coda ACTIVE folder
- 🗄️ **Supabase integration** - Connects to your Supabase database to fetch project data
- 📊 **Project-specific pages** - Each project gets its own dashboard view
- 🔐 **Secure configuration** - Supports both local .env and Streamlit Cloud secrets
- 🎯 **Dynamic navigation** - Easy switching between projects

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Coda API Token

1. Go to https://coda.io/account
2. Scroll to "API Settings"
3. Generate a new API token
4. Copy the token

### 3. Get Your Supabase Credentials

1. Go to your Supabase project dashboard
2. Navigate to Settings → API
3. Copy your:
   - **Project URL** (e.g., https://xyz.supabase.co)
   - **anon/public** API key

### 4. Configure Environment Variables

**For Local Development:**

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your credentials:
   ```env
   CODA_API_TOKEN=your_coda_api_token_here
   SUPABASE_URL=your_supabase_project_url_here
   SUPABASE_KEY=your_supabase_anon_key_here
   FOLDER_NAME=ACTIVE
   ```

**For Streamlit Cloud:**

Add secrets in the Streamlit Cloud dashboard (see DEPLOYMENT.md)

## Usage

### Run the Streamlit App

```bash
streamlit run app.py
```

Then:
1. Enter your Coda API token in the sidebar (if not in .env)
2. Enter your Supabase URL and key (if not in .env)
3. Specify your Coda folder name (default: "ACTIVE")
4. Select a project from the dropdown
5. View project data from Supabase

## Customizing Supabase Data Integration

The app currently has a placeholder for Supabase data fetching. To customize it for your table structure:

1. Open `app.py`
2. Find the TODO comment in the Supabase data section
3. Replace the placeholder with your actual query:

```python
# Example: Fetch data from a 'projects' table
response = supabase.table('projects').select('*').eq('doc_id', selected_doc['id']).execute()
data = response.data
df = pd.DataFrame(data)
st.dataframe(df)

# Add visualizations
st.line_chart(df.set_index('date')['metric'])
```

## How It Works

1. **Coda Discovery**: The app uses the Coda API to:
   - List all folders in your workspace
   - Find the folder matching your specified name (e.g., "ACTIVE")
   - Automatically get all docs within that folder

2. **Supabase Connection**: The app connects to your Supabase project using the provided credentials

3. **Project Selection**: Users can select from dynamically discovered projects

4. **Data Display**: Each project page displays relevant data from Supabase (customizable)

## Data Structure

### Coda Docs
The app expects docs to be organized in a folder (default: "ACTIVE"). Each doc should have:
- `id`: Unique document identifier
- `name`: Document name (used as project name)
- `updatedAt`: Last modification timestamp

### Supabase Tables
You'll need to design your Supabase tables to match your project data needs. Common patterns:
- Link Coda doc IDs to Supabase records
- Store time-series data for metrics
- Track project status, tasks, or other attributes

## Deployment to Streamlit Community Cloud

### Quick Deploy

1. **Push your code to GitHub**
2. **Go to** https://share.streamlit.io/
3. **Click "New app"** and configure:
   - Repository: `Carpentry-Plus-Inc/Metrics`
   - Branch: `main`
   - Main file: `supabase-project-dashboard/app.py`
4. **Add secrets** in Streamlit Cloud settings:
   ```toml
   CODA_API_TOKEN = "your_api_token"
   SUPABASE_URL = "your_supabase_url"
   SUPABASE_KEY = "your_supabase_key"
   FOLDER_NAME = "ACTIVE"
   ```
5. **Deploy!**

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

## Troubleshooting

**"No docs found in folder"**
- Ensure the folder name is correct (case-sensitive)
- Check that your API token has access to the folder
- Verify the folder exists in your workspace

**"Failed to connect to Supabase"**
- Verify your Supabase URL and key are correct
- Ensure your Supabase project is active
- Check that the anon/public key has proper permissions

**"Error listing folders"**
- Check your Coda API token is valid
- Ensure you have permission to access the workspace
- Verify your internet connection

## Tips

- **Folder-based tracking**: When you add new docs to the "ACTIVE" folder, they'll automatically appear in the app
- **Custom folder names**: You can track any folder by changing the `FOLDER_NAME` configuration
- **Data visualization**: Use Plotly or Streamlit's built-in charts for rich visualizations
- **Row-level security**: Implement Supabase RLS policies for secure data access
