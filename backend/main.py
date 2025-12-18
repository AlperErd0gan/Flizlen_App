"""
FastAPI Backend for Filizlen App
Handles API endpoints and Gemini AI integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
# Load environment variables immediately
load_dotenv()

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from backend import database
from backend.rag_system import rag_system
from contextlib import asynccontextmanager

# Load environment variables (kept for safety, duplicate is harmless)
load_dotenv()

SYSTEM_PROMPT = """
Sen, “Chatbot Destekli Akıllı Tarım Uygulaması” için özel olarak 
tasarlanmış bir yapay zekâ danışmanısın. Tüm yanıtların yalnızca bu 
uygulamanın kapsamı ve amacı doğrultusunda üretilmelidir. Cevap verirken 
kullanıcı ile konuştuğunu unutma. Veri tabanından gelen bilgileri kullanırken
"verdiğiniz bilgi" gibi ifadeler kullanma. Bilgiyi doğal bir sohbet akışı içinde sun.
Sürekli olarak "veri tabanımızda bulunan haberlere göre" diyerek kendini tekrar etme.

1. Uygulamanın amacı tarım ile ilgilenen kullanıcılar için: 
- Tarım haberleri, 
- Meteorolojik veriler, 
- Bitki yetiştirme rehberleri, 
- Hastalık ve zararlı tanımları, 
- Sulama, gübreleme ve bakım önerileri, 
- Haftalık tarım ipuçları, 
- Tarımsal karar destek bilgileri 
sunmaktır. 

2. Cevapların yalnızca şu bilgi alanlarıyla sınırlı olmalıdır: 
- Tarım haberleri 
- İklim ve meteoroloji verileri 
- Bitki yetiştirme bilgileri 
- Gübreleme, sulama ve bakım teknikleri 
- Zararlı ve hastalık belirtileri 
- Kullanıcıdan gelen bağlam 
- Uygulamada yer alan rehber içerikler 

Bu alanların dışında bilgi üretmek yasaktır. Ancak kullanıcı veritabanındaki bir konsept hakkında (örneğin "nasıl çalışır") detaylı bilgi isterse, genel tarım bilginle konuyu açabilirsin. 

3. Her zaman “Akıllı Tarım Danışmanı” rolünde yanıt vermelisin. 
Yanıtların teknik, doğru, anlaşılır ve tarım odaklı olmalıdır. Gereksiz 
sohbet, hikâye, tahmin veya tarım dışı içerik üretmemelisin. 

4. Kullanıcı tarım dışı bir konu sorarsa şu şekilde yanıt ver: 

“Bu uygulama tarımsal danışmanlık amacıyla tasarlanmıştır. Sorunuz 
uygulama kapsamı dışındadır. Tarımla ilgili bir konuda yardımcı 
olabilirim.” 

Son kural: Tüm yanıtların yalnızca Chatbot Destekli Akıllı Tarım Uygulaması kapsamında olmalıdır.
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load RAG data on startup
    print("INFO: Initializing RAG system...")
    try:
        rag_system.load_data()
        print("INFO: RAG system initialized successfully")
    except Exception as e:
        print(f"WARNING: RAG system initialization failed: {e}")
    yield
    # Clean up (if needed)


