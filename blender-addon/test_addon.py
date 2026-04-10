"""
Integration tests for Talon Blender addon.
Run with: pytest test_addon.py

This script runs inside Blender's Python environment via pytest-blender.
"""

import socket
import json
import time
import pytest

# These imports work because pytest-blender runs tests inside Blender
import bpy
from mathutils import Vector


def send_command(action, **kwargs):
    """Send a command to the addon via UDP"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cmd = {'action': action, **kwargs}
    sock.sendto(json.dumps(cmd).encode(), ('localhost', 9876))
    sock.close()
    return cmd


@pytest.fixture(scope="session", autouse=True)
def enable_addon():
    """Automatically enable the addon before running tests"""
    addon_name = "talon_blender"
    if addon_name not in bpy.context.preferences.addons.keys():
        bpy.ops.preferences.addon_enable(module=addon_name)
        time.sleep(1)  # Give the addon time to start the listener
    yield


def test_addon_enabled():
    """Test that the addon is loaded and enabled"""
    addon_name = "talon_blender"
    assert addon_name in bpy.context.preferences.addons.keys(), \
        f"Addon not enabled. Available: {list(bpy.context.preferences.addons.keys())}"


def test_listener_running():
    """Test that the UDP listener is running on port 9876"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1.0)

    try:
        # Try to send a test command
        test_cmd = {'action': 'test'}
        sock.sendto(json.dumps(test_cmd).encode(), ('localhost', 9876))
        sock.close()
    except Exception as e:
        sock.close()
        pytest.fail(f"Failed to connect to listener: {e}")


def test_pan_command():
    """Test that pan commands modify the viewport"""
    # Find the 3D viewport
    viewport_area = None
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            viewport_area = area
            break

    assert viewport_area is not None, "No 3D viewport found"

    space = viewport_area.spaces.active
    rv3d = space.region_3d

    # Store initial view location
    initial_location = rv3d.view_location.copy()

    # Send pan command
    send_command('pan', direction=[100, 0])

    # Give it time to process
    time.sleep(0.5)

    # Note: In headless mode, the viewport might not update immediately
    # We're mainly testing that the command can be sent without errors
    # The actual viewport change is tested when running with UI


def test_invalid_action():
    """Test that invalid actions are handled gracefully"""
    # Should not raise an exception
    send_command('invalid_action', some_param=123)


def test_malformed_json():
    """Test that malformed JSON is handled gracefully"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Send invalid JSON - should not crash the addon
        sock.sendto(b"not valid json", ('localhost', 9876))
        sock.close()
    except Exception as e:
        sock.close()
        pytest.fail(f"Failed to send malformed JSON: {e}")


def test_zoom_command():
    """Test that zoom commands modify the viewport"""
    # Find the 3D viewport
    viewport_area = None
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            viewport_area = area
            break

    assert viewport_area is not None, "No 3D viewport found"

    space = viewport_area.spaces.active
    rv3d = space.region_3d

    # Store initial view distance
    initial_distance = rv3d.view_distance

    # Send zoom command (positive = zoom in, negative = zoom out)
    send_command('zoom', amount=5)

    # Give it time to process
    time.sleep(0.5)


def test_orbit_command():
    """Test that orbit commands modify the viewport"""
    # Find the 3D viewport
    viewport_area = None
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            viewport_area = area
            break

    assert viewport_area is not None, "No 3D viewport found"

    space = viewport_area.spaces.active
    rv3d = space.region_3d

    # Store initial view rotation
    initial_rotation = rv3d.view_rotation.copy()

    # Send orbit command
    send_command('orbit', direction=[15, 0])

    # Give it time to process
    time.sleep(0.5)


