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

echo Staging all project files...
git add .

echo Committing Member A, Member B, and Member C implementation files...
git commit -m "Complete Member A (ML), Member B (Backend & Routing), and Member C (GIS Dashboard, PWA & Flutter App) implementation, tests, and docs"

echo Pushing to GitHub (https://github.com/Kkushak16/MargSetu.git)...
git push -u origin main --force

echo ========================================================
echo [SUCCESS] Repository synced successfully with GitHub!
echo ========================================================
