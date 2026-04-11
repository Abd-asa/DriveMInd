import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)


import streamlit as st
from PIL import Image
import time
from src.api_client import analyze_dashcam_frame

# ==========================================
# 1. PAGE SETUP
# ==========================================
st.set_page_config(page_title="DriveMind Analyst", page_icon="🚗", layout="wide")

# ==========================================
# 2. INITIALIZE MULTI-CHAT MEMORY
# ==========================================
# We now store a dictionary of chats. Keys are chat names, values are message lists.
if "chats" not in st.session_state:
    st.session_state.chats = {"Chat 1": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"
if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 1

# ==========================================
# 3. SIDEBAR (History Navigation)
# ==========================================
with st.sidebar:
    st.title("🚗 DriveMind")
    
    # Button to create a brand new chat thread
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        st.session_state.chat_counter += 1
        new_chat_name = f"Chat {st.session_state.chat_counter}"
        st.session_state.chats[new_chat_name] = []
        st.session_state.current_chat = new_chat_name
        st.rerun() # Refresh the UI instantly
        
    st.divider()
    st.subheader("Previous Chats")
    
    # Create a navigation button for every chat history
    for chat_name in reversed(list(st.session_state.chats.keys())):
        # Make the currently active chat visually distinct
        is_active = (chat_name == st.session_state.current_chat)
        if st.button(chat_name, key=chat_name, type="secondary" if not is_active else "primary", use_container_width=True):
            st.session_state.current_chat = chat_name
            st.rerun()

# ==========================================
# 4. MAIN DISPLAY (Chat Interface)
# ==========================================
st.header(f"Safety Analysis - {st.session_state.current_chat}")

# --- Step A: Render the Current Chat's History ---
active_messages = st.session_state.chats[st.session_state.current_chat]

for message in active_messages:
    with st.chat_message(message["role"]):
        if message.get("content"):
            st.markdown(message["content"])
        if message.get("image"):
            # Render the image small (250px width) instead of taking up the whole screen
            st.image(message["image"], width=250)

# --- Step B: The Modern Chat Input (With Attachment Icon) ---
# accept_file=True places the native paperclip icon inside the chat bar!
prompt = st.chat_input(
    "Ask a question and attach a dashcam frame...", 
    accept_file=True, 
    file_type=["jpg", "jpeg", "png"]
)

# --- Step C: Logic Execution ---
if prompt:
    # In newer Streamlit versions, prompt is a dict-like object
    user_text = prompt.text
    uploaded_files = prompt["files"] if "files" in prompt else []
    
    # Guardrail: Make sure they didn't just submit an empty box
    if not user_text and not uploaded_files:
        st.stop()
        
    new_user_message = {"role": "user", "content": user_text}
    
    # If they attached an image, open it and attach it to the message payload
    image_obj = None
    if uploaded_files:
        image_obj = Image.open(uploaded_files[0])
        new_user_message["image"] = image_obj
        
    # Save the new message to the active chat memory
    st.session_state.chats[st.session_state.current_chat].append(new_user_message)
    
    # Draw the user's message on the screen instantly
    with st.chat_message("user"):
        if user_text:
            st.markdown(user_text)
        if image_obj:
            st.image(image_obj, width=250)
            
    # Call the AI Backend
    with st.chat_message("assistant"):
        with st.spinner("Analyzing scene..."):
            
            # Look backwards in the chat history to find the most recently uploaded image
            # (This allows the user to ask follow-up questions without re-uploading the image)
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
                # Send to Dev B's backend
                response = analyze_dashcam_frame(image_to_analyze, user_text or "Analyze this image for safety hazards.")
                st.markdown(response)
                
                # Save the AI's response to memory
                st.session_state.chats[st.session_state.current_chat].append({"role": "assistant", "content": response})