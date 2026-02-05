#!/usr/bin/env python3
"""
Tests for the blender_control module.
Tests the UDP communication without requiring Talon to be running.
"""

import unittest
import socket
import json
import threading
import time
from unittest.mock import patch, MagicMock


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


class TestBlenderControl(unittest.TestCase):
    """Test cases for blender_control module"""

    def setUp(self):
        """Set up test fixtures"""
        self.server = MockBlenderServer()
        self.server.start()

    def tearDown(self):
        """Clean up after tests"""
        self.server.stop()

    def test_send_command_success(self):
        """Test sending a command successfully"""
        # Import here to avoid Talon dependency
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))

        # Mock the talon module
        sys.modules['talon'] = MagicMock()

        import blender_control
        original_port = blender_control.BLENDER_PORT
        blender_control.BLENDER_PORT = 9999

        from blender_control import send_blender_command

        try:
            result = send_blender_command('pan', direction=[100, 0])

            self.assertTrue(result)
            time.sleep(0.2)  # Wait for server to receive
            self.assertEqual(len(self.server.received_commands), 1)
            self.assertEqual(self.server.received_commands[0]['action'], 'pan')
            self.assertEqual(self.server.received_commands[0]['direction'], [100, 0])
        finally:
            blender_control.BLENDER_PORT = original_port

    def test_send_command_with_multiple_parameters(self):
        """Test sending a command with multiple parameters"""
        import sys
        sys.modules['talon'] = MagicMock()

        import blender_control
        original_port = blender_control.BLENDER_PORT
        blender_control.BLENDER_PORT = 9999

        from blender_control import send_blender_command

        try:
            result = send_blender_command('test', param1='value1', param2=42, param3=[1, 2, 3])

            self.assertTrue(result)
            time.sleep(0.2)
            self.assertEqual(len(self.server.received_commands), 1)
            cmd = self.server.received_commands[0]
            self.assertEqual(cmd['action'], 'test')
            self.assertEqual(cmd['param1'], 'value1')
            self.assertEqual(cmd['param2'], 42)
            self.assertEqual(cmd['param3'], [1, 2, 3])
        finally:
            blender_control.BLENDER_PORT = original_port

    def test_send_command_server_unreachable(self):
        """Test handling when Blender is not running"""
        import sys
        sys.modules['talon'] = MagicMock()

        import blender_control
        original_port = blender_control.BLENDER_PORT
        blender_control.BLENDER_PORT = 9999

        from blender_control import send_blender_command

        try:
            # Stop the server to simulate Blender not running
            self.server.stop()

            result = send_blender_command('pan', direction=[100, 0])

            # Should return True even if server is down (fire and forget)
            # The function doesn't wait for acknowledgment
            self.assertTrue(result)
        finally:
            blender_control.BLENDER_PORT = original_port

    def test_pan_commands_format(self):
        """Test that pan commands are formatted correctly"""
        import sys
        sys.modules['talon'] = MagicMock()

        import blender_control
        original_port = blender_control.BLENDER_PORT
        blender_control.BLENDER_PORT = 9999

        from blender_control import send_blender_command

        try:
            # Test different pan directions
            test_cases = [
                {'direction': [-100, 0], 'description': 'left'},
                {'direction': [100, 0], 'description': 'right'},
                {'direction': [0, 100], 'description': 'up'},
                {'direction': [0, -100], 'description': 'down'},
            ]

            for test_case in test_cases:
                self.server.received_commands.clear()
                send_blender_command('pan', direction=test_case['direction'])
                time.sleep(0.1)

                self.assertEqual(len(self.server.received_commands), 1,
                               f"Failed for {test_case['description']}")
                cmd = self.server.received_commands[0]
                self.assertEqual(cmd['action'], 'pan')
                self.assertEqual(cmd['direction'], test_case['direction'])
        finally:
            blender_control.BLENDER_PORT = original_port

    def test_json_serialization(self):
        """Test that commands are properly JSON serialized"""
        import sys
        sys.modules['talon'] = MagicMock()

        import blender_control
        original_port = blender_control.BLENDER_PORT
        blender_control.BLENDER_PORT = 9999

        from blender_control import send_blender_command

        try:
            # Test with various data types
            send_blender_command('test',
                               string_param='hello',
                               int_param=42,
                               float_param=3.14,
                               bool_param=True,
                               list_param=[1, 2, 3],
                               dict_param={'key': 'value'})

            time.sleep(0.2)
            self.assertEqual(len(self.server.received_commands), 1)
            cmd = self.server.received_commands[0]

            # Verify all parameters were preserved
            self.assertEqual(cmd['string_param'], 'hello')
            self.assertEqual(cmd['int_param'], 42)
            self.assertAlmostEqual(cmd['float_param'], 3.14)
            self.assertEqual(cmd['bool_param'], True)
            self.assertEqual(cmd['list_param'], [1, 2, 3])
            self.assertEqual(cmd['dict_param'], {'key': 'value'})
        finally:
            blender_control.BLENDER_PORT = original_port


class TestBlenderCommandValidation(unittest.TestCase):
    """Test input validation and sanitization"""

    def test_invalid_json_characters(self):
        """Test handling of characters that could break JSON"""
        server = MockBlenderServer(port=9998)
        server.start()

        try:
            import sys
            sys.modules['talon'] = MagicMock()

            # Mock the BLENDER_PORT to use our test port
            import blender_control
            original_port = blender_control.BLENDER_PORT
            blender_control.BLENDER_PORT = 9998

            from blender_control import send_blender_command

            # These should all be properly escaped by json.dumps
            special_strings = [
                'test"quote',
                "test'apostrophe",
                'test\\backslash',
                'test\nnewline',
                'test\ttab',
            ]

            for test_str in special_strings:
                server.received_commands.clear()
                send_blender_command('test', param=test_str)
                time.sleep(0.1)

                self.assertEqual(len(server.received_commands), 1)
                self.assertEqual(server.received_commands[0]['param'], test_str)

            # Restore original port
            blender_control.BLENDER_PORT = original_port
        finally:
            server.stop()


if __name__ == '__main__':
    unittest.main()
