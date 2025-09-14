#!/bin/bash
# memory-dual-brain-sync.sh
# Unix/Linux shell script to run Memory Dual-Brain Sync System (OneShot Version)
# Fixed to prevent infinite loops by using static rule files

echo "🧠 Starting Memory Dual-Brain Sync System..."

# Set environment variables
export EXECUTION_BRAIN=./memory-rules.mdc
export QUALITY_BRAIN=./memory-rating.mdc
export VERBOSE=1
export AUTO_ACTIVATE=true
export MAX_RETRIES=3
export METRICS_PATH=./memory-sync-metrics.json

# ---------------- RAG AUTOMATION (config) ----------------
: "${RAG_ENABLE:=1}"
: "${RAG_PROFILE:=vscode}"
: "${RAG_WATCH:=1}"
: "${RAG_EVAL:=1}"
: "${RAG_INDEX_DIR:=.rag/index.${RAG_PROFILE}}"
VENV_PY=".venv/bin/python"

echo "📋 Configuration:"
echo "  EXECUTION_BRAIN: $EXECUTION_BRAIN"
echo "  QUALITY_BRAIN: $QUALITY_BRAIN"
echo "  VERBOSE: $VERBOSE"
echo "  AUTO_ACTIVATE: $AUTO_ACTIVATE"

echo ""
echo "🚀 Executing memory-dual-brain-sync-oneshot.js..."
echo "🚫 Rule files will remain static - no auto-modification"
node memory-dual-brain-sync-oneshot.js

# ---------------- RAG AUTOMATION (bootstrap) ----------------
if [ "${RAG_ENABLE}" = "1" ]; then
	echo ""
	echo "🧩 RAG bootstrap starting..."
	if [ ! -d ".venv" ]; then
		echo "🔧 Creating Python venv..."
		python3 -m venv .venv || { echo "❌ Failed to create venv"; exit 1; }
	fi
	if [ ! -x "$VENV_PY" ]; then
		echo "❌ Python executable not found at $VENV_PY"; exit 1;
	fi
	echo "📦 Installing requirements..."
	"$VENV_PY" -m pip install --upgrade pip >/dev/null 2>&1
	"$VENV_PY" -m pip install -r requirements-rag.txt || { echo "❌ pip install failed"; exit 1; }

	echo "🧱 Building RAG index for profile=${RAG_PROFILE}..."
	"$VENV_PY" tools/rag_indexer.py build --root . --index-path "${RAG_INDEX_DIR}" --profile "${RAG_PROFILE}" || { echo "❌ RAG build failed"; exit 1; }

	if [ "${RAG_EVAL}" = "1" ]; then
		if [ -f tests/rag-cases.yaml ]; then
			echo "🧪 Running RAG harness tests..."
			"$VENV_PY" tools/rag_eval.py --index-path "${RAG_INDEX_DIR}" --profile "${RAG_PROFILE}" --cases tests/rag-cases.yaml || echo "⚠ RAG eval had failures"
		else
			echo "ℹ tests/rag-cases.yaml not found, skipping eval"
		fi
	fi

	if [ "${RAG_WATCH}" = "1" ]; then
		echo "👀 Starting RAG watch in background..."
		nohup "$VENV_PY" tools/rag_indexer.py watch --root . --index-path "${RAG_INDEX_DIR}" --profile "${RAG_PROFILE}" --interval 2 --quiet >/dev/null 2>&1 &
	fi
fi

echo ""
echo "✅ Memory Dual-Brain Sync completed!"
echo "📊 Check memory-sync-metrics.json for detailed metrics"
echo "🎯 Rule files preserved as static - infinite loop prevented"
