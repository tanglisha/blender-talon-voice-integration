"""
Talon Python module for controlling Blender via UDP socket.
This module provides actions that can be called from .talon files.
"""

import socket
import json
from talon import Module, actions

# Configuration
BLENDER_HOST = 'localhost'
BLENDER_PORT = 9876

# Create Talon module
mod = Module()
mod.tag("blender_running", desc="Tag to indicate Blender is running")


def send_blender_command(action: str, **kwargs) -> bool:
    """
    Send a command to Blender via UDP socket.

    Args:
        action: The action to perform (e.g., 'pan', 'zoom', 'rotate')
        **kwargs: Additional parameters for the action

    Returns:
        True if command was sent successfully, False otherwise
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.5)

        cmd = {'action': action, **kwargs}
        message = json.dumps(cmd).encode()

        sock.sendto(message, (BLENDER_HOST, BLENDER_PORT))
        sock.close()

        return True
    except Exception as e:
        print(f"Error sending command to Blender: {e}")
        return False


@mod.action_class
class BlenderActions:
    """Actions for controlling Blender"""

    def blender_pan(direction_x: int, direction_y: int):
        """Pan the 3D viewport in the specified direction"""
        send_blender_command('pan', direction=[direction_x, direction_y])

    def blender_pan_left(amount: int = 100):
        """Pan the viewport left"""
        send_blender_command('pan', direction=[-amount, 0])

    def blender_pan_right(amount: int = 100):
        """Pan the viewport right"""
        send_blender_command('pan', direction=[amount, 0])

    def blender_pan_up(amount: int = 100):
        """Pan the viewport up"""
        send_blender_command('pan', direction=[0, amount])

    def blender_pan_down(amount: int = 100):
        """Pan the viewport down"""
        send_blender_command('pan', direction=[0, -amount])

    def blender_zoom(amount: int):
        """Zoom the 3D viewport (positive = in, negative = out)"""
        send_blender_command('zoom', amount=amount)

    def blender_zoom_in(amount: int = 5):
        """Zoom in on the viewport"""
        send_blender_command('zoom', amount=amount)

    def blender_zoom_out(amount: int = 5):
        """Zoom out from the viewport"""
        send_blender_command('zoom', amount=-amount)

    def blender_orbit(direction_x: int, direction_y: int):
        """Orbit the 3D viewport in the specified direction"""
        send_blender_command('orbit', direction=[direction_x, direction_y])

    def blender_orbit_left(amount: int = 15):
        """Orbit the viewport left"""
        send_blender_command('orbit', direction=[-amount, 0])

    def blender_orbit_right(amount: int = 15):
        """Orbit the viewport right"""
        send_blender_command('orbit', direction=[amount, 0])

    def blender_orbit_up(amount: int = 15):
        """Orbit the viewport up"""
        send_blender_command('orbit', direction=[0, amount])

    def blender_orbit_down(amount: int = 15):
        """Orbit the viewport down"""
        send_blender_command('orbit', direction=[0, -amount])

    def blender_frame_selected():
        """Frame the selected object in the viewport"""
        send_blender_command('frame_selected')

    def blender_view_front():
        """Switch to front view"""
        send_blender_command('view_preset', view='front')

    def blender_view_back():
        """Switch to back view"""
        send_blender_command('view_preset', view='back')

    def blender_view_right():
        """Switch to right side view"""
        send_blender_command('view_preset', view='right')

    def blender_view_left():
        """Switch to left side view"""
        send_blender_command('view_preset', view='left')

    def blender_view_top():
        """Switch to top view"""
        send_blender_command('view_preset', view='top')

    def blender_view_bottom():
        """Switch to bottom view"""
        send_blender_command('view_preset', view='bottom')

    def blender_view_camera():
        """Switch to camera view"""
        send_blender_command('view_preset', view='camera')

    def blender_mode_object():
        """Switch to Object mode"""
        send_blender_command('mode_set', mode='OBJECT')

    def blender_mode_edit():
        """Switch to Edit mode"""
        send_blender_command('mode_set', mode='EDIT')

    def blender_mode_sculpt():
        """Switch to Sculpt mode"""
        send_blender_command('mode_set', mode='SCULPT')

    def blender_mode_vertex_paint():
        """Switch to Vertex Paint mode"""
        send_blender_command('mode_set', mode='VERTEX_PAINT')

    def blender_mode_weight_paint():
        """Switch to Weight Paint mode"""
        send_blender_command('mode_set', mode='WEIGHT_PAINT')

    def blender_mode_texture_paint():
        """Switch to Texture Paint mode"""
        send_blender_command('mode_set', mode='TEXTURE_PAINT')

    def blender_mode_pose():
        """Switch to Pose mode (for armatures)"""
        send_blender_command('mode_set', mode='POSE')
