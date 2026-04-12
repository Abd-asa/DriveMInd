import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

import streamlit as st
from PIL import Image
from src.api_client import analyze_dashcam_frame

# ==========================================
# HELPER: RENDER STRUCTURED JSON
# ==========================================
def render_safety_report(data):
    if isinstance(data, dict) and "hazard_level" in data:
        level = str(data.get("hazard_level", "")).upper()
        if "HIGH" in level:
            st.error(f"🚨 **HAZARD LEVEL: HIGH**")
        elif "MEDIUM" in level:
            st.warning(f"⚠️ **HAZARD LEVEL: MEDIUM**")
        elif "LOW" in level:
            st.success(f"✅ **HAZARD LEVEL: LOW**")
        else:
            st.info(f"ℹ️ **HAZARD LEVEL: {level}**")
            
        hazards = data.get("hazards_detected", [])
        if hazards:
            st.write("**Identified Risks:**")
            cols = st.columns(len(hazards) if len(hazards) < 5 else 4)
            for i, hazard in enumerate(hazards):
                cols[i % len(cols)].button(hazard.title(), key=f"btn_{hazard}_{i}", disabled=True)
                
        st.write("**Analysis:**")
        st.markdown(data.get("analysis", "No analysis provided."))
    else:
        st.markdown(str(data))

# ==========================================
# NEW FEATURE: MODAL DIALOG FOR CHAT OPTIONS
# ==========================================
@st.dialog("Chat Options")
def manage_chat_dialog(chat_name, is_active):
    """Pops up a clean window in the center of the screen to manage the chat."""
    
    # 1. Rename Logic (Auto-saves on Enter!)
    st.markdown("**Rename Chat**")
    new_name = st.text_input(
        "Rename", 
        value=chat_name, 
        key=f"dialog_ren_{chat_name}", 
        label_visibility="collapsed",
        help="Type a new name and press Enter to save"
    )
    
    # If the user typed a new name and pressed enter
    if new_name and new_name != chat_name:
        if new_name not in st.session_state.chats:
            # Move data to new key
            st.session_state.chats[new_name] = st.session_state.chats.pop(chat_name)
            # Update pointer if renaming the active chat
            if is_active:
                st.session_state.current_chat = new_name
            st.rerun()
        else:
            st.error("⚠️ Name already exists!")

    st.divider()
    
    # 2. Delete Logic
    if st.button("🗑️ Delete Chat", type="primary", use_container_width=True):
        del st.session_state.chats[chat_name]
        if is_active:
            st.session_state.current_chat = "Landing"
        st.rerun()

# ==========================================
# 1. PAGE SETUP & CSS
# ==========================================
st.set_page_config(page_title="DriveMind Analyst", page_icon="🚗", layout="wide")

# Just tightening the gap between the buttons, no more messy CSS hacks!
st.markdown("""
    <style>
    [data-testid="stSidebar"] [data-testid="column"] {
        padding-left: 0px !important;
        padding-right: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. INITIALIZE MEMORY (START EMPTY)
# ==========================================
if "chats" not in st.session_state:
    st.session_state.chats = {}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Landing"
if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 0

# ==========================================
# 3. SIDEBAR (Navigation)
# ==========================================
with st.sidebar:
    st.title("🚗 DriveMind")
    
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        st.session_state.chat_counter += 1
        new_chat_name = f"Chat {st.session_state.chat_counter}"
        st.session_state.chats[new_chat_name] = []
        st.session_state.current_chat = new_chat_name
        st.rerun()
        
    st.divider()
    
    if st.session_state.chats:
        st.subheader("Chats")
    
    for chat_name in reversed(list(st.session_state.chats.keys())):
        is_active = (chat_name == st.session_state.current_chat)
        
        col_chat, col_menu = st.columns([0.88, 0.12])
        
        with col_chat:
            if st.button(chat_name, key=f"sel_{chat_name}", type="primary" if is_active else "secondary", use_container_width=True):
                st.session_state.current_chat = chat_name
                st.rerun()
                
        with col_menu:
            # --- ADD type="tertiary" HERE ---
            if st.button("⋮", key=f"menu_{chat_name}", help="Chat Options", type="tertiary", use_container_width=True):
                manage_chat_dialog(chat_name, is_active)

# ==========================================
# 4. MAIN DISPLAY (Landing Page OR Chat)
# ==========================================

# --- SCENARIO A: THE LANDING PAGE ---
if st.session_state.current_chat == "Landing":
    st.title("🚗 Welcome to DriveMind")
    st.markdown("### Your VLM Dashcam Analyst")
    st.info("👈 Please click **➕ New Chat** in the sidebar to begin a new safety analysis session.")
    
    st.divider()
    st.markdown("""
    **How to use this tool:**
    1. Click **New Chat** to create a secure session.
    2. Click the 📎 **paperclip icon** in the chat bar below to upload a dashcam frame.
    3. Ask the Agent to evaluate the scene for safety hazards.
    """)

# --- SCENARIO B: THE CHAT INTERFACE ---
else:
    st.header(f"Safety Analysis - {st.session_state.current_chat}")

    active_messages = st.session_state.chats.get(st.session_state.current_chat, [])
    for message in active_messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                if message.get("content"):
                    st.markdown(message["content"])
                if message.get("image"):
                    st.image(message["image"], width=250)
            elif message["role"] == "assistant":
                render_safety_report(message.get("data", message.get("content")))

    prompt = st.chat_input(
        "Ask a question and attach a dashcam frame...", 
        accept_file=True, 
        file_type=["jpg", "jpeg", "png"]
    )

    if prompt:
        user_text = prompt.text
        uploaded_files = prompt["files"] if "files" in prompt else []
        
        if not user_text and not uploaded_files:
            st.stop()
            
        new_user_message = {"role": "user", "content": user_text}
        
        image_obj = None
        if uploaded_files:
            image_obj = Image.open(uploaded_files[0])
            new_user_message["image"] = image_obj
            
        st.session_state.chats[st.session_state.current_chat].append(new_user_message)
        
        with st.chat_message("user"):
            if user_text:
                st.markdown(user_text)
            if image_obj:
                st.image(image_obj, width=250)
                
        with st.chat_message("assistant"):
            with st.spinner("Agent evaluating hazard parameters..."):
                
                image_to_analyze = image_obj
                if not image_to_analyze:
                    for msg in reversed(st.session_state.chats[st.session_state.current_chat]):
                        if msg.get("image"):
                            image_to_analyze = msg["image"]
                            break
                            
                if not image_to_analyze:
                    error_msg = "⚠️ Please attach an image using the paperclip icon in the chat bar first!"
                    st.warning(error_msg)
                    st.session_state.chats[st.session_state.current_chat].append({"role": "assistant", "content": error_msg})
                else:
                    structured_response = analyze_dashcam_frame(image_to_analyze, user_text or "Analyze this image for safety hazards.")
                    render_safety_report(structured_response)
                    st.session_state.chats[st.session_state.current_chat].append({
                        "role": "assistant", 
                        "data": structured_response 
                    })