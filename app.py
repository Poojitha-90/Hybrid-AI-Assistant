# app.py - COMPLETE HYBRID AI ASSISTANT WITH FIXED VOICE OUTPUT (READS ENTIRE MESSAGE)
import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
import sqlite3
import smtplib
import os
import re
import time
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import pandas as pd
import PyPDF2
import docx
from PIL import Image
import io
import uuid
from streamlit_mic_recorder import speech_to_text
import base64
import urllib.parse
import threading
import queue

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Hybrid AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS (keeping compact for space - same as your original)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        font-family: 'Inter', sans-serif;
    }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #fafcff 100%);
        border-right: 1px solid rgba(203, 213, 225, 0.3);
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.02);
    }
    
    section[data-testid="stSidebar"] > div {
        padding: 2rem 1.5rem;
        background: transparent;
    }
    
    .sidebar-header {
        text-align: center;
        margin-bottom: 2rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid #eef2f6;
    }
    
    .sidebar-logo {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        width: 70px;
        height: 70px;
        border-radius: 22px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem;
        box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.3);
    }
    
    .sidebar-logo span {
        color: white;
        font-size: 2.2rem;
    }
    
    .sidebar-title {
        color: #1e293b;
        font-size: 1.4rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 0.5rem 0 0.2rem;
    }
    
    .sidebar-subtitle {
        color: #64748b;
        font-size: 0.85rem;
        font-weight: 400;
    }
    
    .sidebar-card {
        background: white;
        border-radius: 20px;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        border: 1px solid #eef2f6;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
        transition: all 0.2s ease;
    }
    
    .sidebar-card:hover {
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.04);
        border-color: #d9e2ef;
    }
    
    .sidebar-card-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #f1f5f9;
    }
    
    .sidebar-card-header span:first-child {
        font-size: 1.3rem;
    }
    
    .sidebar-card-header h3 {
        font-size: 0.95rem;
        font-weight: 600;
        color: #334155;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    
    .account-info {
        background: #f8fafc;
        border-radius: 16px;
        padding: 1rem;
        border: 1px solid #eef2f6;
    }
    
    .account-email {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 0.8rem;
    }
    
    .account-email .email-icon {
        width: 38px;
        height: 38px;
        background: linear-gradient(135deg, #e0e7ff, #dbeafe);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #4f46e5;
        font-size: 1.2rem;
    }
    
    .account-email .email-text {
        font-weight: 500;
        color: #1e293b;
        font-size: 0.9rem;
        word-break: break-all;
    }
    
    .verified-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: #dcfce7;
        color: #166534;
        padding: 0.3rem 0.8rem;
        border-radius: 30px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .chat-history-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #f8fafc;
        border-radius: 14px;
        padding: 0.6rem 0.8rem 0.6rem 1rem;
        margin: 0.4rem 0;
        transition: all 0.2s ease;
        border: 1px solid transparent;
    }
    
    .chat-history-item:hover {
        background: white;
        border-color: #e2e8f0;
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    }
    
    .chat-title {
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
        flex: 1;
    }
    
    .chat-bullet {
        width: 8px;
        height: 8px;
        background: #94a3b8;
        border-radius: 50%;
        transition: all 0.2s ease;
    }
    
    .chat-history-item:hover .chat-bullet {
        background: #6366f1;
    }
    
    .chat-name {
        color: #334155;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .chat-delete {
        color: #94a3b8;
        background: transparent;
        border: none;
        padding: 0.2rem 0.5rem;
        border-radius: 8px;
        cursor: pointer;
        font-size: 1rem;
        transition: all 0.2s ease;
    }
    
    .chat-delete:hover {
        color: #ef4444;
        background: #fee2e2;
    }
    
    .reminder-item {
        background: #f8fafc;
        border-radius: 14px;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #f97316;
        transition: all 0.2s ease;
    }
    
    .reminder-item:hover {
        background: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
        transform: translateX(3px);
    }
    
    .reminder-text {
        font-weight: 500;
        color: #2d3a4f;
        font-size: 0.9rem;
        margin-bottom: 0.3rem;
    }
    
    .reminder-time {
        font-size: 0.75rem;
        color: #f97316;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .guide-item {
        background: #f8fafc;
        border-radius: 14px;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
        color: #475569;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .guide-icon {
        width: 32px;
        height: 32px;
        background: #e0e7ff;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #4f46e5;
        font-size: 1.1rem;
    }
    
    .main-header {
        background: white;
        padding: 1.5rem 2rem;
        border-radius: 24px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.02);
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.8);
    }
    
    .main-header h1 {
        margin: 0;
        color: #1a2639;
        font-weight: 700;
        font-size: 2.2rem;
        letter-spacing: -0.02em;
    }
    
    .main-header p {
        margin: 0.5rem 0 0;
        color: #5a6a7e;
        font-size: 1rem;
        font-weight: 400;
    }
    
    .input-container {
        display: flex;
        align-items: center;
        gap: 12px;
        background: white;
        border-radius: 50px;
        padding: 6px 8px 6px 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid #eef2f6;
        margin: 1.5rem 0;
    }
    
    .input-action-btn {
        background: #f8fafc !important;
        border: 1px solid #eef2f6 !important;
        border-radius: 40px !important;
        width: 45px !important;
        height: 45px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.3rem !important;
        color: #4f5b66 !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
        min-width: 45px !important;
        flex-shrink: 0 !important;
    }
    
    .input-text-field {
        flex: 1 !important;
        min-width: 0 !important;
    }
    
    .input-text-field .stTextInput {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .input-text-field .stTextInput > div {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .input-text-field input {
        border: none !important;
        background: transparent !important;
        padding: 12px 0 !important;
        font-size: 1rem !important;
        font-family: 'Inter', sans-serif !important;
        color: #1a2639 !important;
        box-shadow: none !important;
    }
    
    .input-text-field input::placeholder {
        color: #9aa8b9 !important;
    }
    
    .input-send-btn {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        border: none !important;
        border-radius: 40px !important;
        padding: 0 28px !important;
        height: 45px !important;
        color: white !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 8px 18px rgba(99, 102, 241, 0.3) !important;
        white-space: nowrap !important;
        flex-shrink: 0 !important;
    }
    
    .input-send-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 25px rgba(99, 102, 241, 0.4) !important;
    }
    
    .chat-message {
        padding: 1.2rem 1.5rem;
        margin: 0.5rem 0;
        border-radius: 18px;
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
        animation: fadeIn 0.3s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: white;
        border: 1px solid #eef2f6;
        color: #1a2639;
        margin-left: 20%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    }
    
    .assistant-message {
        background: #f8fafd;
        border: 1px solid #eef2f6;
        color: #1a2639;
        margin-right: 20%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    }
    
    .message-role {
        font-weight: 600;
        margin-bottom: 0.3rem;
        color: #4f5b66;
        font-size: 0.9rem;
    }
    
    .message-time {
        font-size: 0.7rem;
        color: #9aa8b9;
        margin-top: 0.5rem;
        text-align: right;
    }
    
    .file-chip {
        background: #f1f5f9;
        border-radius: 30px;
        padding: 0.5rem 1rem 0.5rem 1.5rem;
        display: inline-flex;
        align-items: center;
        gap: 10px;
        font-size: 0.9rem;
        color: #334155;
        border: 1px solid #e2e8f0;
        margin: 0.5rem 0;
    }
    
    .reminder-card {
        background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 6px solid #3b82f6;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.1);
    }
    
    .sent-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-radius: 16px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        border-left: 6px solid #22c55e;
        color: #166534;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .generated-image {
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        max-width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state (same as your original)
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hello! I'm your Hybrid AI Assistant. I can answer questions, remember events, and send you reminders via Email. How can I help you today?"}
    ]

