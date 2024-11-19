#!/bin/bash

APP_NAME="OpenScope_V1"
SCRIPT_DIR=$(dirname "$(realpath "$0")")  
EXEC_PATH="$SCRIPT_DIR/main.py"
REQUIREMENTS_FILE="$SCRIPT_DIR/requierments.txt"
DESKTOP_ENTRY_PATH="$HOME/.local/share/applications/${APP_NAME}.desktop"
ICON_PATH="$SCRIPT_DIR/photos/logo.png"  
VENV_DIR="$SCRIPT_DIR/venv"


echo "Checking for tkinter..."
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "tkinter not found. Installing python3-tk..."
    sudo apt update
    sudo apt install -y python3-tk
else
    echo "tkinter is already installed."
fi


echo "Setting up a virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi


echo "Installing Python requirements..."
source "$VENV_DIR/bin/activate"
if [ -f "$REQUIREMENTS_FILE" ]; then
    pip install -r "$REQUIREMENTS_FILE"
else
    echo "Error: $REQUIREMENTS_FILE not found!"
    deactivate
    exit 1
fi
deactivate


echo "Creating a desktop entry..."
cat > "$DESKTOP_ENTRY_PATH" <<EOL
[Desktop Entry]
Version=1.0
Type=Application
Name=$APP_NAME
Exec=$VENV_DIR/bin/python $EXEC_PATH
Icon=$ICON_PATH
Terminal=false
Categories=Utility;
EOL


chmod +x "$DESKTOP_ENTRY_PATH"


echo "Installation complete! You can now find '$APP_NAME' in your application menu."
