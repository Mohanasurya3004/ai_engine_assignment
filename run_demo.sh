#!/bin/bash
echo "Starting uvicorn..."
uvicorn app.main:app --reload --port 8000
