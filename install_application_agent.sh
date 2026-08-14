#!/usr/bin/env bash
set -e

echo "Installing Python dependencies..."
python -m pip install -r requirements.txt

echo "Installing Playwright Chromium..."
python -m playwright install chromium

echo "Running Application Agent tests..."
python -m pytest tests/test_application_browser.py -q

echo
echo "Setup complete."
echo "Start the app with:"
echo "streamlit run app.py --server.port 8502"
