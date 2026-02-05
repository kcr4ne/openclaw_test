@echo off
:: Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [JARVIS] Administrator privileges confirmed.
) else (
    echo [JARVIS] Requesting Administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo [JARVIS] Starting System Core (Background)...
:: Start Python Backend hidden
start /B .\venv\Scripts\pythonw.exe main.py

echo [JARVIS] Starting Interface (Background)...
cd interface
:: Start Next.js hidden (using powershell wrapper to hide window)
powershell -Command "Start-Process npm -ArgumentList 'run dev' -WindowStyle Hidden"

echo [JARVIS] All Systems Online. Opening Dashboard...
timeout /t 3 >nul
start http://localhost:3000

echo [JARVIS] Setup Complete. This window will close in 5 seconds.
timeout /t 5 >nul
exit
