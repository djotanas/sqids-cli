#!/usr/bin/env bash
# Installs (or updates) sqid-convert without cloning the repository.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/djotanas/sqids-cli/main/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/djotanas/sqids-cli/main/install.sh | bash -s -- --uninstall
#
# Environment:
#   INSTALL_DIR   target directory (default: ~/.local/bin)
#   SQIDS_CLI_REF branch, tag or commit to install from (default: main)
set -euo pipefail

INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/bin}"
REF="${SQIDS_CLI_REF:-main}"
BASE_URL="https://raw.githubusercontent.com/djotanas/sqids-cli/$REF"
FILES=(sqid-convert sqid_convert.py)

if [[ "${1:-}" == "--uninstall" ]]; then
  for f in "${FILES[@]}"; do
    rm -f "$INSTALL_DIR/$f"
  done
  echo "sqid-convert removed from $INSTALL_DIR."
  echo "Config kept at ${XDG_CONFIG_HOME:-$HOME/.config}/sqid-convert (delete it manually if you want)."
  exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but was not found." >&2
  exit 1
fi

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

for f in "${FILES[@]}"; do
  curl -fsSL "$BASE_URL/$f" -o "$tmp_dir/$f"
done

mkdir -p "$INSTALL_DIR"
for f in "${FILES[@]}"; do
  chmod +x "$tmp_dir/$f"
  mv -f "$tmp_dir/$f" "$INSTALL_DIR/$f"
done

echo "sqid-convert installed to $INSTALL_DIR."
case ":$PATH:" in
  *":$INSTALL_DIR:"*) ;;
  *) echo "Warning: $INSTALL_DIR is not in your PATH. Add it to use sqid-convert." >&2 ;;
esac
