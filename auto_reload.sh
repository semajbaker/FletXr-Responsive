#!/bin/bash
PORT=8000

# Ensure unbuffered output
export PYTHONUNBUFFERED=1
export PYTHONIOENCODING=utf-8

# Function to flush output immediately
flush_output() {
    exec 1> >(stdbuf -o0 cat)
    exec 2> >(stdbuf -o0 cat >&2)
}

# Enable immediate output flushing
flush_output

# Function to get modification times of all .py files
get_py_files_mtime() {
    find . -name "*.py" -not -path "./.git/*" -not -path "./__pycache__/*" -exec stat -c "%Y %n" {} \; 2>/dev/null | sort
}

# Function to find changed files
find_changed_files() {
    local temp_file="/tmp/py_files_current"
    get_py_files_mtime > "$temp_file"
    
    if [ -f "/tmp/py_files_last" ]; then
        diff "/tmp/py_files_last" "$temp_file" | grep "^>" | sed 's/^> //' | while read line; do
            echo "  Changed: $(echo $line | cut -d' ' -f2-)" | stdbuf -o0 cat
        done
    fi
    
    mv "$temp_file" "/tmp/py_files_last"
}

# Function to check if app is responding
wait_for_app() {
    echo "⏳ Waiting for app to be ready..." | stdbuf -o0 cat
    local max_attempts=15
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "http://localhost:$PORT" > /dev/null 2>&1; then
            echo "✅ App is ready and responding on http://localhost:$PORT" | stdbuf -o0 cat
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done
    
    echo "⚠️ App may still be starting (timeout reached)" | stdbuf -o0 cat
    return 1
}

# Function to kill all related processes
kill_all_app_processes() {
    # Kill by process group if we have the PID
    if [ -n "$APP_PID" ]; then
        kill -TERM -$APP_PID 2>/dev/null
        sleep 2
        kill -KILL -$APP_PID 2>/dev/null
        wait $APP_PID 2>/dev/null
    fi
    
    # Kill any remaining flet processes
    pkill -f "flet run" 2>/dev/null || true
    pkill -f "main.py" 2>/dev/null || true
    
    # Kill any python processes running our script
    pgrep -f "main.py" | while read pid; do
        if [ "$pid" != "$$" ]; then
            kill -KILL $pid 2>/dev/null || true
        fi
    done
    
    sleep 2
}

# Function to start the app
start_app() {
    echo "🚀 Starting Flet app..." | stdbuf -o0 cat
    kill_all_app_processes
    # Use stdbuf to ensure unbuffered output from Python
    setsid stdbuf -o0 -e0 fletx run --web --host 0.0.0.0 --port $PORT &
    APP_PID=$!
    wait_for_app
}

# Cleanup on script exit
trap 'echo "🛑 Shutting down..." | stdbuf -o0 cat; kill_all_app_processes' EXIT

echo "🔄 Auto-reload script started" | stdbuf -o0 cat
echo "📁 Monitoring Python files for changes..." | stdbuf -o0 cat

# Initialize file tracking
LAST_PY_FILES=$(get_py_files_mtime)

# Start the initial app
start_app

echo "👀 Watching for file changes... (Press Ctrl+C to stop)" | stdbuf -o0 cat

while true; do
    sleep 2
    CURRENT_PY_FILES=$(get_py_files_mtime)
    if [ "$CURRENT_PY_FILES" != "$LAST_PY_FILES" ]; then
        echo "" | stdbuf -o0 cat
        echo "📝 File change detected:" | stdbuf -o0 cat
        find_changed_files
        echo "🔄 Restarting app..." | stdbuf -o0 cat
        LAST_PY_FILES="$CURRENT_PY_FILES"
        start_app
        echo "✨ Restart complete!" | stdbuf -o0 cat
        echo "" | stdbuf -o0 cat
    fi
done