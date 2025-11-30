"""
Streamlit Frontend for Flizlen App
User interface for interacting with the FastAPI backend and Gemini AI
"""

import streamlit as st
import requests
import os
from typing import List, Dict

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="Flizlen App",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 20%;
    }
    </style>
""", unsafe_allow_html=True)

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
    except requests.exceptions.HTTPError as e:
        # Try to get error details from response
        try:
            error_detail = response.json().get("detail", str(e))
            st.error(f"Backend error: {error_detail}")
        except:
            st.error(f"Error connecting to backend: {str(e)}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to backend: {str(e)}")
        return None

def main():
    # Header
    st.markdown('<div class="main-header">🚀 Flizlen App</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Backend URL input
        backend_url = st.text_input(
            "Backend URL",
            value=BACKEND_URL,
            help="URL of the FastAPI backend"
        )
        
        # Health check
        if st.button("Check Backend Status"):
            if check_backend_health():
                st.success("✅ Backend is running")
            else:
                st.error("❌ Backend is not accessible")
        
        st.divider()
        
        # Clear conversation button
        if st.button("🗑️ Clear Conversation"):
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        
        st.markdown("### 📖 About")
        st.markdown("""
        This app uses:
        - **FastAPI** for the backend
        - **Streamlit** for the frontend
        - **Google Gemini AI** for intelligent responses
        """)
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Main chat interface
    st.header("💬 Chat with AI")
    
    # Display conversation history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
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
            for msg in st.session_state.messages[:-1]  # Exclude current message
        ]
        
        # Show loading indicator
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Send request to backend
                response = send_chat_message(prompt, conversation_history)
                
                if response and response.get("status") == "success":
                    assistant_response = response.get("response", "No response received")
                    st.markdown(assistant_response)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_response
                    })
                else:
                    error_msg = "Sorry, I encountered an error. Please check your backend connection and API configuration."
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

if __name__ == "__main__":
    main()

