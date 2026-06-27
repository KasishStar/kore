#!/usr/bin/env bash
# Kore installer — makes `kore` available anywhere in the terminal
set -e

KORE_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="${HOME}/.local/bin"

mkdir -p "${BIN_DIR}"

# Symlink the wrapper script
ln -sf "${KORE_DIR}/kore" "${BIN_DIR}/kore"
chmod +x "${KORE_DIR}/kore"

# Ensure ~/.local/bin is in PATH
case ":${PATH}:" in
    *:"${BIN_DIR}":*) ;;
    *)
        SHELL_CONFIG="${HOME}/.bashrc"
        if [ -f "${HOME}/.zshrc" ]; then
            SHELL_CONFIG="${HOME}/.zshrc"
        fi
        echo "" >> "${SHELL_CONFIG}"
        echo "# Kore" >> "${SHELL_CONFIG}"
        echo "export PATH=\"\${PATH}:${BIN_DIR}\"" >> "${SHELL_CONFIG}"
        echo "Added ${BIN_DIR} to PATH in ${SHELL_CONFIG}"
        echo "Restart your terminal or run: source ${SHELL_CONFIG}"
        ;;
esac

# Install dependency
pip install requests -q 2>/dev/null || true

echo ""
echo "  Kore installed. Type 'kore' to start."
echo "  Path: ${KORE_DIR}"
echo "  Bin:  ${BIN_DIR}/kore"
