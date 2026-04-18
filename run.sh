#!/bin/bash
echo "Starting AI Text to Human-Readable Pipeline..."
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo ""
echo "Starting server on http://localhost:8000"
echo ""
python backend.py
