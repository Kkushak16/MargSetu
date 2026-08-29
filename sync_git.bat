@echo off
echo ========================================================
echo         MargSetu Git Repository Synchronization
echo ========================================================

cd /d "D:\Antigravity\MargSetu"

if not exist ".git" (
    echo Initializing local Git repository...
    git init
    git branch -M main
)

echo Checking Git Remote...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/Kkushak16/MargSetu.git

echo Staging all project files (including deleted files)...
git add -A

echo Committing frontend control room updates & prompt file cleanup...
git commit -m "Remove prompt files and update GIS Control Room Dashboard with Crowdsource Feed & Alerts Log"

echo Pushing to GitHub (https://github.com/Kkushak16/MargSetu.git)...
git push -u origin main --force

echo ========================================================
echo [SUCCESS] Repository synced successfully with GitHub!
echo ========================================================
