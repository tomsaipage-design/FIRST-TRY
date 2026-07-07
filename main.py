import streamlit as st
import cv2
import numpy as np
import easyocr
from openai import OpenAI

# 1. הגדרת חיבור לבינה המלאכותית (OpenAI)
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

# אתחול מנוע קריאת הטקסט (OCR)
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

reader = load_ocr()

def get_poker_advice(raw_text_detected):
    prompt = f"""
    You are a professional GTO Poker Tournament Coach. 
    Look at the following raw text detected from a poker table screen via OCR:
    "{raw_text_detected}"
    
    Based on this data, figure out:
    1. What are the player's cards?
    2. What is the position or stack size if visible?
    3. What is the best action (FOLD, CALL, RAISE, CHECK)?
    
    Respond STRICTLY in the following format (in English):
    ACTION: [Write only the action here, e.g., FOLD / RAISE 2.5BB / CALL]
    EXPLANATION: [Write a professional, short explanation in English explaining the math or GTO logic behind this choice]
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return "ACTION: Error\nEXPLANATION: Server connection issue. Check API Key."

# --- עיצוב ממשק האתר מותאם למובייל ---
st.set_page_config(page_title="Poker AI Coach", layout="centered")
st.title("🃏 Poker AI Coach")
st.write("Point your Android camera at the screen and take a shot.")

# שימוש ברכיב המצלמה המובנה שמבקש מהאנדרואיד להשתמש במצלמה האחורית (Environment)
img_file_buffer = st.camera_input("Capture Table Screen", label_visibility="collapsed")

if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    st.info("🧠 AI is analyzing the table...")
    
    results = reader.readtext(cv2_img, detail=0)
    all_detected_text = " ".join(results)
    
    ai_response = get_poker_advice(all_detected_text)
    
    try:
        action_part = ai_response.split("EXPLANATION:")[0].replace("ACTION:", "").strip()
        explanation_part = ai_response.split("EXPLANATION:")[1].strip()
    except:
        action_part = "Analysis Failed"
        explanation_part = "Could not read data clearly. Try taking the photo from a straighter angle."

    st.markdown("---")
    st.subheader("Recommended Move:")
    
    if "FOLD" in action_part.upper():
        st.error(f"🛑 {action_part}")
    elif "RAISE" in action_part.upper():
        st.success(f"🚀 {action_part}")
    else:
        st.warning(f"⚠️ {action_part}")
        
    with st.expander("ℹ️ Show Detailed Logic"):
        st.write(explanation_part)
        st.caption(f"Raw data detected: {all_detected_text}")
