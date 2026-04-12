import sys
import os
import asyncio
import base64
from io import BytesIO
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# ==========================================
# STREAMLIT ASYNC PATCH
# ==========================================
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.prompts import SYSTEM_PROMPT

load_dotenv()

# ==========================================
# PYDANTIC SCHEMA
# ==========================================
# This blueprint forces the AI to output exactly these fields in JSON
class SafetyReport(BaseModel):
    hazard_level: str = Field(description="Must be exactly: 'Low', 'Medium', or 'High'")
    hazards_detected: list[str] = Field(description="A list of specific hazards seen (e.g., ['pedestrian', 'wet road']). Leave empty if none.")
    analysis: str = Field(description="A detailed paragraph answering the user's specific question and explaining the hazard level.")

# Initialize the Gemini model (Make sure this matches the model you verified works!)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)

# Bind the Pydantic schema to the LLM
# This is the "Agentic" superpower: it guarantees a structured JSON return!
structured_llm = llm.with_structured_output(SafetyReport)


def encode_image(image):
    """Converts PIL Image to Base64"""
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_str}"


def analyze_dashcam_frame(image, user_query):
    """
    Sends the image and query to Gemini, and returns a Python dictionary (parsed from JSON).
    """
    try:
        base64_image = encode_image(image)
        
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=[
                    {"type": "text", "text": user_query},
                    {"type": "image_url", "image_url": {"url": base64_image}} 
                ]
            )
        ]
        
        # Invoke the structured LLM
        response_obj = structured_llm.invoke(messages)
        
        # We return the raw dictionary representation of the Pydantic object
        # Example: {"hazard_level": "Low", "hazards_detected": [], "analysis": "..."}
        return response_obj.dict()
        
    except Exception as e:
        # Fallback error format so our UI doesn't crash
        return {
            "hazard_level": "Error", 
            "hazards_detected": [], 
            "analysis": f"⚠️ DriveMind API Error: {str(e)}"
        }

# ==========================================
# LOCAL TESTING BLOCK
# ==========================================
if __name__ == "__main__":
    from PIL import Image
    test_image_path = "sample_images/test.jpg" 
    try:
        test_img = Image.open(test_image_path)
        print("Sending to DriveMind Cloud for Structured Analysis...")
        answer = analyze_dashcam_frame(test_img, "What is happening in this scene?")
        
        print("\n--- JSON RESPONSE ---")
        print(answer)
        print(f"Hazard Level: {answer['hazard_level']}")
        
    except FileNotFoundError:
        print("Image not found.")