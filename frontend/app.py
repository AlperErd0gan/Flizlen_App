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
        color: #2F3E2E;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #4A6741 !important;
        font-family: 'Helvetica Neue', sans-serif;
    }

    /* Custom Header */
    .main-header {
        font-size: 3.5rem;
        font-weight: bold;
        color: #4A6741;
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
        background-color: #4A6741;
        color: #F5F1E6;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #2F3E2E;
        color: #FFFFFF;
        border-color: #2F3E2E;
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
        background-color: #4A6741;
    }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        padding: 1rem;
        border-radius: 10px;
    }
    /* User Message Style (Green) */
    [data-testid="stChatMessage"][data-testid="user"] [data-testid="stMarkdownContainer"] {
        background-color: #D6E8D6; /* Very light green */
        color: #1a1a1a;
        border-left: 5px solid #4A6741;
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
        color: #2F3E2E;
    }
    .news-date {
        color: #888;
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
    }
    .news-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #4A6741;
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

def go_to_landing():
    st.session_state.page = "landing"

def go_to_chat():
    st.session_state.page = "chat"

def go_to_news():
    st.session_state.page = "news"

# --- Views ---

def landing_page():
    st.markdown('<div class="main-header">🌿 Flizlen</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your intelligent companion for insights and news</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Create a container for the navigation buttons
        c1, c2 = st.columns(2, gap="large")
        
        with c1:
            st.markdown("""
            <div style="text-align: center; padding: 20px; background: white; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 10px;">
                <h3 style="margin:0;">💬 Chat</h3>
                <p style="color: #666;">Interact with the AI assistant</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Chat", use_container_width=True):
                go_to_chat()
                st.rerun()

        with c2:
            st.markdown("""
            <div style="text-align: center; padding: 20px; background: white; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 10px;">
                <h3 style="margin:0;">📰 News</h3>
                <p style="color: #666;">Latest updates and headlines</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Read News", use_container_width=True):
                go_to_news()
                st.rerun()

def chat_interface():
    # Top Navigation Bar
    col_nav1, col_nav2 = st.columns([1, 5])
    with col_nav1:
        if st.button("← Home"):
            go_to_landing()
            st.rerun()
    with col_nav2:
        st.markdown("## 💬 Intelligent Chat")

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
    col_nav1, col_nav2 = st.columns([1, 5])
    with col_nav1:
        if st.button("← Home"):
            go_to_landing()
            st.rerun()
    with col_nav2:
        st.markdown("## 📰 Latest News")

    # Mock Data for News (You can replace this with a backend call later)
    news_items = [
        {
            "title": "Global Markets Rally Amid Tech Surge",
            "date": datetime.date.today().strftime("%B %d, %Y"),
            "summary": "Technology stocks led a broad market rally today as investors reacted positively to new AI developments and earnings reports."
        },
        {
            "title": "Sustainable Energy Breakthrough",
            "date": (datetime.date.today() - datetime.timedelta(days=1)).strftime("%B %d, %Y"),
            "summary": "Researchers have discovered a new method to increase the efficiency of solar panels using organic materials."
        },
        {
            "title": "New Features Coming to Flizlen",
            "date": (datetime.date.today() - datetime.timedelta(days=2)).strftime("%B %d, %Y"),
            "summary": "The development team has announced a roadmap including voice integration and document analysis capabilities."
        }
    ]

    # Display News Cards
    for item in news_items:
        st.markdown(f"""
        <div class="news-card">
            <div class="news-date">{item['date']}</div>
            <div class="news-title">{item['title']}</div>
            <div>{item['summary']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.info("End of news feed.")

# --- Main Controller ---
def main():
    if st.session_state.page == "landing":
        landing_page()
    elif st.session_state.page == "chat":
        chat_interface()
    elif st.session_state.page == "news":
        news_interface()

if __name__ == "__main__":
    main()