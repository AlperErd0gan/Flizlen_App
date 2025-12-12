"""
Streamlit Frontend for Flizlen App
User interface for interacting with the FastAPI backend and Gemini AI
"""

import streamlit as st
import requests
import os
import datetime
from typing import List, Dict

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# --- Page configuration ---
st.set_page_config(
    page_title="Flizlen App",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom Theme & CSS ---
# Warm Greens: #4A6741 (Forest), #8FBC8F (Sage)
# Warm Browns: #F5F1E6 (Parchment/Cream), #8B4513 (Saddle Brown)
st.markdown("""
    <style>
    /* Hide Streamlit top bar */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    /* Global Background */
    .stApp {
        background-color: #F5F1E6;
        color: #5A8560;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #5a8560 !important;
        font-family: 'Helvetica Neue', sans-serif;
    }

    /* Custom Header */
    .main-header {
        font-size: 3.5rem;
        font-weight: bold;
        color: #5a8560;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #6B8E23;
        text-align: center;
        margin-bottom: 3rem;
    }

    /* Buttons */
    .stButton>button {
        background-color: #5a8560;
        color: #F5F1E6;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #5A8560;
        color: #FFFFFF;
        border-color: #5A8560;
    }

    /* Chat Messages */
    .chat-message {
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* Streamlit's native chat message container adjustments */
    [data-testid="stChatMessage"] {
        background-color: #5a8560;
    }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        padding: 1rem;
        border-radius: 10px;
        color: #FFFFFF;
    }
    /* User Message Style (Green) */
    [data-testid="stChatMessage"][data-testid="user"] [data-testid="stMarkdownContainer"] {
        background-color: #D6E8D6; /* Very light green */
        color: #1a1a1a;
        border-left: 5px solid #5a8560;
    }
    /* Assistant Message Style (Brown/Beige) */
    [data-testid="stChatMessage"][data-testid="assistant"] [data-testid="stMarkdownContainer"] {
        background-color: #EBE5CE; /* Darker cream */
        color: #1a1a1a;
        border-left: 5px solid #8B4513;
    }

    /* News Cards */
    .news-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #6B8E23;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        color: #5A8560;
    }
    .news-date {
        color: #888;
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
    }
    .news-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #5a8560;
        margin-bottom: 0.5rem;
    }

    /* Navigation Card Style for Landing Page */
    .nav-card {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        height: 100%;
        border: 1px solid #E0E0E0;
    }
    
    /* Center avatar icons vertically inside chat message rows */
    [data-testid="stChatMessage"] {
        display: flex;
        align-items: center;
    }
    
    </style>
""", unsafe_allow_html=True)

# Custom CSS for Tips
st.markdown("""
    <style>
    .tip-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 10px;
        border-right: 5px solid #8B4513;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        color: #5A8560;
    }
    .tip-difficulty {
        display: inline-block;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        color: white;
        margin-bottom: 0.5rem;
    }
    .diff-easy { background-color: #4A6741; }
    .diff-medium { background-color: #DAA520; }
    .diff-hard { background-color: #8B4513; }
    
    .tip-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #8B4513;
        margin-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- State Management ---
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Helper Functions ---
def check_backend_health():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def send_chat_message(message: str, conversation_history: List[Dict]):
    """Send chat message to backend API"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/chat",
            json={
                "message": message,
                "conversation_history": conversation_history
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "detail": str(e)}

def fetch_news(limit: int = 10):
    """Fetch news from backend API"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/news?limit={limit}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "detail": str(e)}

def fetch_tips(limit: int = 10):
    """Fetch tips from backend API"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/tips?limit={limit}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "detail": str(e)}

def go_to_landing():
    st.session_state.page = "landing"

def go_to_chat():
    st.session_state.page = "chat"

def go_to_news():
    st.session_state.page = "news"

def go_to_tips():
    st.session_state.page = "tips"

# --- Views ---

def landing_page():
    st.markdown('<div class="main-header">🌿 Flizlen</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Tarım haberleri ve akıllı öneriler için dijital rehberiniz</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Create a container for the navigation buttons - now 3 columns
        c1, c2, c3 = st.columns(3, gap="medium")
        
        with c1:
            st.markdown("""
            <div style="text-align: center; padding: 20px; background: white; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 10px; height: 160px;">
                <h3 style="margin:0;">💬 Sohbet</h3>
                <p style="color: #666; font-size: 0.9rem;">Yapay zeka danışmanı ile sohbet edin</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Sohbete Git", use_container_width=True):
                go_to_chat()
                st.rerun()

        with c2:
            st.markdown("""
            <div style="text-align: center; padding: 20px; background: white; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 10px; height: 160px;">
                <h3 style="margin:0;">📰 Haberler</h3>
                <p style="color: #666; font-size: 0.9rem;">Son gelişmeler ve başlıklar</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Haberlere Git", use_container_width=True):
                go_to_news()
                st.rerun()
                
        with c3:
            st.markdown("""
            <div style="text-align: center; padding: 20px; background: white; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 10px; height: 160px;">
                <h3 style="margin:0;">💡 İpuçları</h3>
                <p style="color: #666; font-size: 0.9rem;">Pratik tarım bilgileri</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("İpuçlarına Git", use_container_width=True):
                go_to_tips()
                st.rerun()

def chat_interface():
    # Top Navigation Bar
    # We use 3 columns: [Button, Title, Spacer] to ensure the title is perfectly centered
    col_nav1, col_nav2, col_nav3 = st.columns([1, 8, 1])
    
    with col_nav1:
        if st.button("← Anasayfa"):
            go_to_landing()
            st.rerun()
            
    with col_nav2:
        # We use HTML here to force text-align center
        st.markdown(
            "<h2 style='text-align: center; margin-top: -20px; color: #5a8560;'>💬 Akıllı Asistan</h2>",
            unsafe_allow_html=True
        )
        
    with col_nav3:
        st.empty() # Spacer to balance the layout

    # Sidebar for Chat
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Backend URL input
        backend_url_input = st.text_input("Backend URL", value=BACKEND_URL)
        
        # Health check
        if st.button("Check Backend Status"):
            if check_backend_health():
                st.success("✅ Backend is running")
            else:
                st.error("❌ Backend is not accessible")
        
        st.divider()
        if st.button("🗑️ Clear Conversation"):
            st.session_state.messages = []
            st.rerun()

    # Display conversation history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Prepare conversation history for API
        conversation_history = [
            {
                "user": msg["content"] if msg["role"] == "user" else "",
                "assistant": msg["content"] if msg["role"] == "assistant" else ""
            }
            for msg in st.session_state.messages[:-1]
        ]
        
        # Show loading indicator
        with st.chat_message("assistant"):
            placeholder = st.empty()
            with st.spinner("Thinking..."):
                response = send_chat_message(prompt, conversation_history)

            if response and response.get("status") == "success":
                assistant_response = response.get("response", "No response received")
                placeholder.markdown(assistant_response)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_response
                })
            else:
                error_detail = response.get('detail', 'Unknown error') if response else 'Connection failed'
                error_msg = f"⚠️ I encountered an error: {error_detail}"
                placeholder.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

def news_interface():
    # Top Navigation Bar
    # We use 3 columns: [Button, Title, Spacer]
    col_nav1, col_nav2, col_nav3 = st.columns([1, 8, 1])
    
    with col_nav1:
        if st.button("← Anasayfa"):
            go_to_landing()
            st.rerun()
            
    with col_nav2:
        # We use HTML here to force text-align center
        st.markdown(
            "<h2 style='text-align: center; margin-top: -20px; color: #5a8560;'>📰 Son Haberler</h2>", 
            unsafe_allow_html=True
        )
        
    with col_nav3:
        st.empty() # Spacer to balance the layout

    # Fetch News from Backend
    with st.spinner("Haberler yükleniyor..."):
        news_response = fetch_news(limit=20)
        
    if news_response.get("status") == "success":
        news_items = news_response.get("data", [])
        
        if not news_items:
            st.info("Henüz hiç haber bulunmuyor.")
        
        for item in news_items:
            # Format date (handling different potential formats or None)
            display_date = "Tarih yok"
            if item.get('published_at'):
                try:
                    # Try to parse ISO format first
                    if 'T' in item['published_at']:
                        date_obj = datetime.datetime.fromisoformat(item['published_at'].replace('Z', '+00:00'))
                        display_date = date_obj.strftime("%B %d, %Y")
                    else:
                        display_date = item['published_at']
                except:
                    display_date = item['published_at']
            
            # Use 'summary' for the card content, fallback to truncated 'content'
            content_preview = item.get('summary')
            if not content_preview and item.get('content'):
                content_preview = item['content'][:150] + "..." if len(item['content']) > 150 else item['content']
            
            st.markdown(f"""
            <div class="news-card">
                <div class="news-date">{display_date}</div>
                <div class="news-title">{item['title']}</div>
                <div>{content_preview}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.info("Haberlerin sonu.")
        
    else:
        error_msg = news_response.get('detail', 'Sunucuya bağlanılamadı.')
        st.error(f"Haberler yüklenirken bir hata oluştu: {error_msg}")
        if st.button("Tekrar Dene", key="news_retry"):
            st.rerun()

def tips_interface():
    # Top Navigation Bar
    col_nav1, col_nav2, col_nav3 = st.columns([1, 8, 1])
    
    with col_nav1:
        if st.button("← Anasayfa"):
            go_to_landing()
            st.rerun()
            
    with col_nav2:
        st.markdown(
            "<h2 style='text-align: center; margin-top: -20px; color: #5a8560;'>💡 Pratik İpuçları</h2>", 
            unsafe_allow_html=True
        )
        
    with col_nav3:
        st.empty() 

    # Filter Options
    # diff_filter = st.selectbox("Zorluk Seviyesi", ["Tümü", "Kolay", "Orta", "Zor"], key="diff_filter")
    
    # Fetch Tips from Backend
    with st.spinner("İpuçları yükleniyor..."):
        # You could implement server-side filtering by passing difficulty to fetch_tips
        tips_response = fetch_tips(limit=20)
        
    if tips_response.get("status") == "success":
        tips_items = tips_response.get("data", [])
        
        if not tips_items:
            st.info("Henüz hiç ipucu bulunmuyor.")
        
        # Difficulty color mapping
        diff_colors = {
            "Kolay": "diff-easy",
            "Easy": "diff-easy",
            "Orta": "diff-medium",
            "Medium": "diff-medium",
            "Zor": "diff-hard",
            "Hard": "diff-hard"
        }
        
        for item in tips_items:
            # Map difficulty to CSS class
            diff_text = item.get('difficulty', 'Genel')
            diff_class = diff_colors.get(diff_text, "diff-medium")
            
            st.markdown(f"""
            <div class="tip-card">
                <span class="tip-difficulty {diff_class}">{diff_text}</span>
                <div class="tip-title">{item['title']}</div>
                <div>{item['content']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.info("İpuçlarının sonu.")
        
    else:
        error_msg = tips_response.get('detail', 'Sunucuya bağlanılamadı.')
        st.error(f"İpuçları yüklenirken bir hata oluştu: {error_msg}")
        if st.button("Tekrar Dene", key="tips_retry"):
            st.rerun()

# --- Main Controller ---
def main():
    if st.session_state.page == "landing":
        landing_page()
    elif st.session_state.page == "chat":
        chat_interface()
    elif st.session_state.page == "news":
        news_interface()
    elif st.session_state.page == "tips":
        tips_interface()

if __name__ == "__main__":
    main()