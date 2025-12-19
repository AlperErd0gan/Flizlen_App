import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add parent directory to path to import backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.gemini_client import GeminiClient
from google.api_core import exceptions as google_exceptions

class TestGeminiClient(unittest.TestCase):
    def setUp(self):
        # Reset singleton for testing
        GeminiClient._instance = None
        
        # Patch environment variables
        self.env_patcher = patch.dict(os.environ, {
            "GEMINI_API_KEY": "fake_key_1",
            "GEMINI_API_KEY_2": "fake_key_2",
            "GEMINI_API_KEY_3": "fake_key_3"
        })
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    @patch('google.generativeai.configure')
    def test_initialization(self, mock_configure):
        client = GeminiClient()
        self.assertEqual(len(client.api_keys), 3)
        self.assertEqual(client.api_keys[0], "fake_key_1")
        # Should configure with first key
        mock_configure.assert_called_with(api_key="fake_key_1")

    @patch('google.generativeai.configure')
    def test_rotate_key(self, mock_configure):
        client = GeminiClient()
        
        # Rotate 1 -> 2
        success = client.rotate_key()
        self.assertTrue(success)
        self.assertEqual(client.current_key_index, 1)
        mock_configure.assert_called_with(api_key="fake_key_2")
        
        # Rotate 2 -> 3
        client.rotate_key()
        self.assertEqual(client.current_key_index, 2)
        mock_configure.assert_called_with(api_key="fake_key_3")
        
        # Rotate 3 -> 1 (Cycle)
        client.rotate_key()
        self.assertEqual(client.current_key_index, 0)
        mock_configure.assert_called_with(api_key="fake_key_1")

    @patch('google.generativeai.GenerativeModel')
    def test_execution_fallback(self, mock_model_class):
        # Mock the model instance and its generate_content method
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        
        # Setup side effects: 
        # 1st call: Quota Error (Key 1)
        # 2nd call: Quota Error (Key 2)
        # 3rd call: Success (Key 3)
        mock_model.generate_content.side_effect = [
            google_exceptions.ResourceExhausted("Quota exceeded"),
            google_exceptions.ResourceExhausted("Quota exceeded"),
            "Success Response"
        ]
        
        client = GeminiClient()
        
        with patch.object(client, 'rotate_key', wraps=client.rotate_key) as mock_rotate:
            response = client.generate_content("model-name", "prompt")
            
            self.assertEqual(response, "Success Response")
            self.assertEqual(mock_rotate.call_count, 2)
            self.assertEqual(client.current_key_index, 2) # Should be on key 3 (index 2)

    @patch('google.generativeai.GenerativeModel')
    def test_all_keys_fail(self, mock_model_class):
         mock_model = MagicMock()
         mock_model_class.return_value = mock_model
         
         # All 3 keys fail
         mock_model.generate_content.side_effect = [
            google_exceptions.ResourceExhausted("Quota exceeded"),
            google_exceptions.ResourceExhausted("Quota exceeded"),
            google_exceptions.ResourceExhausted("Quota exceeded")
         ]
         
         client = GeminiClient()
         
         with self.assertRaises(google_exceptions.ResourceExhausted):
             client.generate_content("model-name", "prompt")

if __name__ == '__main__':
    unittest.main()
