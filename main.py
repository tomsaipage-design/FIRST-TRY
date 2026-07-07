import streamlit as st
import cv2
import numpy as np
import pytesseract
from groq import Groq

# חיבור ל-API החינמי של Groq (מודל Llama 3)
groq_key = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=groq_key) if groq_key else None

def get_poker_advice_free(raw_text_detected):
    if not client:
        return "ACTION: Configuration Error\nEXPLANATION: Please set GROQ_API_KEY in Streamlit Secrets."
        
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
    EXPLANATION: [Write a professional, short explanation in English explaining the logic]
    """
    
    try:
        # שימוש במודל Llama 3 החינמי והמהיר ביותר בעולם כיום
        response = client.chat.completions.create(
            model="llama3-8b-8192", 
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250
        )
        return response.choices[0].message.content
    except Exception as e:
        return "ACTION: Error\nEXPLANATION: AI server issue. Check your free API Key."

# --- ממשק מובייל ---
st.set_page_config(page_title="Free Poker AI Coach", layout="centered")
st.title("🃏 Free Poker AI Coach")
st.write("100% Free - Powered by Tesseract & Llama 3")

img_file_buffer = st.camera_input("Capture Table Screen", label_visibility="collapsed")

if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    # המרת התמונה למערך שמתאים לעיבוד תמונה
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    st.info("🧠 Reading screen text for free...")
    
    # שלב ה-OCR החינמי של גוגל
    gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
    all_detected_text = pytesseract.image_to_string(gray)
    
    if not all_detected_text.strip():
        st.warning("Could not find text. Try taking the photo closer or more straight.")
    else:
        st.info("🤖 AI is thinking...")
        ai_response = get_poker_advice_free(all_detected_text)
        
        try:
            action_part = ai_response.split("EXPLANATION:")[0].replace("ACTION:", "").strip()
            explanation_part = ai_response.split("EXPLANATION:")[1].strip()
        except:
            action_part = "Analysis Failed"
            explanation_part = "Could not parse response. Raw text was: " + all_detected_text

        st.markdown("---")
        st.subheader("Recommended Move:")
        
        if "FOLD" in action_part.upper():
            st.error(f"🛑 {action_part}")
        elif "RAISE" in action_part.upper() or "PUSH" in action_part.upper():
            st.success(f"🚀 {action_part}")
        else:
            st.warning(f"⚠️ {action_part}")
            
        with st.expander("ℹ️ Show Detailed Logic & Raw Data"):
            st.write(explanation_part)
            st.caption(f"Raw data detected: {all_detected_text}")
