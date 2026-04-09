#!/usr/bin/env bash
# Development installation script for Blender Talon Voice Control
# This script creates symlinks so changes in the repo immediately affect the running system

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
        echo -e "${RED}Error: Symlinks may not work reliably on Windows${NC}"
        echo "Please use install.sh instead, or manually create junction points"
        exit 1
        ;;
    *)
        echo -e "${RED}Unsupported OS: ${OS}${NC}"
        exit 1
        ;;
esac

TALON_USER_DIR="$HOME/.talon/user"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Blender Talon Voice Control - Development Installation"
echo "======================================================="
echo ""
echo -e "${YELLOW}This will create symlinks for development.${NC}"
echo -e "${YELLOW}Changes to files in this repo will immediately affect Talon and Blender.${NC}"
echo ""

# Check if Talon directory exists
if [ ! -d "$TALON_USER_DIR" ]; then
    echo -e "${RED}Error: Talon user directory not found at $TALON_USER_DIR${NC}"
    echo "Please install Talon Voice first: https://talonvoice.com"
    exit 1
fi

# Install Talon scripts
echo -e "${YELLOW}Setting up Talon scripts symlink...${NC}"
TALON_DEST="$TALON_USER_DIR/blender"

# Remove existing directory/symlink if it exists
if [ -e "$TALON_DEST" ] || [ -L "$TALON_DEST" ]; then
    echo "Removing existing installation at $TALON_DEST"
    rm -rf "$TALON_DEST"
fi

# Create symlink to the talon directory
ln -s "$SCRIPT_DIR" "$TALON_DEST"

echo -e "${GREEN}✓ Talon scripts symlinked: $TALON_DEST → $SCRIPT_DIR${NC}"
echo ""

# Check if blender-addon directory exists in monorepo
if [ -d "$SCRIPT_DIR/../blender-addon" ]; then
    echo -e "${YELLOW}Setting up Blender addon symlink...${NC}"

    # Create Blender addons directory if it doesn't exist
    mkdir -p "$BLENDER_ADDONS_DIR"

    ADDON_DEST="$BLENDER_ADDONS_DIR/talon_blender"

    # Remove existing directory/symlink if it exists
    if [ -e "$ADDON_DEST" ] || [ -L "$ADDON_DEST" ]; then
        echo "Removing existing addon at $ADDON_DEST"
        rm -rf "$ADDON_DEST"
    fi

    # Create symlink to the addon directory
    ln -s "$SCRIPT_DIR/../blender-addon" "$ADDON_DEST"

    echo -e "${GREEN}✓ Blender addon symlinked: $ADDON_DEST → $SCRIPT_DIR/../blender-addon${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Open Blender 5.1"
    echo "2. Go to Edit → Preferences → Add-ons"
    echo "3. Search for 'Talon Voice Control'"
    echo "4. Enable the checkbox"
    echo "5. Check console for 'Talon listener started on port 9876'"
else
    echo -e "${YELLOW}Note: blender-addon directory not found${NC}"
    echo "If you have a separate addon repository, symlink it manually:"
    echo "  ln -s /path/to/blender-addon $BLENDER_ADDONS_DIR/talon_blender"
fi

echo ""
echo -e "${GREEN}Development installation complete!${NC}"
echo ""
echo -e "${YELLOW}Development workflow:${NC}"
echo "• Edit files in: $SCRIPT_DIR"
echo "• Changes immediately affect Talon (say 'talon reload' to reload)"
echo "• For Blender addon changes, restart Blender or disable/enable the addon"
echo ""
echo "To reload Talon configuration, say 'talon reload' or restart Talon."