if 'user_email' not in st.session_state:
    st.session_state.user_email = None

if 'user_phone' not in st.session_state:
    st.session_state.user_phone = None

if 'whatsapp_enabled' not in st.session_state:
    st.session_state.whatsapp_enabled = False

if 'last_check' not in st.session_state:
    st.session_state.last_check = datetime.now()

if 'processing' not in st.session_state:
    st.session_state.processing = False

if 'input_key' not in st.session_state:
    st.session_state.input_key = 0

if 'show_upload' not in st.session_state:
    st.session_state.show_upload = False

if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None

if 'upload_type' not in st.session_state:
    st.session_state.upload_type = None

if 'chat_sessions' not in st.session_state:
    st.session_state.chat_sessions = {}

if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())

if 'chat_titles' not in st.session_state:
    st.session_state.chat_titles = {}

if 'voice_processing' not in st.session_state:
    st.session_state.voice_processing = False

if 'active_mode' not in st.session_state:
    st.session_state.active_mode = "standard"

if 'memory_context' not in st.session_state:
    st.session_state.memory_context = {}

if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None

if 'pending_voice_message' not in st.session_state:
    st.session_state.pending_voice_message = None

# Database functions
def init_database():
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            event_text TEXT,
            event_datetime TEXT,
            is_sent INTEGER DEFAULT 0,
            sent_via TEXT DEFAULT '',
            created_at TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            user_email TEXT,
            title TEXT,
            messages TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            memory_key TEXT,
            memory_value TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            user_email TEXT PRIMARY KEY,
            phone_number TEXT,
            whatsapp_enabled INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def update_database_schema():
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    
    c.execute("PRAGMA table_info(reminders)")
    columns = [column[1] for column in c.fetchall()]
    
    if 'sent_via' not in columns:
        c.execute('ALTER TABLE reminders ADD COLUMN sent_via TEXT DEFAULT ""')
    
    conn.commit()
    conn.close()

init_database()
update_database_schema()

def delete_past_reminders():
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute('DELETE FROM reminders WHERE event_datetime < ?', (now,))
    conn.commit()
    conn.close()

