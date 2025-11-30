"""
FastAPI Backend for Flizlen App
Handles API endpoints and Gemini AI integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Flizlen App API",
    description="Backend API with Gemini AI integration",
    version="1.0.0"
)

# CORS middleware to allow Streamlit frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Warning: GEMINI_API_KEY not found in environment variables")

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str
    status: str

class HealthResponse(BaseModel):
    status: str
    message: str

# Initialize Gemini model
def get_gemini_model():
    """Get configured Gemini model"""
    try:
        # Try different model names for compatibility (newest first)
        # Based on available models from API
        model_names = [
            'gemini-2.5-flash',           # Fast and efficient
            'gemini-2.5-pro',             # Most capable
            'gemini-pro-latest',          # Latest stable
            'gemini-flash-latest',        # Latest fast model
            'gemini-2.0-flash',          # Alternative flash
            'gemini-1.5-pro-latest',      # Fallback
            'gemini-1.5-pro',             # Fallback
        ]
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                # Test if model is accessible with a simple test
                return model
            except Exception as e:
                print(f"Model {model_name} failed: {str(e)}")
                continue
        
        # If all fail, raise error with available models info
        try:
            # Try to list available models
            models = genai.list_models()
            available = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to initialize any Gemini model. Available models: {available[:5]}"
            )
        except:
            raise HTTPException(
                status_code=500, 
                detail="Failed to initialize Gemini model. Please check your API key and try using 'gemini-1.5-pro' or 'gemini-1.0-pro'"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Gemini model: {str(e)}. Please check your API key and model availability.")

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Flizlen App API is running"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    gemini_status = "configured" if GEMINI_API_KEY else "not_configured"
    return {
        "status": "healthy",
        "message": f"API is running. Gemini API: {gemini_status}"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint that processes user messages using Gemini AI
    """
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Gemini API key not configured. Please set GEMINI_API_KEY in your .env file"
        )
    
    try:
        model = get_gemini_model()
        
        # Build conversation context
        prompt = request.message
        
        # If there's conversation history, include it for context
        if request.conversation_history:
            context = "\n".join([
                f"User: {msg.get('user', '')}\nAssistant: {msg.get('assistant', '')}"
                for msg in request.conversation_history[-5:]  # Last 5 messages for context
            ])
            prompt = f"{context}\n\nUser: {request.message}\nAssistant:"
        
        # Generate response using Gemini
        response = model.generate_content(prompt)
        
        # Handle different response formats - try most common first
        response_text = None
        try:
            # Most common: direct text attribute
            if hasattr(response, 'text') and response.text:
                response_text = response.text
            # Alternative: candidates structure
            elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    response_text = candidate.content.parts[0].text
                elif hasattr(candidate, 'text'):
                    response_text = candidate.text
            # Fallback: try to extract from content
            elif hasattr(response, 'content'):
                if hasattr(response.content, 'parts') and len(response.content.parts) > 0:
                    response_text = response.content.parts[0].text
                elif hasattr(response.content, 'text'):
                    response_text = response.content.text
        except Exception as e:
            print(f"Error extracting response text: {e}")
        
        # Final fallback
        if not response_text:
            response_text = str(response)
            print(f"Warning: Using string representation of response: {type(response)}")
        
        return ChatResponse(
            response=response_text,
            status="success"
        )
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in chat endpoint: {error_details}")  # Log for debugging
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )

@app.post("/api/generate-text")
async def generate_text(prompt: str):
    """
    Simple text generation endpoint
    """
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Gemini API key not configured"
        )
    
    try:
        model = get_gemini_model()
        response = model.generate_content(prompt)
        
        # Handle different response formats
        if hasattr(response, 'text'):
            response_text = response.text
        elif hasattr(response, 'candidates') and len(response.candidates) > 0:
            response_text = response.candidates[0].content.parts[0].text
        elif hasattr(response, 'content'):
            response_text = response.content.parts[0].text if hasattr(response.content, 'parts') else str(response.content)
        else:
            response_text = str(response)
        
        return {
            "generated_text": response_text,
            "status": "success"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating text: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

