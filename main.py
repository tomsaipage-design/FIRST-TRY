import streamlit as st
from google import genai
from google.genai import types

# חיבור ל-API החינמי של גוגל
gemini_key = st.secrets.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=gemini_key) if gemini_key else None

def get_poker_advice_gemini(image_bytes):
    if not client:
        return "ACTION: Configuration Error\nEXPLANATION: Please set GEMINI_API_KEY in Streamlit Secrets."
        
    prompt = """
    You are a professional GTO Poker Tournament Coach. 
    Analyze this image of a poker table screen taken via a mobile phone camera.
    
    Extract all critical data you can see:
    1. Hero's cards.
    2. Community cards (if any).
    3. Hero's position and stack size in Big Blinds (BB).
    4. Action history before Hero.
    
    Based on this data, determine the absolute best GTO play (FOLD, CALL, CHECK, or RAISE/PUSH with sizing).
    
    Respond STRICTLY in the following format (in English):
    ACTION: [Write only the action here, e.g., FOLD / RAISE 2.5BB / CALL]
    EXPLANATION: [Write a professional, short explanation in English explaining the strategic GTO logic behind this choice]
    """
    
    try:
        # תיקון הפורמט עבור הספרייה החדשה של google-genai
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/jpeg'
                ),
                prompt
            ]
        )
        return response.text
    except Exception as e:
        # הצגת השגיאה האמיתית בתוך תפריט נפתח למקרה הצורך
        return f"ACTION: Error\nEXPLANATION: Could not process image. Technical details: {str(e)}"

# --- ממשק מובייל ---
st.set_page_config(page_title="Free Gemini Poker Coach", layout="centered")
st.title("🃏 Free AI Poker Coach")
st.write("100% Free - Powered by Google Gemini")

img_file_buffer = st.camera_input("Capture Table Screen", label_visibility="collapsed")

if img_file_buffer is not None:
    st.info("🧠 Gemini Vision is analyzing the image...")
    
    ai_response = get_poker_advice_gemini(img_file_buffer.getvalue())
    
    try:
        action_part = ai_response.split("EXPLANATION:")[0].replace("ACTION:", "").strip()
        explanation_part = ai_response.split("EXPLANATION:")[1].strip()
    except:
        action_part = "Analysis Response Received"
        explanation_part = ai_response

    st.markdown("---")
    st.subheader("Recommended Move:")
    
    if "FOLD" in action_part.upper():
        st.error(f"🛑 {action_part}")
    elif "RAISE" in action_part.upper() or "PUSH" in action_part.upper():
        st.success(f"🚀 {action_part}")
    else:
        st.warning(f"⚠️ {action_part}")
        
    with st.expander("ℹ️ Show Detailed Logic"):
        st.write(explanation_part)
