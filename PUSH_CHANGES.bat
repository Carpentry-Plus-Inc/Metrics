@echo off
echo Pushing changes to GitHub...
cd /d "C:\Users\Dan\Documents\GitHub\Metrics"

echo.
echo Adding files...
git add coda-progress-tracker/requirements.txt

echo.
echo Committing...
git commit -m "Fix requirements.txt for Python 3.14 compatibility"

echo.
echo Pushing to GitHub...
git push origin main

echo.
echo Done! Check Streamlit Cloud for automatic redeployment.
pause
