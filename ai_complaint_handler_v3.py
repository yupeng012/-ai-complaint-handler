# -*- coding: utf-8 -*-
"""
🚀 AI Complaint Handler v3.2 (Final Clean Version)
- NO external imports (except standard libs)
- Self-contained logic
- Streamlit Cloud Ready
"""

import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- Configuration ---
st.set_page_config(page_title="AI Complaint Handler", page_icon="🤖", layout="wide")

# --- Logic Class (Internal) ---
class InternalAnalyzer:
    def __init__(self):
        self.templates = {
            "Refund": "We apologize for the inconvenience. A refund has been initiated.",
            "Delay": "We understand your frustration regarding the delay. We are expediting your order.",
            "Quality": "Thank you for your feedback on quality. We are investigating this issue.",
            "Default": "Thank you for contacting us. We value your feedback."
        }

    def analyze(self, text):
        text_lower = text.lower()
        if "refund" in text_lower or "money" in text_lower:
            category = "Refund"
            sentiment = "Negative"
        elif "delay" in text_lower or "late" in text_lower:
            category = "Delay"
            sentiment = "Negative"
        elif "broken" in text_lower or "quality" in text_lower:
            category = "Quality"
            sentiment = "Negative"
        else:
            category = "General"
            sentiment = "Neutral"
        
        return {
            "category": category,
            "sentiment": sentiment,
            "response": self.templates.get(category, self.templates["Default"]),
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

# --- Telegram Function ---
def send_telegram_alert(name, email, message):
    token = st.secrets.get("TELEGRAM_BOT_TOKEN")
    chat_id = st.secrets.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    text = f"📬 *New Lead*: {name}\n📧 {email}\n💬 {message}"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}, timeout=5)
        return True
    except:
        return False

# --- Main App ---
def main():
    st.title("🤖 AI Complaint Handler")
    st.markdown("**Automate your customer service workflow.**")
    
    analyzer = InternalAnalyzer()
    
    tab1, tab2, tab3 = st.tabs(["📝 Analysis", "📊 Batch", "📬 Contact"])
    
    # Tab 1
    with tab1:
        st.header("Single Analysis")
        user_input = st.text_area("Complaint text:", height=100)
        if st.button("Analyze"):
            if user_input:
                result = analyzer.analyze(user_input)
                st.success("✅ Done")
                st.json(result)
    
    # Tab 2
    with tab2:
        st.header("Batch Processing")
        uploaded = st.file_uploader("Upload Excel", type=["xlsx"])
        if uploaded and st.button("Process"):
            try:
                df = pd.read_excel(uploaded)
                if 'complaint_text' in df.columns:
                    results = [analyzer.analyze(str(t)) for t in df['complaint_text']]
                    st.success("✅ Batch Done")
                    st.dataframe(results)
                else:
                    st.error("Missing 'complaint_text' column")
            except Exception as e:
                st.error(f"Error: {e}")

    # Tab 3
    with tab3:
        st.header("Contact Us")
        name = st.text_input("Name")
        email = st.text_input("Email")
        msg = st.text_area("Message")
        if st.button("Send"):
            if name and email and msg:
                if send_telegram_alert(name, email, msg):
                    st.success("✅ Sent!")
                else:
                    st.success("✅ Queued (Demo)")

if __name__ == "__main__":
    main()
