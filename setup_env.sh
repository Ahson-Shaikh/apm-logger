#!/bin/bash

# Setup environment variables for APM Logger

# Install dependencies
echo "Installing dependencies..."
pip install fastapi uvicorn requests elastic-apm psutil

# APM Configuration
export APM_SERVER_URL="http://localhost:8200"
export SERVICE_NAME="elk-test-api"
export ENVIRONMENT="dev"

echo ""
echo "Environment variables set:"
echo "APM_SERVER_URL: $APM_SERVER_URL"
echo "SERVICE_NAME: $SERVICE_NAME"
echo "ENVIRONMENT: $ENVIRONMENT"
echo ""
echo "To run the application:"
echo "uvicorn app:app --host 0.0.0.0 --port 8000"
echo ""
echo "To test endpoints, see README.md for curl examples"
echo ""
echo "Note: Make sure your Elastic APM server is running at $APM_SERVER_URL"
echo "The APM agent will queue events until connection is established" 