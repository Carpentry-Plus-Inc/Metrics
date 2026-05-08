# How to Push Your Code to GitHub

This guide will help you commit and push your Coda Progress Tracker code to GitHub.

## Option 1: Using GitHub Desktop (Easiest)

If you have GitHub Desktop installed:

1. Open GitHub Desktop
2. Select the `Metrics` repository
3. You should see all your changes in the left panel
4. Add a commit message (e.g., "Add Coda Progress Tracker app")
5. Click "Commit to main"
6. Click "Push origin" to push to GitHub

## Option 2: Using Git Command Line

If Git is installed and in your PATH:

```bash
# Navigate to your repository
cd C:\Users\Dan\Documents\GitHub\Metrics

# Check what files have changed
git status

# Add all files in the coda-progress-tracker folder
git add coda-progress-tracker/

# Commit with a message
git commit -m "Add Coda Progress Tracker Streamlit app"

# Push to GitHub
git push origin main
```

## Option 3: Using VS Code Source Control

If you're using VS Code:

1. Open the `Metrics` folder in VS Code
2. Click the Source Control icon in the left sidebar (looks like a branch)
3. You'll see all changed files
4. Click the "+" icon next to each file to stage them
5. Enter a commit message in the text box at the top
6. Click the checkmark to commit
7. Click the "..." menu and select "Push"

## What Files to Commit

Make sure these files are included:
- ✅ `coda-progress-tracker/app.py`
- ✅ `coda-progress-tracker/fetch_data.py`
- ✅ `coda-progress-tracker/requirements.txt`
- ✅ `coda-progress-tracker/README.md`
- ✅ `coda-progress-tracker/DEPLOYMENT.md`
- ✅ `coda-progress-tracker/.gitignore`
- ✅ `coda-progress-tracker/.streamlit/config.toml`
- ✅ `coda-progress-tracker/.streamlit/secrets.toml.example`

Make sure these files are NOT committed (they're in .gitignore):
- ❌ `coda-progress-tracker/.env`
- ❌ `coda-progress-tracker/.streamlit/secrets.toml`
- ❌ `coda-progress-tracker/progress_history.csv`

## Verify on GitHub

After pushing:
1. Go to https://github.com/Carpentry-Plus-Inc/Metrics
2. You should see the `coda-progress-tracker` folder
3. Click into it and verify all files are there

## Next Steps

Once your code is on GitHub, you can deploy to Streamlit Community Cloud!
See [DEPLOYMENT.md](DEPLOYMENT.md) for instructions.
