#!/bin/bash

# Exit on any error
set -e

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SCRIPT_NAME="dns_updater.py"
VENV_DIR="$SCRIPT_DIR/venv"

cd $SCRIPT_DIR

# Set up Python virtual environment
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

# Install requirements in the virtual environment
pip3 install -qq requests
chmod +x $SCRIPT_NAME

# Set up the cron job
VENV_PYTHON="$VENV_DIR/bin/python3"
JOB="$VENV_PYTHON $SCRIPT_DIR/$SCRIPT_NAME"
CRON_JOB="*/30 * * * * $JOB"
$JOB

# Add the cron job
(crontab -l 2>/dev/null || echo "") | grep -v "$SCRIPT_NAME" | { cat; echo "$CRON_JOB"; } | crontab -

echo "Setup completed successfully."
echo "To edit the cron job, run 'crontab -e'"
