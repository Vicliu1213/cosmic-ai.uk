#!/usr/bin/env bash
set -e

# Set VS Code user data directory for root user
export CODE_USER_DATA_DIR="/tmp/vscode-user-data"
mkdir -p "$CODE_USER_DATA_DIR"

code --user-data-dir="$CODE_USER_DATA_DIR" --install-extension ms-python.python
code --user-data-dir="$CODE_USER_DATA_DIR" --install-extension ms-python.vscode-pylance
code --user-data-dir="$CODE_USER_DATA_DIR" --install-extension charliermarsh.ruff
code --user-data-dir="$CODE_USER_DATA_DIR" --install-extension eamodio.gitlens
code --user-data-dir="$CODE_USER_DATA_DIR" --install-extension GitHub.copilot
code --user-data-dir="$CODE_USER_DATA_DIR" --install-extension ms-vscode.makefile-tools
code --user-data-dir="$CODE_USER_DATA_DIR" --install-extension ms-python.debugpy
code --user-data-dir="$CODE_USER_DATA_DIR" --install-extension mhutchie.git-graph
code --user-data-dir="$CODE_USER_DATA_DIR" --install-extension tamasfe.even-better-toml
code --user-data-dir="$CODE_USER_DATA_DIR" --install-extension redhat.vscode-yaml
code --user-data-dir="$CODE_USER_DATA_DIR" --install-extension gruntfuggly.todo-tree
code --user-data-dir="$CODE_USER_DATA_DIR" --install-extension wayou.vscode-todo-highlight
code --user-data-dir="$CODE_USER_DATA_DIR" --install-extension chrisdias.vscode-opennewinstance

echo "✅ VS Code extensions installation completed!"
