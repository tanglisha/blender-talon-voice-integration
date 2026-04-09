#!/usr/bin/env bash
# Installation script for Blender Talon Voice Control
# This script copies files to their required locations for production use

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect OS and set paths
OS="$(uname -s)"
case "${OS}" in
    Linux*)
        BLENDER_ADDONS_DIR="$HOME/.config/blender/5.1/scripts/addons"
        ;;
    Darwin*)
        BLENDER_ADDONS_DIR="$HOME/Library/Application Support/Blender/5.1/scripts/addons"
        ;;
    MINGW*|MSYS*|CYGWIN*)
        BLENDER_ADDONS_DIR="$APPDATA/Blender Foundation/Blender/5.1/scripts/addons"
        ;;
    *)
        echo -e "${RED}Unsupported OS: ${OS}${NC}"
        exit 1
        ;;
esac

TALON_USER_DIR="$HOME/.talon/user"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Blender Talon Voice Control - Installation"
echo "==========================================="
echo ""

# Check if Talon directory exists
if [ ! -d "$TALON_USER_DIR" ]; then
    echo -e "${RED}Error: Talon user directory not found at $TALON_USER_DIR${NC}"
    echo "Please install Talon Voice first: https://talonvoice.com"
    exit 1
fi

# Install Talon scripts
echo -e "${YELLOW}Installing Talon scripts...${NC}"
TALON_DEST="$TALON_USER_DIR/blender"

# Create directory if it doesn't exist
mkdir -p "$TALON_DEST"

# Copy Talon files
cp -v "$SCRIPT_DIR/blender_control.py" "$TALON_DEST/"
cp -v "$SCRIPT_DIR/blender.talon" "$TALON_DEST/"
cp -v "$SCRIPT_DIR/test_blender_control.py" "$TALON_DEST/"
cp -v "$SCRIPT_DIR/pyproject.toml" "$TALON_DEST/"
[ -f "$SCRIPT_DIR/uv.lock" ] && cp -v "$SCRIPT_DIR/uv.lock" "$TALON_DEST/"

echo -e "${GREEN}✓ Talon scripts installed to $TALON_DEST${NC}"
echo ""

# Check if blender-addon directory exists in monorepo
if [ -d "$SCRIPT_DIR/../blender-addon" ]; then
    echo -e "${YELLOW}Installing Blender addon...${NC}"

    # Create Blender addons directory if it doesn't exist
    mkdir -p "$BLENDER_ADDONS_DIR"

    ADDON_DEST="$BLENDER_ADDONS_DIR/talon_blender"

    # Copy addon files
    cp -rv "$SCRIPT_DIR/../blender-addon" "$ADDON_DEST"

    echo -e "${GREEN}✓ Blender addon installed to $ADDON_DEST${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Open Blender 5.1"
    echo "2. Go to Edit → Preferences → Add-ons"
    echo "3. Search for 'Talon Voice Control'"
    echo "4. Enable the checkbox"
    echo "5. Check console for 'Talon listener started on port 9876'"
else
    echo -e "${YELLOW}Note: blender-addon directory not found${NC}"
    echo "If you have a separate addon repository, install it manually to:"
    echo "  $BLENDER_ADDONS_DIR/talon_blender"
fi

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "To reload Talon configuration, say 'talon reload' or restart Talon."
