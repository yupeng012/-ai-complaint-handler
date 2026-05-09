import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="AI Complaint Handler", page_icon="🤖")

st.title("🤖 AI Complaint Handler")
st.markdown("**Automate your customer service workflow.**")

# Analyzer
def analyze(text):
    t = text.lower()
    if "refund" in t or "money" in t: return {"category": "Refund", "sentiment": "Negative"}
    if "delay" in t or "late" in t: return {"category": "Delay", "sentiment": "Negative"}
    if "broken" in t or "quality" in t: return {"category": "Quality", "sentiment": "Negative"}
    return {"category": "General", "sentiment": "Neutral"}

# Telegram
def send_alert(name, email, msg):
    token = st.secrets.get("TELEGRAM_BOT_TOKEN")
    cid = st.secrets.get("TELEGRAM_CHAT_ID")
    if token and cid:
        try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": cid, "text": f"Lead: {name}\n{email}\n{msg}"}, timeout=3)
        except: pass

# UI
tab1, tab2, tab3 = st.tabs(["Analysis", "Batch", "Contact"])

with tab1:
    txt = st.text_area("Complaint text")
    if st.button("Analyze") and txt:
        st.json(analyze(txt))

with tab2:
    f = st.file_uploader("Upload Excel", type=["xlsx"])
    if f and st.button("Process"):
        try:
            df = pd.read_excel(f)
            if 'complaint_text' in df.columns:
                st.success("Done")
                st.dataframe([analyze(str(t)) for t in df['complaint_text']])
        except Exception as e: st.error(e)

with tab3:
    n = st.text_input("Name")
    e = st.text_input("Email")
    m = st.text_area("Message")
    if st.button("Send") and n and e and m:
        send_alert(n, e, m)
        st.success("Sent!")

st.markdown("---\nPowered by **Yupeng AI**")
