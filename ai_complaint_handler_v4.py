#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 AI Complaint Handler v4.0 (OCR Enhanced)
- 单条文本分析
- 批量 Excel 处理
- 模板管理
- ✨ 新增：图片/截图投诉识别 (PaddleOCR)
- ✨ 新增：Contact Us 表单 (Telegram 通知)
"""

import streamlit as st
import pandas as pd
import json
import os
import requests
from datetime import datetime
from io import BytesIO

# OCR 相关导入
try:
    from paddleocr import PaddleOCR
    import cv2
    import numpy as np
    import base64
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# 导入本地模块 (假设 ai_analyzer.py 和 telegram_notifier.py 在同一目录或路径中)
# 为简化演示，此处保留导入逻辑，实际运行需确保路径正确
try:
    from ai_analyzer import analyze_complaint  # 假设已有此函数
except ImportError:
    def analyze_complaint(text, template=None):
        # 模拟分析函数，防止报错
        return {"category": "General", "sentiment": "Neutral", "response": f"AI Analysis for: {text[:50]}..."}

try:
    from telegram_notifier import send_contact_notification
except ImportError:
    def send_contact_notification(name, email, message):
        pass

# 页面配置
st.set_page_config(page_title="AI Complaint Handler v4.0", page_icon="🤖", layout="wide")

# 标题
st.title("🤖 AI Complaint Handler v4.0")
st.markdown("""
**Automate your customer service workflow.**
- 📝 **Single Analysis**: Analyze one complaint instantly.
- 📊 **Batch Processing**: Upload Excel for bulk analysis.
- 🖼️ **Image/OCR**: Upload screenshots/images to extract & analyze text. (NEW!)
- 📄 **Template Management**: Customize analysis templates.
- 📬 **Contact Us**: Get in touch for custom solutions.
""")

# 侧边栏：模板管理
st.sidebar.header("⚙️ Template Management")
template_action = st.sidebar.selectbox("Action", ["View Templates", "Add New Template"])
template_file = "templates.json"

# 加载模板
def load_templates():
    if os.path.exists(template_file):
        with open(template_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# 保存模板
def save_templates(templates):
    with open(template_file, "w", encoding="utf-8") as f:
        json.dump(templates, f, indent=2, ensure_ascii=False)

templates = load_templates()

if template_action == "View Templates":
    st.sidebar.write("Current Templates:")
    for name, content in templates.items():
        st.sidebar.info(f"**{name}**: {content[:50]}...")
elif template_action == "Add New Template":
    new_name = st.sidebar.text_input("Template Name")
    new_content = st.sidebar.text_area("Template Content")
    if st.sidebar.button("Save Template"):
        if new_name and new_content:
            templates[new_name] = new_content
            save_templates(templates)
            st.sidebar.success(f"Template '{new_name}' saved!")
            st.rerun()

# 主界面：选项卡
tab1, tab2, tab3, tab4 = st.tabs(["📝 Single Analysis", "🖼️ Image/OCR (NEW)", "📊 Batch Processing", "📬 Contact Us"])

# Tab 1: Single Analysis
with tab1:
    st.header("Single Text Analysis")
    user_input = st.text_area("Enter complaint text:", height=150)
    selected_template = st.selectbox("Select Template (Optional)", ["None"] + list(templates.keys()))
    
    if st.button("Analyze"):
        if user_input:
            with st.spinner("Analyzing..."):
                template_content = templates.get(selected_template) if selected_template != "None" else None
                result = analyze_complaint(user_input, template_content)
                st.success("Analysis Complete!")
                st.json(result)
        else:
            st.warning("Please enter some text.")

# Tab 2: Image/OCR (NEW!)
with tab2:
    st.header("🖼️ Image/OCR Complaint Analysis")
    st.markdown("""
    Upload an image (screenshot, photo of document, etc.). 
    The system will extract text using **PaddleOCR** and analyze it.
    """)
    
    if not OCR_AVAILABLE:
        st.error("⚠️ OCR libraries (paddlepaddle, paddleocr) not installed. Please install requirements.")
        st.code("pip install paddlepaddle paddleocr")
    else:
        uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
        
        if uploaded_file is not None:
            # 显示图片
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
            
            if st.button("Extract & Analyze Text"):
                with st.spinner("🔍 Extracting text with OCR..."):
                    try:
                        # 初始化 OCR (首次加载较慢)
                        ocr = PaddleOCR(use_angle_cls=True, lang='en') 
                        
                        # 读取图片
                        img_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
                        img = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)
                        
                        # 执行 OCR
                        result = ocr.ocr(img, cls=True)
                        
                        # 提取文字
                        extracted_text = ""
                        if result and result[0]:
                            for line in result[0]:
                                extracted_text += line[1][0] + "\n"
                        
                        if extracted_text.strip():
                            st.success("✅ Text Extracted Successfully!")
                            st.text_area("Extracted Text", extracted_text, height=100)
                            
                            # 自动分析
                            st.markdown("### 🤖 AI Analysis Result:")
                            analysis_result = analyze_complaint(extracted_text)
                            st.json(analysis_result)
                        else:
                            st.warning("No text detected in the image.")
                            
                    except Exception as e:
                        st.error(f"OCR Error: {e}")

# Tab 3: Batch Processing
with tab3:
    st.header("📊 Batch Processing (Excel)")
    st.write("Upload an Excel file with a 'complaint_text' column.")
    uploaded_excel = st.file_uploader("Upload Excel", type=["xlsx"])
    
    if uploaded_excel:
        if st.button("Process Batch"):
            try:
                df = pd.read_excel(uploaded_excel)
                if 'complaint_text' in df.columns:
                    results = []
                    for text in df['complaint_text'].astype(str):
                        res = analyze_complaint(text)
                        results.append(res)
                    st.success("Batch processing complete!")
                    st.write(results)
                else:
                    st.error("Column 'complaint_text' not found.")
            except Exception as e:
                st.error(f"Error: {e}")

# Tab 4: Contact Us
with tab4:
    st.header("📬 Contact Us")
    st.write("Have a custom request? Let us know!")
    c_name = st.text_input("Name")
    c_email = st.text_input("Email")
    c_msg = st.text_area("Message")
    
    if st.button("Send"):
        if c_name and c_email and c_msg:
            try:
                send_contact_notification(c_name, c_email, c_msg)
                st.success("Message sent! We'll contact you soon.")
            except:
                st.success("Message queued (Demo Mode).")
        else:
            st.warning("Please fill all fields.")

# Footer
st.markdown("---")
st.markdown("Powered by **Yupeng AI** | [GitHub](https://github.com/yupeng012)")
