import os
import sys
import time
import unittest
import threading
import subprocess
import requests
from self_awareness_client import SelfAwarenessClient

class TestSelfAwareness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start server in a separate process
        cls.server_process = subprocess.Popen(
            [sys.executable, "server.py"],
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        # Give the server time to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:8765/")
            if response.status_code != 404:  # We expect 404 since we don't have a root endpoint
                raise Exception("Server is not running correctly")
        except requests.exceptions.ConnectionError:
            cls.server_process.terminate()
            raise Exception("Server failed to start")

    @classmethod
    def tearDownClass(cls):
        # Terminate the server process
        cls.server_process.terminate()
        cls.server_process.wait()

    def test_client_connection(self):
        # Create a client
        client = SelfAwarenessClient()
        
        # Connect to server
        client.connect()
        
        # Wait for connection to establish
        time.sleep(2)
        
        # Verify connection
        self.assertTrue(client.connected)
        self.assertIsNotNone(client.client_id)
        
        # Query system status
        status = client.query_system_status()
        self.assertEqual(status["type"], "query_response")
        self.assertEqual(status["query_type"], "system_status")
        
        # Update decision metrics
        client.update_decision_metrics(0.9, 5.0, 0.2)
        
        # Wait for server to process
        time.sleep(2)
        
        # Get metrics
        metrics = client.get_metrics()
        self.assertIn("decision_confidence", metrics)
        self.assertEqual(metrics["decision_confidence"], 0.9)
        
        # Disconnect
        client.disconnect()
        
        # Verify disconnection
        self.assertFalse(client.connected)

if __name__ == "__main__":
    unittest.main()
