@echo off
REM memory-dual-brain-sync.bat
REM Windows batch script to run Memory Dual-Brain Sync System (OneShot Version)
REM Fixed to prevent infinite loops by using static rule files

echo 🧠 Starting Memory Dual-Brain Sync System...

REM Set environment variables
set EXECUTION_BRAIN=./memory-rules.mdc
set QUALITY_BRAIN=./memory-rating.mdc
set VERBOSE=1
set AUTO_ACTIVATE=true
set MAX_RETRIES=3
set METRICS_PATH=./memory-sync-metrics.json

echo 📋 Configuration:
echo   EXECUTION_BRAIN: %EXECUTION_BRAIN%
echo   QUALITY_BRAIN: %QUALITY_BRAIN%
echo   VERBOSE: %VERBOSE%
echo   AUTO_ACTIVATE: %AUTO_ACTIVATE%

echo.
echo 🚀 Executing memory-dual-brain-sync-oneshot.js...
echo 🚫 Rule files will remain static - no auto-modification
node memory-dual-brain-sync-oneshot.js

echo.
echo ✅ Memory Dual-Brain Sync completed!
echo 📊 Check memory-sync-metrics.json for detailed metrics
echo 🎯 Rule files preserved as static - infinite loop prevented
pause
