import sys
import os
import asyncio

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())



current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)


import base64
from io import BytesIO
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.prompts import SYSTEM_PROMPT

# Load the API key from the .env file
load_dotenv()

# Initialize the Gemini 1.5 Flash model
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

def encode_image(image):
    """
    Converts a PIL Image into a Base64 string format that LangChain/Gemini expects.
    """
    # Convert image to RGB just in case it's a PNG with a transparent background
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
        
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    # Encode the bytes into a string
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    # Format it as a data URI
    return f"data:image/jpeg;base64,{img_str}"

def analyze_dashcam_frame(image, user_query):
    """
    Takes a PIL Image and a text query, sends them to Gemini, 
    and returns the AI's text response.
    """
    try:
        # 1. Translate the PIL image into a Base64 string
        base64_image = encode_image(image)
        
        # 2. Build the LangChain message payload
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=[
                    {"type": "text", "text": user_query},
                    # Notice we are now passing a dictionary with the Base64 URL
                    {"type": "image_url", "image_url": {"url": base64_image}} 
                ]
            )
        ]
        
        # 3. Send to the cloud VLM
        response = llm.invoke(messages)
        return response.content
        
    except Exception as e:
        return f"⚠️ DriveMind API Error: {str(e)}"

# ==========================================
# DEVELOPER B's LOCAL TESTING BLOCK
# ==========================================
if __name__ == "__main__":
    from PIL import Image
    import sys
    
    # Updated path to run from the root DriveMind folder
    test_image_path = "sample_images/test.jpg" 
    
    try:
        print("Loading image...")
        test_img = Image.open(test_image_path)
        print("Translating image to Base64 and sending to DriveMind Cloud...")
        
        # Run the function
        answer = analyze_dashcam_frame(test_img, "Are there any hazards in this scene?")
        print("\n--- AI RESPONSE ---")
        print(answer)
        
    except FileNotFoundError:
        print(f"Error: Could not find an image at {test_image_path}. Please check the folder.")