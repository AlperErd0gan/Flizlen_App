#!/usr/bin/env python3
"""
Test script to list available Gemini models
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY not found in environment variables")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

print("=" * 60)
print("Available Gemini Models")
print("=" * 60)

try:
    models = genai.list_models()
    
    print("\n📋 All available models:")
    for model in models:
        print(f"  - {model.name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"    Methods: {', '.join(model.supported_generation_methods)}")
    
    print("\n✅ Models that support generateContent:")
    generate_content_models = [
        m for m in models 
        if 'generateContent' in m.supported_generation_methods
    ]
    
    for model in generate_content_models:
        print(f"  ✓ {model.name}")
    
    if generate_content_models:
        print(f"\n💡 Recommended model: {generate_content_models[0].name}")
        print(f"   Try using: '{generate_content_models[0].name.split('/')[-1]}'")
    
except Exception as e:
    print(f"❌ Error listing models: {e}")

print("\n" + "=" * 60)

