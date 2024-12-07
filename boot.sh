#!/bin/bash
# This script is used to boot a Docker container

# Set maximum retry attempts for database upgrade
MAX_RETRIES=5
COUNT=0

# Check if flask and gunicorn are installed
if ! command -v flask &> /dev/null || ! command -v gunicorn &> /dev/null; then
    echo "Error: flask or gunicorn command not found."
    exit 1
fi

# Run flask db upgrade in a retry loop with a max retry count
while [[ $COUNT -lt $MAX_RETRIES ]]; do
    flask db upgrade
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo "Deploy command failed, retrying in 5 secs... ($((COUNT+1))/$MAX_RETRIES)"
    sleep 5
    COUNT=$((COUNT + 1))
done

# Check if max retries were reached
if [[ $COUNT -eq $MAX_RETRIES ]]; then
    echo "Error: Database migration failed after multiple attempts. Please check the database connection and migration files."
    exit 1
fi

# Start gunicorn with environment-variable-based port (default to 5000 if not set)
exec gunicorn -b :5000 --access-logfile - --error-logfile - blog:app
