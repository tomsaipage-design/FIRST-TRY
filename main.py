import streamlit as st
import cv2
import numpy as np
import easyocr
from openai import OpenAI

# 1. הגדרת חיבור לבינה המלאכותית (OpenAI) לצורך קבלת ההסברים
# יש להזין את ה-API Key שלך במערכת
client = OpenAI(api_key="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")

# אתחול מנוע קריאת הטקסט (OCR) - תומך באנגלית ומספרים
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

reader = load_ocr()

# פונקציה ששולחת את הנתונים ל-ChatGPT ומבקשת החלטה והסבר
def get_poker_advice(raw_text_detected):
    prompt = f"""
    You are a professional GTO Poker Tournament Coach. 
    Look at the following raw text detected from a poker table screen via OCR:
    "{raw_text_detected}"
    
    Based on this data, figure out:
    1. What are the player's cards?
    2. What is the position or stack size if visible?
    3. What is the best action (FOLD, CALL, RAISE, CHECK)?
    
    Respond STRICTLY in the following format (in Hebrew):
    ACTION: [Write only the action here, e.g., FOLD / RAISE 2.5BB / CALL]
    EXPLANATION: [Write a professional, short explanation in Hebrew explaining the math or GTO logic behind this choice]
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # מודל חזק ומהיר לניתוח
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return "ACTION: שגיאה\nEXPLANATION: לא מצליח להתחבר לשרת ה-AI. ודא שהקוד של OpenAI תקין."

# --- עיצוב ממשק האתר (UI) ---
st.set_page_config(page_title="Poker AI Coach", layout="centered")
st.title("🃏 מאמן פוקר AI בזמן אמת")
st.write("כוון את מצלמת הטלפון למסך הטורניר שלך לקבלת עצה מיידית")

# כפתור לפתיחת המצלמה ישירות בדפדפן (עובד מעולה גם מהנייד)
img_file_buffer = st.camera_input("צלם את שולחן הפוקר")

if img_file_buffer is not None:
    # הפיכת התמונה מהמצלמה לפורמט ש-Python מבין
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    st.info("🧠 ה-AI מנתח את השולחן כעת...")
    
    # שלב 2: קריאת הטקסט מהתמונה (OCR)
    results = reader.readtext(cv2_img, detail=0)
    all_detected_text = " ".join(results)
    
    # שלב 3: שליחת הטקסט ל-ChatGPT לקבלת החלטה
    ai_response = get_poker_advice(all_detected_text)
    
    # עיבוד התשובה והצגתה בצורה יפה על המסך
    try:
        action_part = ai_response.split("EXPLANATION:")[0].replace("ACTION:", "").strip()
        explanation_part = ai_response.split("EXPLANATION:")[1].strip()
    except:
        action_part = "ניתוח נכשל"
        explanation_part = "הבינה המלאכותית לא הצליחה לקרוא את הנתונים בבירור. נסה לצלם מזווית ישרה יותר."

    # הצגת המהלך המומלץ בכותרת ענקית וצבעונית
    st.markdown("---")
    st.subheader("המהלך המומלץ:")
    
    if "FOLD" in action_part.upper():
        st.error(f"🛑 {action_part}")
    elif "RAISE" in action_part.upper():
        st.success(f"🚀 {action_part}")
    else:
        st.warning(f"⚠️ {action_part}")
        
    # כפתור נפתח (אלקורדיון) שמציג את ההסבר רק אם המשתמש לוחץ עליו
    with st.expander("ℹ️ לחץ כאן להסבר המחשבה מאחורי המהלך"):
        st.write(explanation_part)
        st.caption(f"נתונים גולמיים שנראו במסך: {all_detected_text}")
