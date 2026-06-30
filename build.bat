@echo off
cd /d %~dp0
echo Building app.js from src/app.jsx...
call npm run build
if %ERRORLEVEL% NEQ 0 (
  echo BUILD FAILED. Check errors above.
  pause
  exit /b 1
)
echo.
echo Done. Restart Flask server to pick up changes.
pause
