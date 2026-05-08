# Deploying to Streamlit Community Cloud

This guide will help you deploy your Coda Progress Tracker to Streamlit Community Cloud.

## Prerequisites

- GitHub account
- Streamlit Community Cloud account (sign up at https://share.streamlit.io/)
- Your code pushed to a GitHub repository

## Step 1: Prepare Your Repository

Your code should already be in the GitHub repository at `Carpentry-Plus-Inc/Metrics` in the `coda-progress-tracker` folder.

## Step 2: Configure Secrets

In Streamlit Community Cloud, you'll need to add your secrets:

1. Go to https://share.streamlit.io/
2. Click on your deployed app (or during deployment setup)
3. Go to Settings → Secrets
4. Add the following in TOML format:

```toml
CODA_API_TOKEN = "your_actual_api_token_here"
DOC_IDS = "nFrKoFvzyS,vHO5EIKhUx,hLlbizQWCQ"
```

**Important:** Replace the values with your actual credentials.

## Step 3: Deploy

1. Go to https://share.streamlit.io/
2. Click "New app"
3. Fill in the deployment form:
   - **Repository**: `Carpentry-Plus-Inc/Metrics`
   - **Branch**: `main`
   - **Main file path**: `coda-progress-tracker/app.py`
4. Click "Deploy"

## Step 4: Wait for Deployment

Streamlit will:
- Install dependencies from `requirements.txt`
- Start your app
- Provide you with a public URL

## Updating Your Deployed App

Any time you push changes to the `main` branch on GitHub, Streamlit Community Cloud will automatically redeploy your app.

## Troubleshooting

### "No module named 'dotenv'"
Make sure `python-dotenv` is in your `requirements.txt`

### "Unable to deploy - not connected to GitHub"
Make sure your local code is committed and pushed to GitHub

### Secrets not loading
Double-check the TOML format in Streamlit Cloud secrets settings. Keys should match exactly: `CODA_API_TOKEN` and `DOC_IDS`

### App crashes on startup
Check the logs in Streamlit Cloud dashboard for specific error messages

## Local vs Cloud Configuration

The app supports both local development and cloud deployment:

- **Local**: Uses `.env` file (not committed to git)
- **Cloud**: Uses Streamlit secrets (configured in cloud dashboard)

The app automatically detects which environment it's running in and uses the appropriate configuration source.
