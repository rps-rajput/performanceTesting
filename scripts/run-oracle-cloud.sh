#!/usr/bin/env bash
# Run PerfTestpro on Oracle Cloud (or any Linux server).
# Bind to 0.0.0.0 so the app is reachable from the internet.
# Usage: ./scripts/run-oracle-cloud.sh   OR   bash scripts/run-oracle-cloud.sh

set -e
cd "$(dirname "$0")/.."
PORT="${PORT:-8501}"
exec streamlit run streamlit_app.py --server.port="$PORT" --server.address=0.0.0.0
