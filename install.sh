#!/usr/bin/env bash
# One-line installer for craigm26/antigravity-plugins
# Remote: curl -fsSL https://raw.githubusercontent.com/craigm26/antigravity-plugins/main/install.sh | bash
# Single: curl -fsSL https://raw.githubusercontent.com/craigm26/antigravity-plugins/main/install.sh | bash -s -- --plugin robot-md
set -euo pipefail

PLUGIN="all"
PYTHON_BIN="$(command -v python3 || true)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --plugin) PLUGIN="${2:?missing plugin name}"; shift 2 ;;
    --python) PYTHON_BIN="${2:?missing python path}"; shift 2 ;;
    *) PYTHON_BIN="$1"; shift ;;
  esac
done

if [[ -z "$PYTHON_BIN" ]]; then
  echo "Error: python3 not found on PATH. Pass --python /path/to/python3." >&2
  exit 1
fi

TMP_DIR=""
cleanup() { [[ -n "$TMP_DIR" ]] && rm -rf "$TMP_DIR"; }
trap cleanup EXIT

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || true)"
if [[ -n "$SCRIPT_DIR" && -d "$SCRIPT_DIR/plugins" ]]; then
  SRC_ROOT="$SCRIPT_DIR"
else
  TMP_DIR="$(mktemp -d)"
  echo "Downloading craigm26/antigravity-plugins..."
  git clone --depth 1 --quiet https://github.com/craigm26/antigravity-plugins.git "$TMP_DIR/repo"
  SRC_ROOT="$TMP_DIR/repo"
fi

TARGET="${HOME}/.gemini/config/plugins"
mkdir -p "$TARGET"

if [[ "$PLUGIN" == "all" ]]; then
  LIST=(robot-md graftfork)
else
  LIST=("$PLUGIN")
fi

for name in "${LIST[@]}"; do
  if [[ ! -d "$SRC_ROOT/plugins/$name" ]]; then
    echo "Unknown plugin: $name (available: robot-md, graftfork)" >&2
    exit 1
  fi
  rm -rf "$TARGET/$name"
  cp -r "$SRC_ROOT/plugins/$name" "$TARGET/$name"
  sed -i "s|\"command\": \"python3\"|\"command\": \"${PYTHON_BIN}\"|g" "$TARGET/$name/mcp_config.json"
  echo "Installed $name -> $TARGET/$name (python: $PYTHON_BIN)"
done

echo ""
echo "Done! Antigravity discovers plugins in ~/.gemini/config/plugins/ automatically."
echo "Open Robot-MD Console or GraftFork Inspector from the side pane '+' menu or sidebar."