# Initialize FastAPI app
# Initialize FastAPI app
app = FastAPI(
    title="Filizlen App API",
    description="Backend API with Gemini AI integration and RAG",
    version="1.1.0",
    lifespan=lifespan
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

# News Models
class NewsCreate(BaseModel):
    title: str
    summary: str
    content: str
    category_id: int
    image_url: Optional[str] = None
    published_at: Optional[str] = None  # Format: "YYYY-MM-DD HH:MM:SS" or ISO format

class NewsUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    published_at: Optional[str] = None  # Format: "YYYY-MM-DD HH:MM:SS" or ISO format

# Tips Models
class TipCreate(BaseModel):
    title: str
    content: str
    difficulty: Optional[str] = None

class TipUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    difficulty: Optional[str] = None

# Category Models
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

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
                model = genai.GenerativeModel(model_name, system_instruction=SYSTEM_PROMPT)
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

# Cache for models to avoid recreating them and resending system prompt
_model_cache = {}

async def generate_with_fallback(prompt: str):
    """
    Attempts to generate content using a prioritized list of models.
    If a ResourceExhausted (Quota) error occurs, it switches to the next model.
    Uses cached models with system_instruction for efficiency (avoids sending system prompt in every request).
    """
    # Priority list as requested
    MODEL_PRIORITY = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite"
    ]
    
    last_exception = None

    for model_name in MODEL_PRIORITY:
        try:
            print(f"INFO: Attempting generation with model: {model_name}")
            
            # Use cached model if available, otherwise create and cache it
            if model_name not in _model_cache:
                try:
                    # Try with system_instruction first (most efficient - system prompt sent once)
                    _model_cache[model_name] = genai.GenerativeModel(
                        model_name, 
                        system_instruction=SYSTEM_PROMPT
                    )
                    print(f"INFO: Created and cached model {model_name} with system_instruction")
                except (TypeError, ValueError) as e:
                    # Fallback: if system_instruction not supported, create model without it
                    # and we'll add system prompt to each request
                    _model_cache[model_name] = {
                        'model': genai.GenerativeModel(model_name),
                        'has_system_instruction': False
                    }
                    print(f"INFO: Created and cached model {model_name} without system_instruction (fallback mode)")
            
            # Get model from cache
            cached_item = _model_cache[model_name]
            
            # Check if it's a dict (fallback mode) or direct model (with system_instruction)
            if isinstance(cached_item, dict):
                # Fallback mode: add system prompt to each request
                model = cached_item['model']
                full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"
                response = model.generate_content(full_prompt)
            else:
                # Optimized mode: model has system_instruction, use prompt directly
                model = cached_item
                response = model.generate_content(prompt)
            
            return response
            
        except google_exceptions.ResourceExhausted as e:
            print(f"WARNING: Quota exceeded for {model_name}. Switching to fallback...")
            last_exception = e
            continue  # Try the next model in the list
            
        except Exception as e:
            # If it's a different error (e.g. InvalidArgument), usually we shouldn't retry
            # simply with a different model, but for robustness we can log it.
            print(f"ERROR: Failed with {model_name}: {str(e)}")
            last_exception = e
            # Depending on the error type, you might want to break here. 
            # For now, we continue to try the next model just in case.
            continue

    # If loop finishes without returning, raise the last exception
    raise last_exception if last_exception else Exception("All models failed to generate content.")

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Filizlen App API is running"
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
    Chat endpoint that processes user messages using Gemini AI with Fallback
    """
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Gemini API key not configured. Please set GEMINI_API_KEY in your .env file"
        )
    
    try:
        # Build conversation context
        prompt_text = request.message
        
        # If there's conversation history, include it for context
        if request.conversation_history:
            context = "\n".join([
                f"User: {msg.get('user', '')}\nAssistant: {msg.get('assistant', '')}"
                for msg in request.conversation_history[-5:]
            ])
            prompt_text = f"{context}\n\nUser: {request.message}\nAssistant:"
        
        # RAG Retrieval
        retrieved_docs = rag_system.search(request.message, top_k=3)
        
        context_block = ""
        if retrieved_docs:
            print(f"INFO: Retrieved {len(retrieved_docs)} relevant documents")
            context_block = "\n".join([
                f"--- BEGIN CONTEXT FROM DATABASE ({doc['type']}) ---\n{doc['content']}\n--- END CONTEXT ---"
                for doc in retrieved_docs
            ])
            
            # Augment User Message
            prompt_text = (
                f"Kullanıcı Sorusu: {request.message}\n\n"
                f"İlgili Dokümanlar (Context):\n"
                f"{context_block}\n\n"
                f"Yönerge: Yukarıdaki dokümanları temel alarak cevapla. Ancak kullanıcı konsepti anlamaya yönelik genel sorular sorarsa (örn: 'nasıl çalışır?') ve dokümanlar yetersizse, genel tarım bilginle konuyu detaylandır. 'Veri tabanımıza göre' ifadesini gereksiz yere tekrarlama."
            )
            
            # If conversation history exists, we need to bridge it carefully
            if request.conversation_history:
                 context = "\n".join([
                    f"User: {msg.get('user', '')}\nAssistant: {msg.get('assistant', '')}"
                    for msg in request.conversation_history[-5:]
                ])
                 prompt_text = f"{context}\n\n{prompt_text}\nAssistant:"

        # Fallback function
        response = await generate_with_fallback(prompt_text)
        
        # Handle different response formats
        response_text = None
        try:
            if hasattr(response, 'text') and response.text:
                response_text = response.text
            elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    response_text = candidate.content.parts[0].text
                elif hasattr(candidate, 'text'):
                    response_text = candidate.text
            elif hasattr(response, 'content'):
                if hasattr(response.content, 'parts') and len(response.content.parts) > 0:
                    response_text = response.content.parts[0].text
                elif hasattr(response.content, 'text'):
                    response_text = response.content.text
        except Exception as e:
            print(f"Error extracting response text: {e}")
        
        if not response_text:
            response_text = str(response)
            
        print("INFO: RAGAS metrics calculation (Faithfulness, Answer Relevancy) should be triggered here.")
        
        return ChatResponse(
            response=response_text,
            status="success"
        )
    
    except google_exceptions.ResourceExhausted:
        # If even the fallback fails
        return ChatResponse(
            response="Sistem şu anda çok yoğun (Kota limiti aşıldı). Lütfen bir süre sonra tekrar deneyin.",
            status="error"
        )
    except Exception as e:
        import traceback
        print(f"[CHAT ENDPOINT ERROR]\n{traceback.format_exc()}")
        return ChatResponse(
            response="Sistemde beklenmeyen bir hata oluştu. Lütfen bağlantınızı kontrol edin.",
            status="error"
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

# ========== NEWS ENDPOINTS ==========

@app.get("/api/news")
async def get_news(limit: Optional[int] = None, category_id: Optional[int] = None):
    """Tüm haberleri getir"""
    try:
        news = database.get_all_news(limit=limit, category_id=category_id)
        return {"status": "success", "data": news, "count": len(news)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")

@app.get("/api/news/{news_id}")
async def get_news_by_id(news_id: int):
    """ID'ye göre haber getir"""
    news = database.get_news_by_id(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return {"status": "success", "data": news}

@app.post("/api/news")
async def create_news(news: NewsCreate):
    """Yeni haber ekle"""
    try:
        news_id = database.add_news(
            title=news.title,
            summary=news.summary,
            content=news.content,
            category_id=news.category_id,
            image_url=news.image_url,
            published_at=news.published_at
        )
        return {"status": "success", "message": "News created", "id": news_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating news: {str(e)}")

@app.put("/api/news/{news_id}")
async def update_news(news_id: int, news: NewsUpdate):
    """Haber güncelle"""
    try:
        success = database.update_news(
            news_id=news_id,
            title=news.title,
            summary=news.summary,
            content=news.content,
            category_id=news.category_id,
            image_url=news.image_url,
            published_at=news.published_at
        )
        if not success:
            raise HTTPException(status_code=404, detail="News not found")
        return {"status": "success", "message": "News updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating news: {str(e)}")

@app.delete("/api/news/{news_id}")
async def delete_news(news_id: int):
    """Haber sil"""
    try:
        success = database.delete_news(news_id)
        if not success:
            raise HTTPException(status_code=404, detail="News not found")
        return {"status": "success", "message": "News deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting news: {str(e)}")

# ========== TIPS ENDPOINTS ==========

@app.get("/api/tips")
async def get_tips(limit: Optional[int] = None, difficulty: Optional[str] = None):
    """Tüm tips'leri getir"""
    try:
        tips = database.get_all_tips(limit=limit, difficulty=difficulty)
        return {"status": "success", "data": tips, "count": len(tips)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tips: {str(e)}")

@app.get("/api/tips/{tip_id}")
async def get_tip_by_id(tip_id: int):
    """ID'ye göre tip getir"""
    tip = database.get_tip_by_id(tip_id)
    if not tip:
        raise HTTPException(status_code=404, detail="Tip not found")
    return {"status": "success", "data": tip}

@app.post("/api/tips")
async def create_tip(tip: TipCreate):
    """Yeni tip ekle"""
    try:
        tip_id = database.add_tip(
            title=tip.title,
            content=tip.content,
            difficulty=tip.difficulty
        )
        return {"status": "success", "message": "Tip created", "id": tip_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating tip: {str(e)}")

@app.put("/api/tips/{tip_id}")
async def update_tip(tip_id: int, tip: TipUpdate):
    """Tip güncelle"""
    try:
        success = database.update_tip(
            tip_id=tip_id,
            title=tip.title,
            content=tip.content,
            difficulty=tip.difficulty
        )
        if not success:
            raise HTTPException(status_code=404, detail="Tip not found")
        return {"status": "success", "message": "Tip updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating tip: {str(e)}")

@app.delete("/api/tips/{tip_id}")
async def delete_tip(tip_id: int):
    """Tip sil"""
    try:
        success = database.delete_tip(tip_id)
        if not success:
            raise HTTPException(status_code=404, detail="Tip not found")
        return {"status": "success", "message": "Tip deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting tip: {str(e)}")

# ========== CATEGORIES ENDPOINTS ==========

@app.get("/api/categories")
async def get_categories():
    """Tüm kategorileri getir"""
    try:
        categories = database.get_all_categories()
        return {"status": "success", "data": categories, "count": len(categories)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching categories: {str(e)}")

@app.get("/api/categories/{category_id}")
async def get_category_by_id(category_id: int):
    """ID'ye göre kategori getir"""
    category = database.get_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"status": "success", "data": category}

@app.post("/api/categories")
async def create_category(category: CategoryCreate):
    """Yeni kategori ekle"""
    try:
        category_id = database.add_category(
            name=category.name,
            description=category.description
        )
        return {"status": "success", "message": "Category created", "id": category_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating category: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

