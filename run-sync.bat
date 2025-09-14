@echo off
setlocal
@echo off
setlocal ENABLEDELAYEDEXPANSION
REM memory-dual-brain-sync.bat (ASCII safe)

REM Configuration (Memory system)
set "EXECUTION_BRAIN=./memory-rules.mdc"
set "QUALITY_BRAIN=./memory-rating.mdc"
set "VERBOSE=1"
set "AUTO_ACTIVATE=true"
set "MAX_RETRIES=3"
set "METRICS_PATH=./memory-sync-metrics.json"

REM Configuration (RAG)
if not defined RAG_ENABLE set "RAG_ENABLE=1"
if not defined RAG_PROFILE set "RAG_PROFILE=vscode"
if not defined RAG_WATCH set "RAG_WATCH=1"
if not defined RAG_EVAL set "RAG_EVAL=1"
if not defined RAG_INDEX_DIR set "RAG_INDEX_DIR=.rag\index.%RAG_PROFILE%"
set "VENV_PY=.venv\Scripts\python.exe"

echo == Memory Dual-Brain Sync ==
echo EXECUTION_BRAIN: %EXECUTION_BRAIN%
echo QUALITY_BRAIN: %QUALITY_BRAIN%
echo VERBOSE: %VERBOSE%
echo AUTO_ACTIVATE: %AUTO_ACTIVATE%
echo RAG_ENABLE: %RAG_ENABLE%
echo RAG_PROFILE: %RAG_PROFILE%
echo RAG_WATCH: %RAG_WATCH%
echo RAG_EVAL: %RAG_EVAL%
echo.

REM Run oneshot JS if Node is available
where node >NUL 2>&1
if %ERRORLEVEL%==0 (
	echo Running memory-dual-brain-sync-oneshot.js ...
	node "memory-dual-brain-sync-oneshot.js" || echo WARNING: memory sync returned non-zero exit
) else (
	echo WARNING: Node.js not found in PATH, skipping memory sync JS
)

REM RAG bootstrap
REM Robust truthy check for RAG_ENABLE
if /I "%RAG_ENABLE%"=="1" goto rag_bootstrap
if /I "%RAG_ENABLE%"=="true" goto rag_bootstrap
if /I "%RAG_ENABLE%"=="yes" goto rag_bootstrap
if /I "%RAG_ENABLE%"=="on" goto rag_bootstrap
if not "%RAG_ENABLE%"=="" if not "%RAG_ENABLE%"=="0" goto rag_bootstrap
goto end

:rag_bootstrap
echo.
echo == RAG Bootstrap ==
REM Sanitize profile (remove spaces)
set "RAG_PROFILE=!RAG_PROFILE: =!"
echo Using RAG profile: !RAG_PROFILE!
REM Recompute and sanitize index dir based on sanitized profile
set "RAG_INDEX_DIR=.rag\index.!RAG_PROFILE!"
echo Using RAG index dir: !RAG_INDEX_DIR!
if not exist ".rag" mkdir ".rag"
if not exist "!RAG_INDEX_DIR!" mkdir "!RAG_INDEX_DIR!"
if not exist .venv (
	echo Creating Python venv ...
	where py >NUL 2>&1
	if %ERRORLEVEL%==0 (
		py -3 -m venv .venv || (echo ERROR: Failed to create venv & goto end)
	) else (
		where python >NUL 2>&1 || (echo ERROR: python not found & goto end)
		python -m venv .venv || (echo ERROR: Failed to create venv & goto end)
	)
)

if not exist "%VENV_PY%" (
	echo ERROR: Python executable not found at %VENV_PY%
	goto end
)

echo Installing requirements ...
"%VENV_PY%" -m pip install --upgrade pip >NUL 2>&1
"%VENV_PY%" -m pip install -r requirements-rag.txt || (echo ERROR: pip install failed & goto end)

echo Building RAG index for profile=!RAG_PROFILE! ...
"%VENV_PY%" tools\rag_indexer.py build --root . --index-path "%RAG_INDEX_DIR%" --profile !RAG_PROFILE! || (echo ERROR: RAG build failed & goto end)

if "%RAG_EVAL%"=="1" (
	if exist tests\rag-cases.yaml (
		echo Running RAG harness tests ...
		"%VENV_PY%" tools\rag_eval.py --index-path "%RAG_INDEX_DIR%" --profile !RAG_PROFILE! --cases tests\rag-cases.yaml || echo WARNING: RAG eval had failures
	) else (
		echo INFO: tests\rag-cases.yaml not found, skipping eval
	)
)

if "%RAG_WATCH%"=="1" (
	echo Starting RAG watch in background ...
		start "RAG Watch" "%VENV_PY%" tools\rag_indexer.py watch --root . --index-path "%RAG_INDEX_DIR%" --profile !RAG_PROFILE! --interval 2 --quiet
)

:end
echo.
echo All done.
endlocal
pause
