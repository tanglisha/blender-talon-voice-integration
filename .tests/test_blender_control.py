#!/usr/bin/env python3
"""
Tests for the blender_control module.
Tests the UDP communication without requiring Talon to be running.
"""

import socket
import json
import threading
import time
import sys
import os
from unittest.mock import MagicMock
import pytest


class MockBlenderServer:
    """Mock Blender UDP server for testing"""

    def __init__(self, host='localhost', port=9999):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(1.0)
        self.sock.bind((host, port))
        self.running = False
        self.received_commands = []
        self.thread = None

    def start(self):
        """Start the mock server in a background thread"""
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        time.sleep(0.1)  # Give server time to start

    def stop(self):
        """Stop the mock server"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        self.sock.close()

    def _run(self):
        """Run the server loop"""
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                cmd = json.loads(data.decode())
                self.received_commands.append(cmd)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Mock server error: {e}")
                break


@pytest.fixture
def mock_server():
    """Fixture that provides a mock Blender server"""
    server = MockBlenderServer()
    server.start()
    yield server
    server.stop()


@pytest.fixture
def mock_server_alt():
    """Fixture for alternative port mock server"""
    server = MockBlenderServer(port=9998)
    server.start()
    yield server
    server.stop()


@pytest.fixture
def blender_control_module():
    """Fixture that mocks talon and imports blender_control"""
    # Add parent directory to path (since we're now in tests/)
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    # Mock the talon module
    sys.modules['talon'] = MagicMock()

    # Import blender_control
    import blender_control
    original_port = blender_control.BLENDER_PORT

    yield blender_control

    # Restore original port
    blender_control.BLENDER_PORT = original_port


def test_send_command_success(mock_server, blender_control_module):
    """Test sending a command successfully"""
    blender_control_module.BLENDER_PORT = 9999

    from blender_control import send_blender_command

    result = send_blender_command('pan', direction=[100, 0])

    assert result is True
    time.sleep(0.2)  # Wait for server to receive
    assert len(mock_server.received_commands) == 1
    assert mock_server.received_commands[0]['action'] == 'pan'
    assert mock_server.received_commands[0]['direction'] == [100, 0]


def test_send_command_with_multiple_parameters(mock_server, blender_control_module):
    """Test sending a command with multiple parameters"""
    blender_control_module.BLENDER_PORT = 9999

    from blender_control import send_blender_command

    result = send_blender_command('test', param1='value1', param2=42, param3=[1, 2, 3])

    assert result is True
    time.sleep(0.2)
    assert len(mock_server.received_commands) == 1
    cmd = mock_server.received_commands[0]
    assert cmd['action'] == 'test'
    assert cmd['param1'] == 'value1'
    assert cmd['param2'] == 42
    assert cmd['param3'] == [1, 2, 3]


def test_send_command_server_unreachable(mock_server, blender_control_module):
    """Test handling when Blender is not running"""
    blender_control_module.BLENDER_PORT = 9999

    from blender_control import send_blender_command

    # Stop the server to simulate Blender not running
    mock_server.stop()

    result = send_blender_command('pan', direction=[100, 0])

    # Should return True even if server is down (fire and forget)
    # The function doesn't wait for acknowledgment
    assert result is True


@pytest.mark.parametrize('direction,description', [
    ([-100, 0], 'left'),
    ([100, 0], 'right'),
    ([0, 100], 'up'),
    ([0, -100], 'down'),
])
def test_pan_commands_format(mock_server, blender_control_module, direction, description):
    """Test that pan commands are formatted correctly"""
    blender_control_module.BLENDER_PORT = 9999

    from blender_control import send_blender_command

    mock_server.received_commands.clear()
    send_blender_command('pan', direction=direction)
    time.sleep(0.1)

    assert len(mock_server.received_commands) == 1, f"Failed for {description}"
    cmd = mock_server.received_commands[0]
    assert cmd['action'] == 'pan'
    assert cmd['direction'] == direction


def test_json_serialization(mock_server, blender_control_module):
    """Test that commands are properly JSON serialized"""
    blender_control_module.BLENDER_PORT = 9999

    from blender_control import send_blender_command

    # Test with various data types
    send_blender_command('test',
                       string_param='hello',
                       int_param=42,
                       float_param=3.14,
                       bool_param=True,
                       list_param=[1, 2, 3],
                       dict_param={'key': 'value'})

    time.sleep(0.2)
    assert len(mock_server.received_commands) == 1
    cmd = mock_server.received_commands[0]

    # Verify all parameters were preserved
    assert cmd['string_param'] == 'hello'
    assert cmd['int_param'] == 42
    assert abs(cmd['float_param'] - 3.14) < 0.001
    assert cmd['bool_param'] is True
    assert cmd['list_param'] == [1, 2, 3]
    assert cmd['dict_param'] == {'key': 'value'}


@pytest.mark.parametrize('test_str', [
    'test"quote',
    "test'apostrophe",
    'test\\backslash',
    'test\nnewline',
    'test\ttab',
])
def test_invalid_json_characters(mock_server_alt, test_str):
    """Test handling of characters that could break JSON"""
    # Mock the talon module
    sys.modules['talon'] = MagicMock()

    # Mock the BLENDER_PORT to use our test port
    import blender_control
    original_port = blender_control.BLENDER_PORT
    blender_control.BLENDER_PORT = 9998

    from blender_control import send_blender_command

    try:
        mock_server_alt.received_commands.clear()
        send_blender_command('test', param=test_str)
        time.sleep(0.1)

        assert len(mock_server_alt.received_commands) == 1
        assert mock_server_alt.received_commands[0]['param'] == test_str
    finally:
        # Restore original port
        blender_control.BLENDER_PORT = original_port


@pytest.mark.parametrize('amount,description', [
    (1, 'zoom in small'),
    (10, 'zoom in medium'),
    (-1, 'zoom out small'),
    (-10, 'zoom out medium'),
])
def test_zoom_commands_format(mock_server, blender_control_module, amount, description):
    """Test that zoom commands are formatted correctly"""
    blender_control_module.BLENDER_PORT = 9999

    from blender_control import send_blender_command

    mock_server.received_commands.clear()
    send_blender_command('zoom', amount=amount)
    time.sleep(0.1)

    assert len(mock_server.received_commands) == 1, f"Failed for {description}"
    cmd = mock_server.received_commands[0]
    assert cmd['action'] == 'zoom'
    assert cmd['amount'] == amount


def test_zoom_command_success(mock_server, blender_control_module):
    """Test sending a zoom command successfully"""
    blender_control_module.BLENDER_PORT = 9999

    from blender_control import send_blender_command

    result = send_blender_command('zoom', amount=5)

    assert result is True
    time.sleep(0.2)
    assert len(mock_server.received_commands) == 1
    assert mock_server.received_commands[0]['action'] == 'zoom'
    assert mock_server.received_commands[0]['amount'] == 5


@pytest.mark.parametrize('direction,description', [
    ([-15, 0], 'orbit left'),
    ([15, 0], 'orbit right'),
    ([0, 15], 'orbit up'),
    ([0, -15], 'orbit down'),
])
def test_orbit_commands_format(mock_server, blender_control_module, direction, description):
    """Test that orbit commands are formatted correctly"""
    blender_control_module.BLENDER_PORT = 9999

    from blender_control import send_blender_command

    mock_server.received_commands.clear()
    send_blender_command('orbit', direction=direction)
    time.sleep(0.1)

    assert len(mock_server.received_commands) == 1, f"Failed for {description}"
    cmd = mock_server.received_commands[0]
    assert cmd['action'] == 'orbit'
    assert cmd['direction'] == direction


def test_orbit_command_success(mock_server, blender_control_module):
    """Test sending an orbit command successfully"""
    blender_control_module.BLENDER_PORT = 9999

    from blender_control import send_blender_command

    result = send_blender_command('orbit', direction=[15, 10])

    assert result is True
    time.sleep(0.2)
    assert len(mock_server.received_commands) == 1
    assert mock_server.received_commands[0]['action'] == 'orbit'
    assert mock_server.received_commands[0]['direction'] == [15, 10]


def test_frame_selected_command(mock_server, blender_control_module):
    """Test sending a frame selected command"""
    blender_control_module.BLENDER_PORT = 9999

    from blender_control import send_blender_command

    result = send_blender_command('frame_selected')

    assert result is True
    time.sleep(0.2)
    assert len(mock_server.received_commands) == 1
    assert mock_server.received_commands[0]['action'] == 'frame_selected'


@pytest.mark.parametrize('view_type', [
    'front', 'back', 'right', 'left', 'top', 'bottom', 'camera'
])
def test_view_preset_commands(mock_server, blender_control_module, view_type):
    """Test that view preset commands are formatted correctly"""
    blender_control_module.BLENDER_PORT = 9999

    from blender_control import send_blender_command

    mock_server.received_commands.clear()
    send_blender_command('view_preset', view=view_type)
    time.sleep(0.1)

    assert len(mock_server.received_commands) == 1
    cmd = mock_server.received_commands[0]
    assert cmd['action'] == 'view_preset'
    assert cmd['view'] == view_type


@pytest.mark.parametrize('mode', [
    'OBJECT', 'EDIT', 'SCULPT', 'VERTEX_PAINT', 'WEIGHT_PAINT', 'TEXTURE_PAINT', 'POSE'
])
def test_mode_set_commands(mock_server, blender_control_module, mode):
    """Test that mode_set commands are formatted correctly"""
    blender_control_module.BLENDER_PORT = 9999

    from blender_control import send_blender_command

    mock_server.received_commands.clear()
    send_blender_command('mode_set', mode=mode)
    time.sleep(0.1)

    assert len(mock_server.received_commands) == 1
    cmd = mock_server.received_commands[0]
    assert cmd['action'] == 'mode_set'
    assert cmd['mode'] == mode


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
