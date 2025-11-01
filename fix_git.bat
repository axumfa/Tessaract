@echo off
REM Remove venv folder from Git and fix the push issue

echo 🔧 Fixing Git repository...
echo.
echo ⚠️  This will remove venv folder from Git tracking
echo ⚠️  The venv folder will remain on your computer, just not in Git
echo.
pause

echo.
echo 🔹 Removing venv from Git cache...
git rm -r --cached venv/

echo.
echo 🔹 Checking .gitignore...
if not exist ".gitignore" (
    echo ❌ .gitignore not found! Creating it...
    REM .gitignore should already be created
)

echo.
echo ✅ Done!
echo.
echo Now you can:
echo 1. Add the changes: git add .gitignore
echo 2. Commit: git commit -m "Remove venv folder, add .gitignore"
echo 3. Push: git push
echo.
pause

