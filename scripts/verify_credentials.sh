#!/bin/bash
echo "Checking credentials file..."
if [ -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "Found credentials at $GOOGLE_APPLICATION_CREDENTIALS"
    python3 -c "import json; json.load(open('$GOOGLE_APPLICATION_CREDENTIALS'))"
    if [ $? -eq 0 ]; then
        echo "Credentials JSON is valid"
    else
        echo "Invalid JSON in credentials file"
        exit 1
    fi
else
    echo "Credentials file not found"
    exit 1
fi 