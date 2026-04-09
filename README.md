# Blender Talon Voice Control

Voice commands to control Blender 5.1 viewport using Talon Voice.

⚠️ **Both components required**: This monorepo contains both the Talon voice commands and the Blender addon needed for operation.

## Quick Start

```bash
git clone https://github.com/tanglisha/blender-talon-voice.git
cd blender-talon-voice/talon
./install.sh
```

Then enable the addon in Blender (Edit → Preferences → Add-ons → search "Talon Voice Control").

## What's Inside

- **`talon/`** - Talon voice command scripts that send commands via UDP
- **`blender-addon/`** - Blender addon that receives commands and controls the viewport

## Installation

### Production Install

```bash
cd talon
./install.sh
```

Copies files to:
- Talon scripts → `~/.talon/user/blender/`
- Blender addon → `~/.config/blender/5.1/scripts/addons/talon_blender/`

### Development Install

```bash
cd talon
./dev-install.sh
```

Creates symlinks so changes in this repo immediately affect Talon and Blender.

## Documentation

- [Talon Scripts Documentation](talon/README.md) - Full voice command list and Talon integration details
- [Blender Addon Documentation](blender-addon/README.md) - Addon implementation and UDP protocol

## Available Voice Commands

With Blender focused:
- **"view pan left/right/up/down"** - Pan viewport
- **"view zoom in/out"** - Zoom viewport
- **"view orbit left/right/up/down"** - Rotate view around center
- **"view front/back/left/right/top/bottom"** - Preset views
- **"view camera"** - Switch to camera view
- **"frame selected"** - Frame selected object
- **"mode object/edit/sculpt"** - Switch modes

Add "slow" or "far" for speed variants, or say a number for precise control.

See [full command list](talon/README.md#available-voice-commands).

## Testing

```bash
# Test Talon integration
cd talon
uv sync --extra dev
.venv/bin/pytest -v

# Test Blender connection
cd blender-addon
./test_connection.py
```

## How It Works

```
Voice → Talon → UDP (port 9876) → Blender Addon → Viewport Action
```

Commands are sent as JSON over UDP to localhost. See the [architecture docs](talon/README.md#architecture) for details.

## License

MIT License - see LICENSE files in subdirectories
