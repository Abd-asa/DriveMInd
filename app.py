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
# 1. THE INTERFACE CONTRACT (Mock Backend)
# ==========================================
#def mock_analyze(image, question):
#    
#    This simulates Developer B's VLM backend. 
#    It takes an image and a string, waits 2 seconds, and returns a fake string.
#    Later, we simply swap this out for Developer B's real function.
#    
#    time.sleep(1) # Simulate network latency to the cloud VLM
#    return f"**Simulated VLM Analysis:**\n\nI received the image. Regarding your question (*'{question}'*): The scene appears clear, but I am just a mock function right now!"

# ==========================================
# 2. PAGE SETUP & LAYOUT
# ==========================================
# This must be the first Streamlit command called. It sets the browser tab info.
st.set_page_config(page_title="DriveMind Analyst", page_icon="🚗", layout="wide")

st.title("🚗 DriveMind: VLM Dashcam Analyst")
st.markdown("Upload a dashcam frame and ask our AI Agent to evaluate safety hazards.")

# ==========================================
# 3. SIDEBAR (Inputs)
# ==========================================
with st.sidebar:
    st.header("1. Upload Footage")
    # Streamlit handles the complex file buffering automatically here.
    uploaded_file = st.file_uploader("Choose a dashcam image...", type=["jpg", "jpeg", "png"])

# ==========================================
# 4. MAIN DISPLAY (Logic & Outputs)
# ==========================================
# Only show the rest of the app IF a file has been uploaded
if uploaded_file is not None:
    
    # --- Step A: Process and Show Image ---
    # We use PIL (Python Imaging Library) because it's the standard format 
    # that LangChain and Cloud APIs expect later on.
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Dashcam Frame", use_column_width=True)
    
    st.divider() # Draws a neat horizontal line
    
    # --- Step B: Capture User Query ---
    st.header("2. Ask the Analyst")
    user_query = st.text_input(
        "What would you like the AI to analyze?", 
        placeholder="e.g., Are there any pedestrians approaching the crosswalk?"
    )
    
    # --- Step C: Execution & Loading State ---
    # st.button returns True ONLY on the exact frame the user clicks it
    if st.button("Analyze Scene", type="primary"):
        
        # Guardrail: Make sure they actually typed a question
        if not user_query:
            st.warning("Please enter a question before analyzing.")
        else:
            # st.spinner is a context manager that shows a loading wheel while the block executes
            with st.spinner("Transmitting to DriveMind Cloud..."):
                
                # We call our mock contract here!
                #response = mock_analyze(image, user_query)
                response = analyze_dashcam_frame(image, user_query)
            
            # --- Step D: Display Results ---
            st.success("Analysis Complete!")
            # st.info creates a nice visual callout box for the AI's answer
            st.info(response)

else:
    # This shows when the app first boots up and no file is uploaded yet
    st.info("👈 Please upload a dashcam image in the sidebar to begin.")