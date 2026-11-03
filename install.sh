#!/usr/bin/env bash
# Installs (or updates) sqid-convert without cloning the repository.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/djotanas/sqids-cli/main/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/djotanas/sqids-cli/main/install.sh | bash -s -- --uninstall
#
# Environment:
#   INSTALL_DIR     target directory (default: ~/.local/bin)
#   SQIDS_CLI_REF   branch, tag or commit to install from (default: main)
#   NO_MODIFY_PATH  set to 1 to skip adding INSTALL_DIR to your shell startup files
#
# Why the current terminal may still not find the command:
#   `curl ... | bash` runs this script in a child process, and a child process
#   cannot change the environment (PATH) of the shell that started it. So the
#   installer adds INSTALL_DIR to your shell startup files, which every new
#   terminal reads; for the terminal you are already in, reload it with
#   `exec "$SHELL"` (or open a new one).
set -euo pipefail

INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/bin}"
INSTALL_DIR="${INSTALL_DIR%/}"
REF="${SQIDS_CLI_REF:-main}"
BASE_URL="https://raw.githubusercontent.com/djotanas/sqids-cli/$REF"
FILES=(sqid-convert sqid_convert.py)

MARK_BEGIN="# >>> sqid-convert >>>"
MARK_END="# <<< sqid-convert <<<"

# Shell startup files that get the PATH snippet: the ones of your login shell,
# plus any of these that already exist.
rc_files() {
  local files=() f
  case "$(basename "${SHELL:-}")" in
    zsh)  files+=("${ZDOTDIR:-$HOME}/.zshrc") ;;
    bash) files+=("$HOME/.bashrc") ;;
  esac
  for f in "$HOME/.bashrc" "$HOME/.bash_profile" "$HOME/.zshrc" "$HOME/.profile"; do
    [[ -f "$f" ]] && files+=("$f")
  done
  [[ ${#files[@]} -eq 0 ]] && files+=("$HOME/.profile")
  printf '%s\n' "${files[@]}" | awk '!seen[$0]++'
}

remove_path_snippet() {
  local f="$1" tmp
  [[ -f "$f" ]] && grep -qF "$MARK_BEGIN" "$f" || return 1
  tmp="$(mktemp)"
  # Drops the block and the blank line add_path_snippet put before it.
  awk -v b="$MARK_BEGIN" -v e="$MARK_END" '
    $0 == b {skip = 1; blank = 0; next}
    $0 == e {skip = 0; next}
    skip {next}
    $0 == "" {if (blank) print ""; blank = 1; next}
    {if (blank) print ""; blank = 0; print}
    END {if (blank) print ""}' "$f" > "$tmp"
  cat "$tmp" > "$f"   # keeps the file's permissions and symlinks intact
  rm -f "$tmp"
}

add_path_snippet() {
  local f="$1" dir_expr="$INSTALL_DIR"
  # Write $HOME instead of the expanded home path, so the file stays portable.
  [[ "$INSTALL_DIR" == "$HOME"/* ]] && dir_expr="\$HOME${INSTALL_DIR#"$HOME"}"
  remove_path_snippet "$f" || true
  mkdir -p "$(dirname "$f")"
  {
    echo ""
    echo "$MARK_BEGIN"
    echo "case \":\$PATH:\" in *\":$dir_expr:\"*) ;; *) export PATH=\"$dir_expr:\$PATH\" ;; esac"
    echo "$MARK_END"
  } >> "$f"
}

if [[ "${1:-}" == "--uninstall" ]]; then
  for f in "${FILES[@]}"; do
    rm -f "$INSTALL_DIR/$f"
  done
  for f in "$HOME/.bashrc" "$HOME/.bash_profile" "${ZDOTDIR:-$HOME}/.zshrc" "$HOME/.zshrc" "$HOME/.profile"; do
    remove_path_snippet "$f" && echo "Removed the PATH entry from $f."
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
  *":$INSTALL_DIR:"*)
    echo "Run: sqid-convert"
    exit 0
    ;;
esac

if [[ "${NO_MODIFY_PATH:-0}" == "1" ]]; then
  echo "Warning: $INSTALL_DIR is not in your PATH (NO_MODIFY_PATH=1, startup files left untouched)." >&2
  echo "Add it yourself:  export PATH=\"$INSTALL_DIR:\$PATH\"" >&2
  exit 0
fi

while IFS= read -r f; do
  add_path_snippet "$f"
  echo "Added $INSTALL_DIR to PATH in $f."
done < <(rc_files)

cat <<EOF

New terminals will find sqid-convert. This terminal was opened before the
change, so reload it once (an installer piped into bash cannot change the PATH
of the shell that launched it):

  exec "\$SHELL"

or, without reloading:  export PATH="$INSTALL_DIR:\$PATH"
EOF
