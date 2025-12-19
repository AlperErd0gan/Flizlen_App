import os
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
import logging
import time

logger = logging.getLogger(__name__)

class GeminiClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GeminiClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0
        self.model_cache = {}
        
        if not self.api_keys:
            logger.warning("No Gemini API keys found in environment variables.")
        else:
            self._configure_current_key()
            
        self._initialized = True

    def _load_api_keys(self):
        """Load all available Gemini API keys from environment variables."""
        keys = []
        
        # Check for GEMINI_API_KEY
        key1 = os.getenv("GEMINI_API_KEY")
        if key1:
            keys.append(key1)
            
        # Check for numbered keys (e.g., GEMINI_API_KEY_2, GEMINI_API_KEY_3, etc.)
        i = 2
        while True:
            key = os.getenv(f"GEMINI_API_KEY_{i}")
            if key:
                keys.append(key)
                i += 1
            else:
                break
                
        return keys

    def _configure_current_key(self):
        """Configure genai with the currently selected API key."""
        if not self.api_keys:
            return
            
        current_key = self.api_keys[self.current_key_index]
        # Mask key for logging
        masked_key = f"{current_key[:4]}...{current_key[-4:]}" if len(current_key) > 8 else "***"
        logger.info(f"Configuring Gemini API with key index {self.current_key_index} ({masked_key})")
        genai.configure(api_key=current_key)

    def rotate_key(self):
        """Switch to the next available API key."""
        if not self.api_keys or len(self.api_keys) <= 1:
            logger.warning("Key rotation requested but no alternative keys available.")
            return False

        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        self._configure_current_key()
        
        # Clear model cache as models might need re-instantiation (though usually configure is global)
        # But to be safe and ensure new configuration takes effect if models hold on to config
        self.model_cache = {} 
        return True

    def get_model(self, model_name: str, system_instruction: str = None):
        """Get or create a GenerativeModel."""
        cache_key = f"{model_name}_{hash(system_instruction) if system_instruction else 'no_sys'}"
        
        if cache_key not in self.model_cache:
            if system_instruction:
                model = genai.GenerativeModel(model_name, system_instruction=system_instruction)
            else:
                model = genai.GenerativeModel(model_name)
            self.model_cache[cache_key] = model
            
        return self.model_cache[cache_key]

    def embed_content(self, model: str, content, task_type: str = "retrieval_document"):
        """Wrapper for genai.embed_content with retry logic."""
        return self._execute_with_retry(
            genai.embed_content,
            model=model,
            content=content,
            task_type=task_type
        )

    def generate_content(self, model_name: str, prompt: str, system_instruction: str = None):
        """Wrapper for model.generate_content with retry logic."""
        
        def _generate():
            model = self.get_model(model_name, system_instruction)
            return model.generate_content(prompt)
            
        return self._execute_with_retry(_generate)

    def _execute_with_retry(self, func, *args, **kwargs):
        """Execute a function and retry with key rotation on specific errors."""
        max_retries = len(self.api_keys) if self.api_keys else 1
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
                
            except google_exceptions.ResourceExhausted as e:
                logger.warning(f"ResourceExhausted error on key index {self.current_key_index}: {e}")
                if attempt < max_retries - 1:
                    logger.info("Retrying with next API key...")
                    if self.rotate_key():
                        # Small delay to let config settle if needed
                        time.sleep(0.5) 
                        continue
                raise e
            except google_exceptions.PermissionDenied as e:
                logger.warning(f"PermissionDenied error on key index {self.current_key_index}: {e}")
                # This might happen if a key is invalid
                if attempt < max_retries - 1:
                     logger.info("Retrying with next API key...")
                     if self.rotate_key():
                        time.sleep(0.5)
                        continue
                raise e
            except Exception as e:
                # For other errors, we might not want to rotate key immediately?
                # But let's log it
                logger.error(f"Gemini API Error: {e}")
                raise e
        
        raise Exception("All API keys failed.")

# Initialize singleton
gemini_client = GeminiClient()
