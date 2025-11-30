# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Set Up Environment
```bash
# Copy the example env file
cp env.example .env

# Edit .env and add your Gemini API key
# Get your API key from: https://makersuite.google.com/app/apikey
```

### Step 3: Start Backend (Terminal 1)
```bash
cd backend
python main.py
```
You should see: `Application startup complete` and the API running on http://localhost:8000

### Step 4: Start Frontend (Terminal 2)
```bash
cd frontend
streamlit run app.py
```
The browser will automatically open to http://localhost:8501

### Step 5: Test It Out!
1. Open the Streamlit app in your browser
2. Type a message in the chat
3. See the AI response powered by Gemini!

## 🔍 Verify Everything Works

### Check Backend
- Visit: http://localhost:8000/docs (Swagger UI)
- Visit: http://localhost:8000/health (Health check)

### Check Frontend
- The Streamlit app should show "✅ Backend is running" when you click "Check Backend Status"

## 🐛 Common Issues

**Backend won't start:**
- Make sure port 8000 is free: `lsof -ti:8000` (kill if needed)
- Check Python version: `python --version` (needs 3.8+)

**Frontend can't connect:**
- Ensure backend is running first
- Check that BACKEND_URL in frontend matches your backend URL

**Gemini API errors:**
- Verify your API key in `.env` file
- Make sure the key is valid and has quota

## 📚 Next Steps

- Read the full README.md for detailed documentation
- Explore the API docs at http://localhost:8000/docs
- Customize the frontend in `frontend/app.py`
- Add new endpoints in `backend/main.py`

Happy coding! 🎉

