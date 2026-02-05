# Talon Voice Control for Blender

Voice commands to control Blender 5.0 viewport using Talon Voice.

> **📦 Companion Repository**: This works with the [Blender Talon Voice Addon](https://github.com/tanglisha/blender-talon-voice-integration) which runs inside Blender to receive voice commands.

## Prerequisites

1. **Blender 5.0** installed with the Talon Voice Control addon enabled
2. **Talon Voice** installed and running
3. Python 3.x for testing

## Installation

### 1. Install Blender Addon

The Blender addon should already be installed at:
- Linux: `~/.config/blender/5.0/scripts/addons/talon_blender/`
- macOS: `~/Library/Application Support/Blender/5.0/scripts/addons/talon_blender/`
- Windows: `%APPDATA%\Blender Foundation\Blender\5.0\scripts\addons\talon_blender\`

Enable it in Blender:
1. Open Blender
2. Go to Edit → Preferences → Add-ons
3. Search for "Talon Voice Control"
4. Enable the checkbox
5. Check the console for "Talon listener started on port 9876"

### 2. Install Talon Scripts

The Talon scripts should be in `~/.talon/user/blender/`:
- `blender_control.py` - Python module with control actions
- `blender.talon` - Voice command definitions
- `.tests/test_blender_control.py` - Test suite

Talon will automatically load these files when it starts or when you reload the Talon configuration.

## Testing

### Test Blender Connection (without Talon)

From the Blender addon directory:

```bash
cd ~/.config/blender/5.0/scripts/addons/talon_blender
./test_connection.py
```

This tests the UDP connection to Blender directly.

### Test Talon Integration

From the Talon scripts directory:

```bash
pushd ~/.talon/user/blender
.venv/bin/pytest -v
popd
```

Or run directly with pytest after installing dev dependencies:

```bash
pushd ~/.talon/user/blender
uv sync --extra dev
.venv/bin/pytest
popd
```

This tests the Talon command module using pytest (uses test ports, not the production Blender instance).

### Test Voice Commands

1. Make sure Blender is running with the addon enabled
2. Make sure Talon is running
3. In Blender, say one of the voice commands:
   - "view pan left"
   - "view pan right"
   - "view zoom in"
   - "view zoom out"

## Available Voice Commands

### Basic Panning
- **"view pan left"** - Pan viewport left (100 units)
- **"view pan right"** - Pan viewport right (100 units)
- **"view pan up"** - Pan viewport up (100 units)
- **"view pan down"** - Pan viewport down (100 units)

### Fast Panning
- **"view pan left far"** - Pan viewport left quickly (300 units)
- **"view pan right far"** - Pan viewport right quickly (300 units)
- **"view pan up far"** - Pan viewport up quickly (300 units)
- **"view pan down far"** - Pan viewport down quickly (300 units)

### Slow Panning
- **"view pan left slow"** - Pan viewport left slowly (30 units)
- **"view pan right slow"** - Pan viewport right slowly (30 units)
- **"view pan up slow"** - Pan viewport up slowly (30 units)
- **"view pan down slow"** - Pan viewport down slowly (30 units)

### Basic Zooming
- **"view zoom in"** - Zoom in (5 units)
- **"view zoom out"** - Zoom out (5 units)

### Fast Zooming
- **"view zoom in far"** - Zoom in quickly (15 units)
- **"view zoom out far"** - Zoom out quickly (15 units)

### Slow Zooming
- **"view zoom in slow"** - Zoom in slowly (2 units)
- **"view zoom out slow"** - Zoom out slowly (2 units)

## Architecture

### Communication Flow

```
Voice Command → Talon → UDP Socket → Blender Addon → Viewport Action
```

1. **User speaks** a voice command
2. **Talon** matches the command in `blender.talon`
3. **Talon** calls the Python action in `blender_control.py`
4. **Python action** sends JSON command via UDP to localhost:9876
5. **Blender addon** receives command and executes viewport action

### UDP Command Format

Commands are sent as JSON over UDP:

**Pan command:**
```json
{
  "action": "pan",
  "direction": [x, y]
}
```

- **direction**: Array with [x, y] movement values
  - Negative x = left, Positive x = right
  - Negative y = down, Positive y = up

**Zoom command:**
```json
{
  "action": "zoom",
  "amount": 5
}
```

- **amount**: Zoom amount (positive = zoom in, negative = zoom out)

## Troubleshooting

### Voice commands not working

1. **Check Blender addon is enabled:**
   - Look for "Talon listener started on port 9876" in Blender's console
   - If not showing, re-enable the addon in Preferences

2. **Check Talon is running:**
   - Look for Talon in your system tray/menu bar
   - Try saying "help alphabet" - if this works, Talon is listening

3. **Reload Talon configuration:**
   - Say "talon reload" or restart Talon
   - Check the Talon log for any Python errors

4. **Check the UDP connection:**
   - Run the test script: `./test_connection.py`
   - If this works but voice commands don't, the issue is in Talon configuration

5. **Check Blender is in focus:**
   - The `.talon` file is configured for `app: Blender`
   - Voice commands only work when Blender window is active

### Permission errors

If you get permission errors accessing the UDP port:
- Make sure no firewall is blocking localhost:9876
- Try running Blender as your regular user (not root)

## Extending

### Adding New Commands

To add new voice commands:

1. **Add action to Blender addon** (`talon_blender/__init__.py`):
   ```python
   def execute_command(self, cmd):
       action = cmd.get('action')
       if action == 'zoom':
           # Implement zoom logic
           pass
   ```

2. **Add action to Talon module** (`blender_control.py`):
   ```python
   @mod.action_class
   class BlenderActions:
       def blender_zoom(amount: int):
           """Zoom the viewport"""
           send_blender_command('zoom', amount=amount)
   ```

3. **Add voice command** (`blender.talon`):
   ```
   view zoom in: user.blender_zoom(10)
   view zoom out: user.blender_zoom(-10)
   ```

4. **Add tests** (`.tests/test_blender_control.py`):
   ```python
   def test_zoom_command(self):
       send_blender_command('zoom', amount=10)
       # Assert command was sent correctly
   ```

## Security Notes

- Commands are only accepted from localhost (127.0.0.1)
- No authentication is required (assumes single-user desktop environment)
- All commands are validated and sanitized before execution
- JSON parsing errors are caught and logged

## License

This project integrates Talon Voice with Blender for accessibility and productivity purposes.
