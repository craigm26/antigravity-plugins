#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${HOME}/.gemini/config/plugins"
PYTHON_BIN="${1:-$(command -v python3)}"

mkdir -p "$TARGET"
for plugin in robot-md graftfork; do
  rm -rf "$TARGET/$plugin"
  cp -r "$ROOT/plugins/$plugin" "$TARGET/$plugin"
  sed -i "s|\"command\": \"python3\"|\"command\": \"${PYTHON_BIN}\"|g" "$TARGET/$plugin/mcp_config.json"
  echo "Installed $plugin -> $TARGET/$plugin (python: $PYTHON_BIN)"
done

echo "Done! Antigravity will auto-discover robot-md and graftfork live."
