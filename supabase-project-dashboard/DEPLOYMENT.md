# Deploying to Streamlit Community Cloud

This guide will help you deploy your Supabase Project Dashboard to Streamlit Community Cloud.

## Prerequisites

- GitHub account
- Streamlit Community Cloud account (sign up at https://share.streamlit.io/)
- Your code pushed to a GitHub repository
- Supabase project with API credentials
- Coda API token

## Step 1: Prepare Your Repository

Your code should be in the GitHub repository at `Carpentry-Plus-Inc/Metrics` in the `supabase-project-dashboard` folder.

### Commit Your Code

```bash
git add supabase-project-dashboard/
git commit -m "Add Supabase Project Dashboard"
git push origin main
```

## Step 2: Configure Secrets

In Streamlit Community Cloud, you'll need to add your secrets:

1. Go to https://share.streamlit.io/
2. Click on your deployed app (or during deployment setup)
3. Go to Settings → Secrets
4. Add the following in TOML format:

```toml
CODA_API_TOKEN = "your_actual_coda_api_token_here"
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your_supabase_anon_key_here"
FOLDER_NAME = "ACTIVE"
```

**Important:** Replace the values with your actual credentials.

### Where to Find Credentials

**Coda API Token:**
- Go to https://coda.io/account
- Scroll to "API Settings"
- Generate and copy your API token

**Supabase URL:**
- Go to your Supabase project dashboard
- Navigate to Settings → API
- Copy the "Project URL"

**Supabase Key:**
- In the same Settings → API section
- Copy the "anon/public" key

## Step 3: Deploy

1. Go to https://share.streamlit.io/
2. Click "New app"
3. Fill in the deployment form:
   - **Repository**: `Carpentry-Plus-Inc/Metrics`
   - **Branch**: `main`
   - **Main file path**: `supabase-project-dashboard/app.py`
4. Click "Deploy"

## Step 4: Wait for Deployment

Streamlit will:
- Install dependencies from `requirements.txt`
- Start your app
- Provide you with a public URL

## Step 5: Configure Secrets (if not done during setup)

If you didn't add secrets during deployment:
1. Go to your app dashboard on Streamlit Cloud
2. Click "Settings"
3. Click "Secrets"
4. Add the TOML configuration shown in Step 2
5. Click "Save"
6. Your app will automatically redeploy

## Updating Your Deployed App

Any time you push changes to the `main` branch on GitHub, Streamlit Community Cloud will automatically redeploy your app.

## Troubleshooting

### "No module named 'supabase'"
Make sure `supabase>=2.0.0` is in your `requirements.txt`

### "Unable to deploy - not connected to GitHub"
Make sure your local code is committed and pushed to GitHub

### Secrets not loading
Double-check the TOML format in Streamlit Cloud secrets settings. Keys should match exactly:
- `CODA_API_TOKEN`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `FOLDER_NAME` (optional, defaults to "ACTIVE")

### App crashes on startup
Check the logs in Streamlit Cloud dashboard for specific error messages. Common issues:
- Invalid API tokens
- Supabase project not accessible
- Coda folder not found

### "Error listing folders"
- Verify your Coda API token is valid
- Ensure the token has proper permissions
- Check that the folder name exists in your workspace

### "Failed to connect to Supabase"
- Verify your Supabase URL is correct (should include https://)
- Ensure the anon/public key is valid
- Check that your Supabase project is active

## Local vs Cloud Configuration

The app supports both local development and cloud deployment:

- **Local**: Uses `.env` file (not committed to git)
- **Cloud**: Uses Streamlit secrets (configured in cloud dashboard)

The app automatically detects which environment it's running in and uses the appropriate configuration source.

## Security Best Practices

1. **Never commit secrets**: The `.env` file is in `.gitignore` to prevent accidental commits
2. **Use environment-specific keys**: Consider using different API keys for development and production
3. **Supabase RLS**: Implement Row Level Security policies in Supabase to control data access
4. **Rotate keys regularly**: Periodically update your API tokens and keys

## Performance Optimization

For better performance with large datasets:
- Implement pagination in Supabase queries
- Use Supabase indexes on frequently queried columns
- Cache data when appropriate
- Consider using Supabase's real-time subscriptions for live updates

## Monitoring

Streamlit Cloud provides:
- Resource usage metrics
- Error logs
- Deployment history
- App analytics

Monitor these regularly to ensure your app is performing well.
