# Talon-Blender Voice Control

Control Blender's viewport with Talon voice commands via UDP socket communication.

> **📦 Companion Repository**: This works with the [Talon Voice Commands for Blender](https://github.com/YOUR_USERNAME/talon-blender-commands) which provides the voice command definitions.

## Installation

### 1. Install Blender Addon

1. Copy the `talon_blender` folder to your Blender addons directory:
   - Linux: `~/.config/blender/5.0/scripts/addons/`
   - macOS: `~/Library/Application Support/Blender/5.0/scripts/addons/`
   - Windows: `%APPDATA%\Blender Foundation\Blender\5.0\scripts\addons\`

2. Open Blender
3. Go to Edit → Preferences → Add-ons
4. Search for "Talon Voice Control"
5. Enable the checkbox next to it
6. Check the terminal/console for "Talon listener started on port 9876"

### 2. Test the Connection

Before setting up Talon, verify the Blender addon is working:

```bash
python test_connection.py
```

You should see the 3D viewport camera pan in different directions.

### 3. Run Integration Tests

Run automated integration tests inside Blender:

```bash
./run_tests.sh
```

Or run directly with Blender:

```bash
blender --background --python test_addon.py
```

The integration tests verify:
- Addon is loaded and enabled
- UDP listener is running on port 9876
- Pan commands modify the viewport
- Zoom commands modify the viewport
- Invalid actions are handled gracefully
- Malformed JSON is handled safely

## Current Commands

- **Pan view**: The addon listens for pan commands with x/y direction values
- **Zoom view**: The addon listens for zoom commands with amount values (positive = zoom in, negative = zoom out)

## Architecture

- **Blender addon**: Runs a UDP server on port 9876, listens for JSON commands
- **Talon scripts**: Send JSON commands via UDP socket
- **No external dependencies**: Uses only Python stdlib

## Talon Voice Integration

The Talon voice command scripts are located in `~/.talon/user/blender/`:

- `blender_control.py` - Python module that sends commands to Blender
- `blender.talon` - Voice command definitions
- `test_blender_control.py` - Test suite for Talon integration
- `README.md` - Detailed documentation for using voice commands

### Quick Start with Voice Commands

1. Make sure Blender is running with this addon enabled
2. Make sure Talon Voice is running
3. Focus on Blender window
4. Say: "view pan left" (or right, up, down)

See `~/.talon/user/blender/README.md` for complete documentation on:
- All available voice commands
- Testing the integration
- Troubleshooting
- Adding new commands

## Next Steps

Potential features to add:
- Zoom controls
- Rotation controls
- Object selection by voice
- Mode switching (Edit, Object, Sculpt)
- Tool selection
- Custom view angles
