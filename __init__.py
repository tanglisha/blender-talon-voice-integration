import bpy
import socket
import threading
import json
from mathutils import Vector

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
                    break
        else:
            print(f"Unknown action: {action}")

# Global listener instance
listener = None

def register():
    global listener
    if listener is None:
        listener = TalonListener()
        listener.start()

def unregister():
    global listener
    if listener:
        listener.running = False
        listener.sock.close()
        listener = None

if __name__ == "__main__":
    register()