def delete_reminder(reminder_id):
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
    conn.commit()
    conn.close()

def load_user_settings(user_email):
    if not user_email:
        return
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('SELECT phone_number, whatsapp_enabled FROM user_settings WHERE user_email = ?', (user_email,))
    result = c.fetchone()
    conn.close()
    if result:
        st.session_state.user_phone = result[0]
        st.session_state.whatsapp_enabled = bool(result[1])

def save_user_settings(user_email, phone_number, whatsapp_enabled):
    if not user_email:
        return
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO user_settings (user_email, phone_number, whatsapp_enabled)
        VALUES (?, ?, ?)
    ''', (user_email, phone_number, 1 if whatsapp_enabled else 0))
    conn.commit()
    conn.close()

def load_chat_history(user_email):
    if not user_email:
        return
    
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('''
        SELECT chat_id, title, messages, updated_at 
        FROM chat_history 
        WHERE user_email = ? 
        ORDER BY updated_at DESC
    ''', (user_email,))
    
    chats = c.fetchall()
    conn.close()
    
    for chat_id, title, messages_json, updated_at in chats:
        if chat_id not in st.session_state.chat_sessions:
            st.session_state.chat_sessions[chat_id] = json.loads(messages_json)
            st.session_state.chat_titles[chat_id] = title

def load_user_memory(user_email):
    if not user_email:
        return
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('SELECT memory_key, memory_value FROM user_memory WHERE user_email = ?', (user_email,))
    memories = c.fetchall()
    conn.close()
    for key, value in memories:
        st.session_state.memory_context[key] = value

def save_user_memory(user_email, key, value):
    if not user_email:
        return
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO user_memory (user_email, memory_key, memory_value, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_email, key, value, now, now))
    conn.commit()
    conn.close()
    st.session_state.memory_context[key] = value

def save_current_chat():
    if not st.session_state.user_email or not st.session_state.current_chat_id:
        return
    
    if st.session_state.current_chat_id not in st.session_state.chat_titles:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                title = msg["content"][:30] + "..." if len(msg["content"]) > 30 else msg["content"]
                st.session_state.chat_titles[st.session_state.current_chat_id] = title
                break
        else:
            st.session_state.chat_titles[st.session_state.current_chat_id] = "New Chat"
    
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    
    c.execute('SELECT chat_id FROM chat_history WHERE chat_id = ?', (st.session_state.current_chat_id,))
    exists = c.fetchone()
    
    messages_json = json.dumps(st.session_state.messages)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if exists:
        c.execute('''
            UPDATE chat_history 
            SET messages = ?, updated_at = ? 
            WHERE chat_id = ?
        ''', (messages_json, now, st.session_state.current_chat_id))
    else:
        c.execute('''
            INSERT INTO chat_history (chat_id, user_email, title, messages, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (st.session_state.current_chat_id, st.session_state.user_email, 
              st.session_state.chat_titles[st.session_state.current_chat_id], 
              messages_json, now, now))
    
    conn.commit()
    conn.close()

def new_chat():
    if st.session_state.messages and st.session_state.user_email:
        save_current_chat()
    
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hello! I'm your Hybrid AI Assistant. I can answer questions, remember events, and send you reminders via Email. How can I help you today?"}
    ]
    st.session_state.uploaded_file = None
    st.session_state.uploaded_file_name = None
    st.session_state.upload_type = None
    st.session_state.input_key += 1
    st.rerun()

def load_chat(chat_id):
    if chat_id in st.session_state.chat_sessions:
        if st.session_state.messages and st.session_state.user_email:
            save_current_chat()
        
        st.session_state.current_chat_id = chat_id
        st.session_state.messages = st.session_state.chat_sessions[chat_id]
        st.session_state.uploaded_file = None
        st.session_state.uploaded_file_name = None
        st.session_state.upload_type = None
        st.session_state.input_key += 1
        st.rerun()

def delete_chat(chat_id):
    if chat_id in st.session_state.chat_sessions:
        del st.session_state.chat_sessions[chat_id]
        del st.session_state.chat_titles[chat_id]
        
        conn = sqlite3.connect('reminders.db')
        c = conn.cursor()
        c.execute('DELETE FROM chat_history WHERE chat_id = ?', (chat_id,))
        conn.commit()
        conn.close()
        
        if st.session_state.current_chat_id == chat_id:
            new_chat()
        else:
            st.rerun()

def export_current_chat(format_type):
    messages = st.session_state.messages
    title = st.session_state.chat_titles.get(st.session_state.current_chat_id, "Chat Export")
    
    export_content = f"# {title}\n\n"
    export_content += f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    export_content += "=" * 50 + "\n\n"
    
    for msg in messages:
        role = msg["role"].upper()
        content = msg["content"]
        export_content += f"**{role}**:\n{content}\n\n"
        export_content += "-" * 30 + "\n\n"
    
    if format_type == "txt":
        return export_content.encode('utf-8')
    elif format_type == "json":
        return json.dumps({"title": title, "messages": messages, "export_date": str(datetime.now())}, indent=2).encode('utf-8')
    return None

