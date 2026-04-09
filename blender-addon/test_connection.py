#!/usr/bin/env python3
"""
Test script to verify Talon-Blender communication works.
Run this while Blender is open with the addon enabled.
"""

import socket
import json
import time

def send_command(action, **kwargs):
    """Send a command to Blender via UDP"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cmd = {'action': action, **kwargs}
    sock.sendto(json.dumps(cmd).encode(), ('localhost', 9876))
    sock.close()
    print(f"Sent: {cmd}")

if __name__ == "__main__":
    print("Testing Blender addon...")
    print("Make sure Blender is running with the Talon Voice Control addon enabled!")
    print()
    
    time.sleep(1)
    
    print("Panning left...")
    send_command('pan', direction=[-100, 0])
    time.sleep(1)
    
    print("Panning right...")
    send_command('pan', direction=[100, 0])
    time.sleep(1)
    
    print("Panning up...")
    send_command('pan', direction=[0, 100])
    time.sleep(1)
    
    print("Panning down...")
    send_command('pan', direction=[0, -100])
    
    print("\nDone! Check Blender - did the view move?")
