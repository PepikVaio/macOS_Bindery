#!/bin/bash

# ╭─ Info ───────────────────────────────────────────────────────────────────────╮
# │ Builds the Bindery application for the current operating system.             │
# │                                                                              │
# │ macOS:  Creates the application icon and builds the macOS application.       │
# │ Windows: Creates the application icon and builds the Windows application.    │
# │                                                                              │
# │ How to use it:                                                               │
# │   ./build.sh                                                                 │
# ╰──────────────────────────────────────────────────────────────────────────────╯

if [[ "$OSTYPE" == "darwin"* ]]; then
    ./create_icon_mac.sh
    ./build_mac.sh

elif [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* || "$OSTYPE" == "win32" ]]; then
    ./create_icon_win.sh
    ./build_win.sh

else
    echo "Unsupported operating system."
    exit 1
fi
