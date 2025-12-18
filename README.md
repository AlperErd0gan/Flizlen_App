# Filizlen App

A modern web application with FastAPI backend and Streamlit frontend, integrated with Google Gemini AI.

## Architecture :)

```
Flizlen_App/
├── backend/           # FastAPI backend
│   └── main.py       # API endpoints and Gemini integration
├── frontend/         # Streamlit frontend
│   └── app.py        # User interface
├── requirements.txt  # Python dependencies
├── .env.example      # Environment variables template
└── README.md         # This file
```

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd Flizlen_App
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

### Running the Application

#### Option 1: Use the Startup Scripts (Recommended) 

**Start everything at once:**
```bash
./start.sh
```

**Stop everything:**
```bash
./stop.sh
```

This will:
- Start backend on http://localhost:8000
- Start frontend on http://localhost:8501
- Show status and access URLs
- Log output to `backend.log` and `frontend.log`

#### Option 2: Run Backend and Frontend Separately

**Terminal 1 - Start Backend:**
```bash
./start_backend.sh
```
Or manually:
```bash
cd backend
python main.py
```

**Terminal 2 - Start Frontend:**
```bash
./start_frontend.sh
```
Or manually:
```bash
cd frontend
streamlit run app.py
```

### Access the Application

- **Frontend (Streamlit):** http://localhost:8501
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs (Swagger UI)
- **Alternative API Docs:** http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check with Gemini API status

### Chat
- `POST /api/chat` - Send chat message with conversation history
  ```json
  {
    "message": "Hello, how are you?",
    "conversation_history": []
  }
  ```

### Text Generation
- `POST /api/generate-text?prompt=Your prompt here` - Simple text generation

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Frontend Configuration
FRONTEND_PORT=8501
BACKEND_URL=http://localhost:8000
```

## Features

- FastAPI backend with async support
- Streamlit interactive frontend
- Google Gemini AI integration
- Conversation history support
- CORS enabled for frontend-backend communication
- Health check endpoints
- Error handling and validation
- RESTful API design

## Usage Example

1. Start the backend server
2. Start the Streamlit frontend
3. Open the frontend in your browser
4. Type a message in the chat input
5. The message is sent to the backend, processed by Gemini AI, and the response is displayed

## Development

### Project Structure

- `backend/main.py`: FastAPI application with Gemini integration
- `frontend/app.py`: Streamlit user interface
- `requirements.txt`: All Python dependencies

### Adding New Features

1. **Backend:** Add new endpoints in `backend/main.py`
2. **Frontend:** Update UI components in `frontend/app.py`
3. **API Integration:** Modify the request/response models as needed

## Troubleshooting

### Backend not starting
- Check if port 8000 is available
- Verify Python version (3.8+)
- Ensure all dependencies are installed

### Frontend can't connect to backend
- Verify backend is running on port 8000
- Check BACKEND_URL in frontend configuration
- Check CORS settings in backend

### Gemini API errors
- Verify GEMINI_API_KEY is set correctly in `.env`
- Check API key validity
- Ensure you have API quota available

## Model Cache Mechanism For Gemini Models (Short Explanation)

The backend stores the Gemini model in an in-memory cache:

```python
_model_cache = {}
```

This means the model is **loaded only once**, and all future requests reuse the same instance.
It behaves similarly to a lightweight *session* because:

* The **system prompt is applied once** and kept inside the model
* The model **persists in memory** while the server is running
* Requests do **not** reload or reinitialize the model
* Performance improves and token usage decreases

However, this is **not a user session**.
It does **not** store user-specific data—only the model instance is reused.

In short:

> **Model caching = Fast, consistent, low-cost model reuse (session-like behavior, but not per-user).**

## Embedding Model Performance

We compared the AI-based **text-embedding-004** model against a statistical **TF-IDF (Term Frequency-Inverse Document Frequency)** baseline found in `compare_embeddings.py`.

**Comparison Result:**
*   **TF-IDF Baseline:** Score **0.00** (Failed to capture semantic context)
*   **text-embedding-004 (AI):** Score **0.18** (Successfully captured semantic context)

This proves that the AI model significantly outperforms traditional statistical methods in understanding semantic relationships, even without exact keyword matches. Therefore we used the AI model for embedding.

## 📄 License

This project is provided as-is for development purposes.

##  Contributing

Feel free to extend this project with additional features:
- Database integration
- User authentication
- File upload support
- Advanced AI features
- Multi-language support

