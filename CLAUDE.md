# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Talon Voice Control integration for Blender 5.1. It enables hands-free viewport control using voice commands through a UDP-based communication protocol.

**Architecture**: Voice commands in Talon → Python actions → UDP socket (port 9876) → Blender addon → Viewport actions

**Key files**:
- `blender_control.py`: Talon module with action definitions and UDP communication
- `blender.talon`: Voice command mappings (only active when Blender is focused)
- `test_blender_control.py`: Test suite with mock UDP server
- Companion: [Blender addon](https://github.com/tanglisha/blender-talon-voice-integration) runs inside Blender

## Development Commands

### Testing
```bash
# Run all tests
uv sync --extra dev
.venv/bin/pytest -v

# Run specific test file
.venv/bin/pytest test_blender_control.py -v

# Run specific test
.venv/bin/pytest test_blender_control.py::test_send_command_success -v
```

### Package Management
This project uses `uv` for dependency management (defined in `pyproject.toml`).

## Code Architecture

### UDP Command Protocol
Commands are sent as JSON over UDP to localhost:9876. All commands have an `action` field plus additional parameters:

```python
# Pan command
{"action": "pan", "direction": [x, y]}  # negative x=left, positive x=right, negative y=down, positive y=up

# Zoom command
{"action": "zoom", "amount": 5}  # positive=in, negative=out

# Orbit command
{"action": "orbit", "direction": [x, y]}

# View preset command
{"action": "view_preset", "view": "front"}  # front|back|right|left|top|bottom|camera

# Mode switching command
{"action": "mode_set", "mode": "EDIT"}  # OBJECT|EDIT|SCULPT|VERTEX_PAINT|WEIGHT_PAINT|TEXTURE_PAINT|POSE
```

### Talon Action Pattern
Actions are defined in `blender_control.py` using the `@mod.action_class` decorator. The `send_blender_command()` function handles all UDP communication with error handling and timeout (0.5s).

Voice commands in `blender.talon` map to these actions and are only active when Blender window is focused (`app.name: Blender`).

### Testing Strategy
Tests use a `MockBlenderServer` that listens on alternate ports (9999, 9998) to avoid conflicts with production Blender. The test suite mocks the Talon module since tests run outside of Talon's environment.

## Adding New Commands

1. **Define action in `blender_control.py`**:
```python
@mod.action_class
class BlenderActions:
    def blender_new_action(param: int):
        """Description"""
        send_blender_command('new_action', param=param)
```

2. **Add voice command in `blender.talon`**:
```
new command: user.blender_new_action(100)
```

3. **Add test in `test_blender_control.py`**:
```python
def test_new_action_command(mock_server, blender_control_module):
    blender_control_module.BLENDER_PORT = 9999
    from blender_control import send_blender_command
    result = send_blender_command('new_action', param=100)
    assert result is True
    time.sleep(0.2)
    assert mock_server.received_commands[0]['action'] == 'new_action'
```

4. **Implement handler in Blender addon** (separate repository)

## Important Notes

- Commands are fire-and-forget (no acknowledgment from Blender)
- Only localhost connections accepted for security
- Talon tag `user.blender_running` indicates Blender context is active
- Commands support variable amounts via `<number_small>` capture in voice grammar
- Test server uses ports 9999/9998 to avoid conflicts with production port 9876
