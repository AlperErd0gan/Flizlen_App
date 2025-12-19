import os
import sys
import logging

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from dotenv import load_dotenv

# Load env vars first
load_dotenv()

from backend.gemini_client import gemini_client

def test_live_keys():
    
    print("🔑 API Key Live Test")
    print("====================")
    
    keys = gemini_client.api_keys
    print(f"Found {len(keys)} keys in environment.")
    
    if len(keys) < 2:
        print("⚠️  Warning: Less than 2 keys found. Add GEMINI_API_KEY_2 to .env to test rotation.")
    
    # Test Key 1
    print("\n[1] Testing Primary Key...")
    try:
        response = gemini_client.generate_content("gemini-2.5-flash", "Say 'Key 1 OK' in 3 words")
        print(f"✅ Success! Response: {response.text.strip()}")
    except Exception as e:
        print(f"❌ Failed: {e}")

    if len(keys) >= 2:
        # Force Rotation
        print("\n🔄 Manually Rotating Key...")
        gemini_client.rotate_key()
        
        # Test Key 2
        print("[2] Testing Secondary Key...")
        try:
            response = gemini_client.generate_content("gemini-2.5-flash", "Say 'Key 2 OK' in 3 words")
            print(f"✅ Success! Response: {response.text.strip()}")
        except Exception as e:
            print(f"❌ Failed: {e}")
            
    print("\nDone.")

if __name__ == "__main__":
    test_live_keys()
