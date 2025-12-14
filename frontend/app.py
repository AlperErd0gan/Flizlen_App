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
# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
if not BACKEND_URL.startswith("http"):
    BACKEND_URL = f"http://{BACKEND_URL}"

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
    
    /* --- Professional Landing Page Theme --- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Hero Section Styling */
    .main-header {
        font-family: 'Inter', sans-serif;
        font-size: 4.5rem;
        font-weight: 800;
        background: linear-gradient(120deg, #4A6741, #8FBC8F);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -1.5px;
        padding-top: 2rem;
    }
    
    .sub-header {
        font-family: 'Inter', sans-serif;
        font-size: 1.25rem;
        color: #6B8E23;
        text-align: center;
        font-weight: 400;
        margin-bottom: 4rem;
        opacity: 0.9;
    }

    /* Card Container Styling */
    .landing-card {
        background: white;
        border-radius: 24px;
        padding: 2.5rem 1.5rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.04);
        border: 1px solid rgba(0,0,0,0.03);
        height: 220px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 1rem;
    }
    
    .landing-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(74, 103, 65, 0.1);
        border-color: rgba(74, 103, 65, 0.2);
    }
    
    .landing-icon {
        font-size: 3rem;
        margin-bottom: 1.5rem;
        background: #F5F1E6;
        width: 80px;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
    }
    
    .landing-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.75rem;
    }
    
    .landing-desc {
        font-size: 0.9rem;
        color: #7f8c8d;
        line-height: 1.5;
    }
    
    /* Enhance Streamlit Buttons to match cards */
    .stButton button {
        background-color: #4A6741 !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(74, 103, 65, 0.2) !important;
        transition: all 0.2s ease !important;
        white-space: nowrap !important;
        min-width: 140px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(74, 103, 65, 0.3) !important;
        background-color: #3e5636 !important;
    }
    
    /* Footer Styling */
    .footer-container {
        text-align: center;
        margin-top: 6rem;
        padding-top: 3rem;
        border-top: 1px solid #e0e0e0;
        color: #95a5a6;
        font-size: 0.85rem;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #5a8560 !important;
        font-family: 'Helvetica Neue', sans-serif;
    }

    /* Custom Header */
    /* The main-header and sub-header above override these for the landing page */
    /* .main-header {
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
    } */

    /* Buttons */
    /* The .stButton button above overrides this */
    /* .stButton>button {
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
    } */

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
    /* The .landing-card above overrides this */
    /* .nav-card {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        height: 100%;
        border: 1px solid #E0E0E0;
    } */
    
    /* Center avatar icons vertically inside chat message rows */
    [data-testid="stChatMessage"] {
        display: flex;
        align-items: center;
    }
    
    /* Footer Styling */
    /* The .footer-container above overrides this */
    /* .footer-container {
        text-align: center;
        margin-top: 5rem;
        padding-top: 2rem;
        border-top: 1px solid #eee;
        color: #aaa;
        font-size: 0.8rem;
        display: flex;
        justify-content: center;
        gap: 2rem;
    } */
    
    /* News Link Styling */
    a.news-card-link {
        text-decoration: none !important;
        color: inherit !important;
        display: block;
    }
    a.news-card-link:hover .news-card {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border-left: 5px solid #5a8560;
    }
    
    /* Hide Streamlit anchor links and disable functionality */
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, .stMarkdown h4 a, .stMarkdown h5 a, .stMarkdown h6 a {
        display: none !important;
        pointer-events: none !important;
        cursor: default !important;
    }
    /* Also target specific data-testid if needed for newer Streamlit versions */
    [data-testid="stMarkdownContainer"] a.anchor-link {
        display: none !important;
        pointer-events: none !important;
        cursor: default !important;
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
if "selected_news" not in st.session_state:
    st.session_state.selected_news = None

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

def fetch_news_item(news_id: int):
    """Fetch single news item from backend API"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/news/{news_id}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "detail": str(e)}

def go_to_landing():
    st.query_params.clear()
    st.session_state.page = "landing"

def go_to_chat():
    st.query_params.clear()
    st.session_state.page = "chat"

def go_to_news():
    st.query_params.clear()
    st.session_state.page = "news"

def go_to_tips():
    st.query_params.clear()
    st.session_state.page = "tips"

def go_to_news_detail(news_item):
    st.session_state.selected_news = news_item
    st.session_state.page = "news_detail"

def display_footer():
    """Display the application footer"""
    st.markdown("""
    <div class="footer-container">
        <div>© 2025 Flizlen App. Tüm hakları saklıdır.</div>
    </div>
    """, unsafe_allow_html=True)

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
            <div class="landing-card">
                <div class="landing-icon">💬</div>
                <div class="landing-title">Sohbet</div>
                <div class="landing-desc">Yapay zeka asistanı ile<br>tarım üzerine konuşun</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Sohbete Başla", use_container_width=True):
                go_to_chat()
                st.rerun()

        with c2:
            st.markdown("""
            <div class="landing-card">
                <div class="landing-icon">📰</div>
                <div class="landing-title">Haberler</div>
                <div class="landing-desc">Tarımsal gelişmeler ve<br>güncel başlıklar</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Haberleri Oku", use_container_width=True):
                go_to_news()
                st.rerun()
                
        with c3:
            st.markdown("""
            <div class="landing-card">
                <div class="landing-icon">💡</div>
                <div class="landing-title">İpuçları</div>
                <div class="landing-desc">Verimlilik için<br>pratik bilgiler</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("İpuçlarını Gör", use_container_width=True):
                go_to_tips()
                st.rerun()

    # Footer
    display_footer()

def chat_interface():
    # Top Navigation Bar
    # We use 3 columns: [Button, Title, Spacer] to ensure the title is perfectly centered
    col_nav1, col_nav2, col_nav3 = st.columns([2, 5, 2])
    
    with col_nav1:
        if st.button("← Ana Sayfa"):
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
    col_nav1, col_nav2, col_nav3 = st.columns([2, 5, 2])
    
    with col_nav1:
        if st.button("← Ana Sayfa"):
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
        
        for index, item in enumerate(news_items):
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
            
            
            # Navigation using HTML link to preserve style
            # We create a link that reloads the page with ?news_id={id}
            news_id = item.get('id', index)
            js_link = f"?news_id={news_id}"
            
            st.markdown(f"""
            <a href="{js_link}" target="_self" class="news-card-link">
                <div class="news-card">
                    <div class="news-date">{display_date}</div>
                    <div class="news-title">{item['title']}</div>
                    <div style="color: #555;">{content_preview}</div>
                </div>
            </a>
            """, unsafe_allow_html=True)
            
        st.info("Haberlerin sonu.")
        
    else:
        error_msg = news_response.get('detail', 'Sunucuya bağlanılamadı.')
        st.error(f"Haberler yüklenirken bir hata oluştu: {error_msg}")
        if st.button("Tekrar Dene", key="news_retry"):
            st.rerun()

    # Footer
    display_footer()

def news_detail_interface():
    # Helper to go back
    def back_to_news():
        # Clear query params
        st.query_params.clear()
        st.session_state.page = "news"
        st.session_state.selected_news = None
        
    # Top Navigation
    col_nav1, col_nav2, col_nav3 = st.columns([2, 5, 2])
    
    with col_nav1:
        c_back, c_home = st.columns([1, 1])
        with c_back:
            if st.button("← Geri"):
                back_to_news()
                st.rerun()
        with c_home:
            if st.button("🏠 Ana Sayfa"):
                go_to_landing()
                st.rerun()
            
    with col_nav2:
        st.markdown(
            "<h2 style='text-align: center; margin-top: -20px; color: #5a8560;'>Haber Detayı</h2>", 
            unsafe_allow_html=True
        )

    # Get news item - either from session state or fetch using ID from query params
    item = st.session_state.selected_news
    
    # If no item in session but we have ID in query params (direct link or refresh)
    if not item and "news_id" in st.query_params:
        try:
            news_id = int(st.query_params["news_id"])
            with st.spinner("Haber yükleniyor..."):
                response = fetch_news_item(news_id)
                if response.get("status") == "success":
                    item = response.get("data")
                    st.session_state.selected_news = item
        except:
            pass
    
    if not item:
        st.error("Haber bulunamadı.")
        if st.button("Geri Dön"):
            back_to_news()
            st.rerun()
        return

    # Display News Detail
    # Parse date for display
    display_date = "Tarih yok"
    if item.get('published_at'):
        try:
            if 'T' in item['published_at']:
                date_obj = datetime.datetime.fromisoformat(item['published_at'].replace('Z', '+00:00'))
                display_date = date_obj.strftime("%B %d, %Y")
            else:
                display_date = item['published_at']
        except:
            display_date = item['published_at']

    st.markdown(f"""
    <div style="background-color: white; padding: 2.5rem; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-top: 1rem;">
        <h1 style="color: #4A6741; margin-bottom: 0.5rem; font-size: 2rem;">{item['title']}</h1>
        <div style="color: #888; margin-bottom: 2rem; font-style: italic; border-bottom: 1px solid #eee; padding-bottom: 1rem;">
            {display_date}
        </div>
        <div style="line-height: 1.8; color: #333; font-size: 1.1rem; whitespace: pre-wrap; font-family: 'Helvetica Neue', sans-serif;">
            {item.get('content', '')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    display_footer()

def tips_interface():
    # Top Navigation Bar
    col_nav1, col_nav2, col_nav3 = st.columns([2, 5, 2])
    
    with col_nav1:
        if st.button("← Ana Sayfa"):
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

    # Footer
    display_footer()

# --- Main Controller ---
def main():
    # Check for query params for routing
    if "news_id" in st.query_params:
        st.session_state.page = "news_detail"

    if st.session_state.page == "landing":
        landing_page()
    elif st.session_state.page == "chat":
        chat_interface()
    elif st.session_state.page == "news":
        news_interface()
    elif st.session_state.page == "tips":
        tips_interface()
    elif st.session_state.page == "news_detail":
        news_detail_interface()

if __name__ == "__main__":
    main()