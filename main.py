import streamlit as st
import base64
from openai import OpenAI

# 1. הגדרת חיבור לבינה המלאכותית (OpenAI)
# החלף את הטקסט במפתח שלך
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

def get_poker_advice_from_image(image_bytes):
    # הפיכת התמונה לפורמט טקסטואלי (Base64) שניתן לשלוח ב-API
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
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
        response = client.chat.completions.create(
            model="gpt-4o", # מודל בעל יכולות ראייה ממוחשבת חזקות
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return "ACTION: Error\nEXPLANATION: Could not process image with OpenAI. Check API Key."

# --- עיצוב ממשק האתר מותאם למובייל ---
st.set_page_config(page_title="Poker AI Coach", layout="centered")
st.title("🃏 Poker AI Coach (Vision)")
st.write("Point your Android camera at the screen and take a shot.")

# רכיב מצלמה קל ומאובטח
img_file_buffer = st.camera_input("Capture Table Screen", label_visibility="collapsed")

if img_file_buffer is not None:
    st.info("🧠 AI is analyzing the image using Vision...")
    
    # שליחת התמונה ישירות לניתוח
    ai_response = get_poker_advice_from_image(img_file_buffer.getvalue())
    
    try:
        action_part = ai_response.split("EXPLANATION:")[0].replace("ACTION:", "").strip()
        explanation_part = ai_response.split("EXPLANATION:")[1].strip()
    except:
        action_part = "Analysis Failed"
        explanation_part = "Could not read the table clearly. Ensure the screen details are visible and try again."

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