def generate_image(prompt):
    """Generate image using Gemini"""
    try:
        image_prompt = f"Generate a detailed, high-quality image of: {prompt}. Make it visually appealing and professional."
        
        response = model.generate_content(
            image_prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
        )
        
        if hasattr(response, 'candidates') and response.candidates:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data'):
                    return part.inline_data.data
        return None
    except Exception as e:
        print(f"Image generation error: {e}")
        return None

# ===== FIXED: Text to speech - READS THE ENTIRE MESSAGE WITHOUT CUTTING OFF =====
def text_to_speech(text):
    """Convert text to speech using browser's Web Speech API - READS FULL TEXT"""
    try:
        # Clean the text (remove HTML tags and special characters)
        clean_text = re.sub(r'<[^>]+>', '', text)
        clean_text = re.sub(r'\[.*?\]', '', clean_text)
        clean_text = re.sub(r'[*_#]', '', clean_text)
        
        # Remove any emojis that might cause issues
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        clean_text = emoji_pattern.sub(r'', clean_text)
        
        # Remove any remaining special characters
        clean_text = re.sub(r'[^\w\s\.,!?\'"-]', '', clean_text)
        clean_text = clean_text.strip()
        
        if not clean_text:
            return False
        
        # Escape backticks and quotes for JavaScript
        clean_text = clean_text.replace('`', '\\`').replace('${', '\\${')
        
        # Create JavaScript to speak the entire text with better handling
        speech_script = f"""
        <script>
            // Cancel any ongoing speech
            window.speechSynthesis.cancel();
            
            const fullText = `{clean_text}`;
            
            // Function to split text into manageable chunks
            function splitIntoChunks(text, maxLength = 200) {{
                const sentences = text.split(/(?<=[.!?])\\s+/);
                const chunks = [];
                let currentChunk = "";
                
                for (let sentence of sentences) {{
                    if ((currentChunk + sentence).length <= maxLength) {{
                        currentChunk += (currentChunk ? " " : "") + sentence;
                    }} else {{
                        if (currentChunk) chunks.push(currentChunk);
                        currentChunk = sentence;
                    }}
                }}
                if (currentChunk) chunks.push(currentChunk);
                return chunks;
            }}
            
            // Split the text into chunks
            const chunks = splitIntoChunks(fullText);
            let currentIndex = 0;
            
            // Function to speak each chunk
            function speakNext() {{
                if (currentIndex >= chunks.length) return;
                
                const utterance = new SpeechSynthesisUtterance(chunks[currentIndex]);
                utterance.rate = 0.85;
                utterance.pitch = 1;
                utterance.volume = 1;
                utterance.lang = 'en-US';
                
                utterance.onend = function() {{
                    currentIndex++;
                    // Small delay between chunks for better flow
                    setTimeout(speakNext, 100);
                }};
                
                utterance.onerror = function(event) {{
                    console.error('Speech error:', event);
                    // Continue with next chunk on error
                    currentIndex++;
                    speakNext();
                }};
                
                window.speechSynthesis.speak(utterance);
            }}
            
            // Start speaking after a small delay
            setTimeout(speakNext, 200);
        </script>
        """
        st.components.v1.html(speech_script, height=0)
        return True
    except Exception as e:
        print(f"Text to speech error: {e}")
        return False

