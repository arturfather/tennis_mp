#!/bin/bash

# Define the log file path
LOG_FILE="/root/my_bots/tt_bot/logs/logger.txt"

# Get the current time
time_now=$(date +"%Y-%m-%d %H:%M:%S")

# Check if the bot process is running
if ! pgrep -f "python tt_bot.py" >/dev/null; then
    echo "$time_now Bot is not running. Restarting..." >> "$LOG_FILE"
    
    # Activate the virtual environment
    source /root/my_bots/tt_bot/venv_tt/bin/activate
    
    # Change directory to the bot's location
    cd /root/my_bots/tt_bot/
    
    # Restart the bot and redirect output
    nohup python tt_bot.py > /dev/null 2>> "$LOG_FILE" &
#else
#   echo "$time_now Bot is already running." >> "$LOG_FILE"
fi