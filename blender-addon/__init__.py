import bpy
import socket
import threading
import json
from mathutils import Vector


def notify_status_panel(action, details=""):
    """
    Notify the status panel addon about a command (if it's installed).

    Args:
        action: Action name (e.g., 'pan', 'zoom', 'orbit')
        details: Additional details about the action
    """
    try:
        # Check if the status panel addon is installed and enabled
        if "blender_status_panel" in bpy.context.preferences.addons:
            # Import the operator_tracker from the status panel addon
            import sys
            if 'blender_status_panel.operator_tracker' in sys.modules:
                tracker = sys.modules['blender_status_panel.operator_tracker']

                # Format a human-readable name
                action_name = action.replace('_', ' ').title()
                if details:
                    full_name = f"{action_name}: {details}"
                else:
                    full_name = action_name

                # Add to the operation history
                tracker.add_external_operation(full_name, source="talon")
    except Exception as e:
        # Silently fail if status panel isn't available
        pass


bl_info = {
    "name": "Talon Voice Control",
    "author": "Liz Dahlstrom",
    "version": (1, 0, 1),
    "blender": (5, 0, 0),
    "location": "View3D",
    "description": "Control Blender with Talon voice commands",
    "category": "3D View",
}

class TalonListener(threading.Thread):
    """Background thread that listens for commands from Talon"""
    
    def __init__(self):
        super().__init__(daemon=True)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(1.0)  # Allow periodic checks of running flag
        self.sock.bind(('localhost', 9876))
        self.running = True
        print("Talon listener started on port 9876")
        
    def run(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(1024)
                cmd = json.loads(data.decode())
                # Schedule command execution on main thread
                bpy.app.timers.register(lambda c=cmd: self.execute_command(c))
            except socket.timeout:
                # Normal timeout, just check if we should keep running
                continue
            except Exception as e:
                print(f"Talon listener error: {e}")
    
    def execute_command(self, cmd):
        """Execute a command from Talon (runs on main thread)"""
        action = cmd.get('action')
        
        if action == 'pan':
            direction = cmd.get('direction', [0, 0])
            
            # Find the 3D viewport
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    # Get the 3D view space
                    space = area.spaces.active
                    rv3d = space.region_3d
                    
                    # Pan by adjusting view_location
                    # Scale the movement based on view distance
                    scale = rv3d.view_distance * 0.001
                    
                    # Get view matrix to transform pan direction
                    view_mat = rv3d.view_matrix.inverted()
                    
                    # Create movement vector (x right, y up in screen space)
                    offset = Vector((direction[0] * scale, direction[1] * scale, 0))
                    
                    # Transform to world space and apply
                    world_offset = view_mat @ offset - view_mat.translation
                    rv3d.view_location -= world_offset
                    
                    # Force view update
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            region.tag_redraw()

                    print(f"Executed pan: {direction}")

                    # Update status panel
                    notify_status_panel('pan', f"[{direction[0]}, {direction[1]}]")
                    break

        elif action == 'zoom':
            amount = cmd.get('amount', 0)

            # Find the 3D viewport
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    # Get the 3D view space
                    space = area.spaces.active
                    rv3d = space.region_3d

                    # Zoom by adjusting view_distance
                    # Positive amount = zoom in (decrease distance)
                    # Negative amount = zoom out (increase distance)
                    # Scale the zoom based on current distance for smooth operation
                    zoom_factor = amount * rv3d.view_distance * 0.01
                    new_distance = rv3d.view_distance - zoom_factor

                    # Clamp to reasonable values (prevent getting too close or too far)
                    min_distance = 0.1
                    max_distance = 10000.0
                    rv3d.view_distance = max(min_distance, min(max_distance, new_distance))

                    # Force view update
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            region.tag_redraw()

                    print(f"Executed zoom: {amount} (new distance: {rv3d.view_distance:.2f})")

                    # Update status panel
                    zoom_dir = "in" if amount > 0 else "out"
                    notify_status_panel('zoom', f"{zoom_dir} ({abs(amount)})")
                    break

        elif action == 'orbit':
            direction = cmd.get('direction', [0, 0])

            # Find the 3D viewport
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    # Get the 3D view space
                    space = area.spaces.active
                    rv3d = space.region_3d

                    # Convert direction to radians (scale factor for smooth rotation)
                    # Horizontal rotation (around Z axis in world space)
                    angle_x = direction[0] * 0.01  # Scale down for smoother control
                    # Vertical rotation (around view's X axis)
                    angle_y = direction[1] * 0.01

                    # Get current view rotation
                    current_rotation = rv3d.view_rotation.copy()

                    # Create rotation quaternions
                    import mathutils

                    # Horizontal rotation (left/right) - rotate around world Z axis
                    rot_horizontal = mathutils.Quaternion((0, 0, 1), angle_x)

                    # Vertical rotation (up/down) - rotate around view's local X axis
                    # Get the view's right vector (local X axis)
                    view_matrix = rv3d.view_matrix.inverted()
                    right_vector = view_matrix.col[0][:3]  # X axis of view
                    rot_vertical = mathutils.Quaternion(right_vector, angle_y)

                    # Apply rotations: first horizontal, then vertical
                    new_rotation = rot_horizontal @ current_rotation @ rot_vertical
                    new_rotation.normalize()

                    rv3d.view_rotation = new_rotation

                    # Force view update
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            region.tag_redraw()

                    print(f"Executed orbit: {direction}")

                    # Update status panel
                    notify_status_panel('orbit', f"[{direction[0]}, {direction[1]}]")
                    break

        elif action == 'frame_selected':
            # Frame the selected object(s) in the viewport
            # Find the 3D viewport and set up context override
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    # Find the 3D view region
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            # Create context override
                            override = {
                                'area': area,
                                'region': region,
                            }

                            try:
                                # Call the operator with the overridden context
                                with bpy.context.temp_override(**override):
                                    bpy.ops.view3d.view_selected()
                                print("Executed frame_selected")

                                # Update status panel
                                notify_status_panel('frame_selected', '')
                            except Exception as e:
                                print(f"Error executing frame_selected: {e}")
                            break
                    break

        elif action == 'view_preset':
            view_type = cmd.get('view', 'front')

            # Find the 3D viewport
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    space = area.spaces.active
                    rv3d = space.region_3d

                    import mathutils
                    import math

                    # Define quaternions for each standard view
                    # These match Blender's numpad view shortcuts
                    view_rotations = {
                        'front': mathutils.Quaternion((0.7071, 0.7071, 0.0, 0.0)),  # numpad 1
                        'back': mathutils.Quaternion((0.0, 0.0, 0.7071, 0.7071)),    # ctrl+numpad 1
                        'right': mathutils.Quaternion((0.5, 0.5, 0.5, 0.5)),        # numpad 3
                        'left': mathutils.Quaternion((-0.5, -0.5, -0.5, 0.5)),      # ctrl+numpad 3
                        'top': mathutils.Quaternion((1.0, 0.0, 0.0, 0.0)),          # numpad 7
                        'bottom': mathutils.Quaternion((0.0, 1.0, 0.0, 0.0)),       # ctrl+numpad 7
                    }

                    if view_type == 'camera':
                        # Switch to camera view
                        rv3d.view_perspective = 'CAMERA'
                        print("Executed view_preset: camera")
                        notify_status_panel('view_preset', view_type)
                    elif view_type in view_rotations:
                        # Set to orthographic preset view
                        rv3d.view_perspective = 'ORTHO'
                        rv3d.view_rotation = view_rotations[view_type]
                        print(f"Executed view_preset: {view_type}")
                        notify_status_panel('view_preset', view_type)
                    else:
                        print(f"Unknown view type: {view_type}")

                    # Force view update
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            region.tag_redraw()
                    break

        elif action == 'mode_set':
            mode = cmd.get('mode', 'OBJECT')

            # Find the 3D viewport and set up context override
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    # Find the window region
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            # Create context override
                            override = {
                                'area': area,
                                'region': region,
                            }

                            try:
                                # Call the mode_set operator with context override
                                with bpy.context.temp_override(**override):
                                    bpy.ops.object.mode_set(mode=mode)
                                print(f"Executed mode_set: {mode}")

                                # Update status panel
                                notify_status_panel('mode_set', mode)
                            except Exception as e:
                                print(f"Error setting mode to {mode}: {e}")
                            break
                    break

        else:
            print(f"Unknown action: {action}")

# Global listener instance
listener = None

def register():
    global listener

    # Start the UDP listener
    if listener is None:
        listener = TalonListener()
        listener.start()

def unregister():
    global listener

    # Stop the UDP listener
    if listener:
        listener.running = False
        listener.sock.close()
        listener = None

if __name__ == "__main__":
    register()