def call_ai_with_backoff(model, prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            return model.generate_content(prompt)
        except Exception as e:
            if "Quota exceeded" in str(e) or "429" in str(e):
                wait_match = re.search(r'retry in (\d+\.?\d*)s', str(e))
                wait_seconds = float(wait_match.group(1)) if wait_match else (2 ** attempt) * 5
                time.sleep(wait_seconds + 1)
            else:
                raise e
    return None

@st.cache_resource
def init_ai():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        st.error("❌ Please set GEMINI_API_KEY in .env file")
        st.stop()
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

model = init_ai()

def send_reminder_email(to_email, event_text, event_time):
    try:
        sender_email = os.getenv('EMAIL')
        sender_password = os.getenv('EMAIL_PASSWORD')
        
        if not sender_email or not sender_password:
            return False
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = f"🔔 Reminder: {event_text}"
        
        body = f"""
        <html>
            <body style="font-family: 'Inter', sans-serif; padding: 20px;">
                <div style="max-width: 500px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); padding: 30px; border-radius: 20px; color: white;">
                        <h1 style="margin:0;">⏰ Time Reminder</h1>
                    </div>
                    <div style="background: white; padding: 30px; border-radius: 15px; margin-top: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                        <div style="font-size: 1.3rem; font-weight: 600; color: #1a2639;">{event_text}</div>
                        <div style="color: #6366f1; margin-top: 10px;">⏰ {event_time}</div>
                        <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #eef2f6; color: #64748b; font-size: 0.9rem;">
                            Sent from Hybrid AI Assistant
                        </div>
                    </div>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def check_and_send_reminders():
    """Check and send due reminders"""
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M")
    two_min_ago = (now - timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M")
    
    c.execute('''
        SELECT id, user_email, event_text, event_datetime 
        FROM reminders 
        WHERE event_datetime BETWEEN ? AND ? AND is_sent = 0
    ''', (two_min_ago, current_time))
    
    due = c.fetchall()
    conn.close()
    
    sent_count = 0
    reminder_messages = []
    
    for reminder in due:
        id, email, event, dt = reminder
        sent_via = []
        
        # Send email
        if send_reminder_email(email, event, dt):
            sent_via.append("Email")
        
        if sent_via:
            conn = sqlite3.connect('reminders.db')
            c = conn.cursor()
            c.execute('UPDATE reminders SET is_sent = 1, sent_via = ? WHERE id = ?', 
                     (",".join(sent_via), id))
            conn.commit()
            conn.close()
            sent_count += 1
            reminder_messages.append(f"🔔 Reminder: {event} at {dt}")
    
    # Play voice for reminders
    if reminder_messages:
        reminder_text = "Reminder! " + ". ".join(reminder_messages)
        text_to_speech(reminder_text)
    
    return sent_count

def extract_text_from_file(uploaded_file, file_type):
    try:
        if file_type == "PDF":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text[:2000]
        elif file_type == "Word":
            doc = docx.Document(uploaded_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text[:2000]
        elif file_type == "Text":
            return uploaded_file.getvalue().decode("utf-8")[:2000]
        elif file_type == "Excel":
            df = pd.read_excel(uploaded_file)
            return df.to_string()[:2000]
        elif file_type == "CSV":
            df = pd.read_csv(uploaded_file)
            return df.to_string()[:2000]
        else:
            return "File content extracted"
    except:
        return "Could not extract text from file"

def process_file_with_ai(file_content, file_name, file_type, is_image=False):
    try:
        if is_image:
            img = Image.open(io.BytesIO(file_content))
            prompt = "Describe this image in 2-3 sentences."
            response = model.generate_content([prompt, img])
            return response.text if response else "Image uploaded"
        else:
            prompt = f"Summarize this {file_type} file '{file_name}' in 2-3 sentences:\n\n{file_content}"
            response = call_ai_with_backoff(model, prompt)
            return response.text if response else "File uploaded"
    except:
        return "File uploaded"

def process_message_with_ai(user_message):
    if not st.session_state.user_email:
        return "⚠️ Please enter your email in the sidebar first!"
    
    current_time = datetime.now()
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M")
    
    # Check for image generation request
    image_keywords = ["generate image", "create image", "draw", "make a picture", "generate a picture"]
    is_image_request = any(keyword in user_message.lower() for keyword in image_keywords)
    
    if is_image_request:
        image_prompt = user_message
        for keyword in image_keywords:
            image_prompt = image_prompt.lower().replace(keyword, "").strip()
        
        with st.spinner("🎨 Generating image..."):
            image_data = generate_image(image_prompt)
            
            if image_data:
                st.session_state.generated_image = image_data
                img = Image.open(io.BytesIO(image_data))
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                return f"""
                <div>
                    <p>Here's the image I generated for: <strong>{image_prompt}</strong></p>
                    <img src="data:image/png;base64,{img_str}" style="max-width: 100%; border-radius: 16px; margin: 1rem 0;">
                    <div style="margin-top: 1rem;">
                        <button onclick="downloadImage()" style="background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; border: none; padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer;">📥 Download Image</button>
                    </div>
                    <script>
                        function downloadImage() {{
                            const link = document.createElement('a');
                            link.href = 'data:image/png;base64,{img_str}';
                            link.download = 'generated_image.png';
                            link.click();
                        }}
                    </script>
                </div>
                """
            else:
                return "I couldn't generate an image right now. Please try again with a different prompt."
    
    # Load memory context
    memory_context_str = ""
    if st.session_state.memory_context:
        memory_context_str = "Information I remember about you:\n"
        for key, value in st.session_state.memory_context.items():
            memory_context_str += f"- {key}: {value}\n"
    
    # Build conversation history
    conversation_history = ""
    recent_messages = st.session_state.messages[-8:] if len(st.session_state.messages) > 8 else st.session_state.messages
    
    for msg in recent_messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        content = msg['content'][:500] if len(msg['content']) > 500 else msg['content']
        conversation_history += f"{role}: {content}\n\n"
    
    # Process uploaded file
    file_context = ""
    if st.session_state.uploaded_file:
        if st.session_state.uploaded_file.type.startswith('image'):
            file_content = st.session_state.uploaded_file.getvalue()
            file_summary = process_file_with_ai(file_content, st.session_state.uploaded_file_name, "Image", is_image=True)
            file_context = f"\n[Uploaded Photo: {st.session_state.uploaded_file_name}]\nSummary: {file_summary}\n"
        else:
            file_ext = st.session_state.uploaded_file_name.split('.')[-1].lower()
            file_type_map = {'pdf':'PDF','docx':'Word','txt':'Text','xlsx':'Excel','csv':'CSV'}
            file_type = file_type_map.get(file_ext, 'Document')
            file_content = extract_text_from_file(st.session_state.uploaded_file, file_type)
            file_summary = process_file_with_ai(file_content, st.session_state.uploaded_file_name, file_type)
            file_context = f"\n[Uploaded File: {st.session_state.uploaded_file_name}]\nSummary: {file_summary}\n"
    
    # Mode-specific instruction
    mode_instruction = {
        "standard": "Provide balanced, natural responses.",
        "creative": "Be creative, use metaphors, and provide imaginative responses.",
        "concise": "Be very concise. Keep responses short and to the point.",
        "detailed": "Provide detailed, comprehensive responses with thorough explanations."
    }.get(st.session_state.active_mode, "Provide balanced, natural responses.")
    
    ai_prompt = f"""
    Current time: {current_time_str}
    {file_context}
    {memory_context_str}
    
    Mode: {st.session_state.active_mode.upper()}
    Instruction: {mode_instruction}
    
    CONVERSATION HISTORY:
    {conversation_history}
    
    Current user message: {user_message}
    
    IMPORTANT: This is a CONTINUING conversation. Use the history to maintain context.
    
    If user mentions a future event, add:
    [REMINDER]description|YYYY-MM-DD HH:MM[/REMINDER]
    
    If user shares personal information (name, preferences, important facts), remember by adding:
    [MEMORY]key|value[/MEMORY]
    """
    
    response = call_ai_with_backoff(model, ai_prompt)
    if response:
        response_text = response.text
        
        # Handle memory storage
        memory_match = re.search(r'\[MEMORY\](.*?)\|(.*?)\[/MEMORY\]', response_text)
        if memory_match:
            key = memory_match.group(1).strip()
            value = memory_match.group(2).strip()
            save_user_memory(st.session_state.user_email, key, value)
            response_text = re.sub(r'\[MEMORY\].*?\[/MEMORY\]', '', response_text)
            response_text += f"\n\n💡 I've remembered that."
        
        # Handle reminders
        reminder_match = re.search(r'\[REMINDER\](.*?)\|(.*?)\[/REMINDER\]', response_text)
        if reminder_match:
            event = reminder_match.group(1).strip()
            event_time = reminder_match.group(2).strip()
            
            conn = sqlite3.connect('reminders.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO reminders (user_email, event_text, event_datetime, created_at)
                VALUES (?, ?, ?, ?)
            ''', (st.session_state.user_email, event, event_time, current_time_str))
            conn.commit()
            conn.close()
            
            response_text = re.sub(r'\[REMINDER\].*?\[/REMINDER\]', '', response_text)
            
            reminder_html = f"""
            <div class="reminder-card">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div style="width: 32px; height: 32px; background: #3b82f6; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; margin-right: 12px;">✓</div>
                    <div style="font-weight: 600; color: #1e293b;">Reminder Saved</div>
                </div>
                <div style="font-weight: 500; color: #0f172a; margin-left: 44px; margin-bottom: 0.5rem;">📌 {event}</div>
                <div style="color: #3b82f6; margin-left: 44px;">⏰ {event_time}</div>
                <div style="margin-top: 10px; margin-left: 44px; font-size: 0.85rem; color: #64748b;">
                    📧 Email will be sent at reminder time
                </div>
            </div>
            """
            response_text = response_text + "<br>" + reminder_html
            
            # Check if reminder is immediate
            if event_time <= current_time_str:
                sent_via = []
                
                # Send email
                if send_reminder_email(st.session_state.user_email, event, event_time):
                    sent_via.append("Email")
                
                if sent_via:
                    response_text += f'<br><div class="sent-card"><span>📢</span><span>Sent via: {", ".join(sent_via)}!</span></div>'
                    # Play voice for immediate reminder
                    reminder_voice_text = f"Reminder! {event} at {event_time}"
                    text_to_speech(reminder_voice_text)
        
        # ===== FIXED: Voice output for voice input - READS THE ENTIRE TEXT =====
        if st.session_state.voice_processing:
            # Clean the text for voice
            clean_text = re.sub(r'<[^>]+>', '', response_text)
            clean_text = re.sub(r'\[.*?\]', '', clean_text)
            clean_text = re.sub(r'[*_#]', '', clean_text)
            clean_text = clean_text.strip()
            
            if clean_text:
                # Read the ENTIRE text (no character limit)
                text_to_speech(clean_text)
        
        return response_text
    
    return "Sorry, I couldn't process that request."

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-logo"><span>🤖</span></div>
        <div class="sidebar-title">Hybrid AI</div>
        <div class="sidebar-subtitle">Smart Assistant with Reminders</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Account Section
    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-card-header"><span>📧</span><h3>Account</h3></div>', unsafe_allow_html=True)
    
    if not st.session_state.user_email:
        email = st.text_input("Email", placeholder="your@email.com", key="email_input", label_visibility="collapsed")
        if st.button("Save Email", use_container_width=True) and email:
            if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                st.session_state.user_email = email
                load_user_settings(email)
                load_chat_history(email)
                load_user_memory(email)
                st.rerun()
    else:
        st.markdown(f"""
        <div class="account-info">
            <div class="account-email">
                <div class="email-icon">📧</div>
                <div class="email-text">{st.session_state.user_email}</div>
            </div>
            <span class="verified-badge">✓ Verified</span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Change Email", use_container_width=True):
            st.session_state.user_email = None
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat History
    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-card-header"><span>💬</span><h3>Chat History</h3></div>', unsafe_allow_html=True)
    
    col_new, col_export = st.columns([7, 5])
    with col_new:
        if st.button("➕ New Chat", use_container_width=True):
            new_chat()
    with col_export:
        if st.button("📤 Export", use_container_width=True):
            export_data = export_current_chat("txt")
            if export_data:
                st.download_button("⬇️", data=export_data, file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", use_container_width=True)
    
    if st.session_state.user_email:
        if not st.session_state.chat_sessions:
            load_chat_history(st.session_state.user_email)
        
        for chat_id, title in list(st.session_state.chat_titles.items()):
            col1, col2 = st.columns([12, 5])
            with col1:
                if st.button(f"💬 {title[:25]}", key=f"chat_{chat_id}", use_container_width=True):
                    load_chat(chat_id)
            with col2:
                if st.button("🗑️", key=f"delete_{chat_id}"):
                    delete_chat(chat_id)
    else:
        st.info("Enter email to see history")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Pending Reminders Section
    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-card-header"><span>⏰</span><h3>Pending Reminders</h3></div>', unsafe_allow_html=True)
    
    if st.session_state.user_email:
        delete_past_reminders()
        
        conn = sqlite3.connect('reminders.db')
        c = conn.cursor()
        c.execute('''
            SELECT id, event_text, event_datetime 
            FROM reminders 
            WHERE user_email = ? AND is_sent = 0 AND event_datetime >= ?
            ORDER BY event_datetime
        ''', (st.session_state.user_email, datetime.now().strftime("%Y-%m-%d %H:%M")))
        reminders = c.fetchall()
        conn.close()
        
        if reminders:
            for reminder_id, event_text, event_time in reminders:
                st.markdown(f"""
                <div class="reminder-item">
                    <div class="reminder-text">📌 {event_text[:40]}</div>
                    <div class="reminder-time">⏰ {event_time}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_reminder_{reminder_id}"):
                    delete_reminder(reminder_id)
                    st.rerun()
        else:
            st.markdown("""
            <div style="text-align: center; padding: 1.5rem; color: #94a3b8; background: #f8fafc; border-radius: 12px;">
                <span style="font-size: 2rem; display: block; margin-bottom: 0.5rem;">✨</span>
                No pending reminders
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("⏰ Check Reminders Now", key="check_reminders", use_container_width=True):
            with st.spinner("Checking..."):
                count = check_and_send_reminders()
                if count > 0:
                    st.success(f"✅ Sent {count} reminder(s)!")
                else:
                    st.info("✨ No due reminders")
    else:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; color: #94a3b8; background: #f8fafc; border-radius: 12px;">
            <span style="font-size: 1.5rem; display: block; margin-bottom: 0.5rem;">🔒</span>
            Enter email to see reminders
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick Guide Section
    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-card-header">
        <span>📖</span>
        <h3>Quick Guide</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="guide-item">
        <div class="guide-icon">💬</div>
        <div>Ask any question - I'll answer</div>
    </div>
    <div class="guide-item">
        <div class="guide-icon">⏰</div>
        <div>Set reminders by mentioning events</div>
    </div>
    <div class="guide-item">
        <div class="guide-icon">🎤</div>
        <div>Click mic for voice input & FULL voice output</div>
    </div>
    <div class="guide-item">
        <div class="guide-icon">➕</div>
        <div>Click + to upload files/photos</div>
    </div>
    <div class="guide-item">
        <div class="guide-icon">📧</div>
        <div>Email reminders sent automatically</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ===== MAIN CONTENT =====
st.markdown("""
<div class="main-header">
    <h1>🤖 Hybrid AI Assistant</h1>
    <p>Your intelligent assistant • Voice input & FULL voice output • Email reminders • Image generation • File uploads</p>
</div>
""", unsafe_allow_html=True)

# Mode Selector
mode_col1, mode_col2, mode_col3, mode_col4 = st.columns(4)

with mode_col1:
    if st.button("⚖️ Standard", use_container_width=True, type="primary" if st.session_state.active_mode == "standard" else "secondary"):
        st.session_state.active_mode = "standard"
        st.rerun()
with mode_col2:
    if st.button("📝 Concise", use_container_width=True, type="primary" if st.session_state.active_mode == "concise" else "secondary"):
        st.session_state.active_mode = "concise"
        st.rerun()
with mode_col3:
    if st.button("🎨 Creative", use_container_width=True, type="primary" if st.session_state.active_mode == "creative" else "secondary"):
        st.session_state.active_mode = "creative"
        st.rerun()
with mode_col4:
    if st.button("🔬 Detailed", use_container_width=True, type="primary" if st.session_state.active_mode == "detailed" else "secondary"):
        st.session_state.active_mode = "detailed"
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Display messages
for msg in st.session_state.messages:
    message_class = "user-message" if msg["role"] == "user" else "assistant-message"
    st.markdown(f"""
    <div class="chat-message {message_class}">
        <div class="message-role">{msg["role"].title()}</div>
        <div>{msg['content']}</div>
        <div class="message-time">{datetime.now().strftime('%I:%M %p')}</div>
    </div>
    """, unsafe_allow_html=True)

# Show uploaded file
if st.session_state.uploaded_file_name:
    st.markdown(f"""
    <div class="file-chip">
        📎 {st.session_state.uploaded_file_name}
        <span onclick="removeFile()">✖️</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Remove File"):
        st.session_state.uploaded_file = None
        st.session_state.uploaded_file_name = None
        st.session_state.upload_type = None
        st.rerun()

# Input Area
st.markdown('<div class="input-container">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([1, 1, 12, 1.5])

with col1:
    if st.button("➕", key="plus_btn", help="Upload file or photo"):
        st.session_state.show_upload = True
        st.rerun()

with col2:
    recorded_text = speech_to_text(
        language='en', 
        start_prompt="🎙️", 
        stop_prompt="⏹️", 
        just_once=True, 
        key=f'speech_{st.session_state.input_key}',
        use_container_width=False
    )

with col3:
    user_input = st.text_input(
        "Message",
        placeholder="Type your message here...",
        label_visibility="collapsed",
        key=f"input_{st.session_state.input_key}",
    )

with col4:
    submitted = st.button("Send", key="send_btn", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# File upload
if st.session_state.show_upload:
    with st.popover("Upload"):
        if st.button("📄 File"):
            st.session_state.upload_type = "file"
            st.session_state.show_upload = False
            st.rerun()
        if st.button("📸 Photo"):
            st.session_state.upload_type = "photo"
            st.session_state.show_upload = False
            st.rerun()

if st.session_state.upload_type == "file":
    uploaded = st.file_uploader("Choose file", type=['pdf','docx','txt','xlsx','csv'], key="file_upload")
    if uploaded:
        st.session_state.uploaded_file = uploaded
        st.session_state.uploaded_file_name = uploaded.name
        st.session_state.upload_type = None
        st.rerun()
elif st.session_state.upload_type == "photo":
    uploaded = st.file_uploader("Choose photo", type=['png','jpg','jpeg','gif'], key="photo_upload")
    if uploaded:
        st.session_state.uploaded_file = uploaded
        st.session_state.uploaded_file_name = uploaded.name
        st.session_state.upload_type = None
        st.rerun()

# Process voice input
if recorded_text and not st.session_state.voice_processing and not st.session_state.processing:
    st.session_state.voice_processing = True
    display_msg = f"{recorded_text}" + (f"\n\n[Uploaded: {st.session_state.uploaded_file_name}]" if st.session_state.uploaded_file_name else "")
    st.session_state.messages.append({"role": "user", "content": display_msg})
    
    with st.spinner("Processing..."):
        response_text = process_message_with_ai(recorded_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        save_current_chat()
    
    st.session_state.uploaded_file = None
    st.session_state.uploaded_file_name = None
    st.session_state.upload_type = None
    st.session_state.voice_processing = False
    st.session_state.input_key += 1
    st.rerun()

# Process text input
if submitted and user_input and not st.session_state.processing:
    st.session_state.processing = True
    display_msg = f"{user_input}" + (f"\n\n[Uploaded: {st.session_state.uploaded_file_name}]" if st.session_state.uploaded_file_name else "")
    st.session_state.messages.append({"role": "user", "content": display_msg})
    
    if not st.session_state.user_email:
        st.session_state.messages.append({"role": "assistant", "content": "⚠️ Please enter your email in the sidebar!"})
    else:
        with st.spinner("Thinking..."):
            response_text = process_message_with_ai(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            save_current_chat()
    
    st.session_state.uploaded_file = None
    st.session_state.uploaded_file_name = None
    st.session_state.upload_type = None
    st.session_state.input_key += 1
    st.session_state.processing = False
    st.rerun()

# Auto-check reminders
if st.session_state.user_email:
    if (datetime.now() - st.session_state.last_check).seconds > 30:
        delete_past_reminders()
        check_and_send_reminders()
        st.session_state.last_check = datetime.now()
        st.rerun()