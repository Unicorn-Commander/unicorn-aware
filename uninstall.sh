#!/bin/bash

# Unicorn Commander Uninstaller

echo "🦄 Uninstalling Unicorn Commander..."

# Remove desktop files
rm -f "$HOME/.local/share/applications/unicorn_commander.desktop"
rm -f "$HOME/.config/autostart/unicorn_commander.desktop"
rm -f "$HOME/.local/share/icons/unicorn-commander.png"

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$HOME/.local/share/applications"
fi

echo "✓ Unicorn Commander uninstalled"
echo "Note: Python packages and project files remain for manual removal"