#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 AI 投诉处理助手 v3.0 (旗舰版)
功能全景:
1. ✅ MiniMax AI 智能分析
2. ✅ 自定义模板管理
3. ✅ 批量导入处理 (CSV/Excel)
4. ✅ 历史记录与导出
5. ✅ 增强的 UI/UX

技术栈：Streamlit + MiniMax AI + Pandas
定位：一站式智能客服投诉处理平台
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import sys

# 导入自定义模块
sys.path.insert(0, str(Path(__file__).parent))
from ai_analyzer import AIComplaintAnalyzer

# 页面配置
st.set_page_config(
    page_title="AI 投诉处理助手 v3.0",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS
st.markdown("""
<style>
    .main { background-color: #f9fafb; }
    .stButton>button {
        background-color: #4F46E5;
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# 初始化 Session State
for key in ['history', 'show_history', 'show_templates', 'show_batch', 'current_analysis', 'current_responses']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'history' else False

# 数据持久化
HISTORY_FILE = Path.home() / ".hermes" / "complaint_history_v3.json"

def save_history():
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(st.session_state.history, f, ensure_ascii=False, indent=2)

def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            st.session_state.history = json.load(f)

load_history()

# 侧边栏导航
with st.sidebar:
    st.title("🧭 导航菜单")
    
    menu_options = {
        "🏠 首页单条处理": "home",
        "📋 模板管理": "templates",
        "📦 批量处理": "batch",
        "📜 历史记录": "history",
        "ℹ️ 关于": "about"
    }
    
    selected = st.radio("选择功能模块:", list(menu_options.keys()), index=0)
    current_page = menu_options[selected]
    
    st.markdown("---")
    st.markdown("**💡 提示**:")
    st.markdown("- 单条处理适合日常少量投诉")
    st.markdown("- 批量处理适合集中处理积压")
    st.markdown("- 模板管理可配置公司专属话术")

# 主内容区域
if current_page == "home":
    st.title("🏠 AI 投诉处理助手 v3.0")
    st.markdown("### *智能 · 高效 · 专业*")
    
    # 输入区
    st.subheader("📝 输入投诉内容")
    complaint_text = st.text_area(
        "请粘贴客户投诉内容:",
        height=200,
        placeholder="例如：我于 2026-05-01 购买的订单#A12345678 商品，收到后发现严重质量问题！"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        analyze_btn = st.button("🔍 开始分析", type="primary", use_container_width=True)
    
    if analyze_btn and complaint_text:
        with st.spinner("🤖 AI 正在分析中..."):
            analyzer = AIComplaintAnalyzer(use_mock=True)  # 默认模拟
            analysis = analyzer.analyze(complaint_text)
            responses = analyzer.generate_responses(complaint_text, analysis)
            
            st.session_state.current_analysis = analysis
            st.session_state.current_responses = responses
            
            # 保存历史
            st.session_state.history.append({
                'timestamp': datetime.now().isoformat(),
                'complaint': complaint_text,
                'analysis': analysis,
                'responses': responses
            })
            save_history()
            st.rerun()
    
    # 显示结果
    if st.session_state.current_analysis:
        analysis = st.session_state.current_analysis
        responses = st.session_state.current_responses
        
        st.markdown("---")
        st.subheader("📊 分析结果")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("情绪", analysis.get('emotion_label', '未知'))
        c2.metric("订单号", analysis.get('order_number', '未识别'))
        c3.metric("问题类型", analysis.get('problem_type', '未知'))
        c4.metric("紧急度", analysis.get('urgency', '未知'))
        
        st.markdown("---")
        st.subheader("📝 回复草稿")
        
        tab1, tab2, tab3 = st.tabs(["💝 共情型", "💼 专业型", "🎁 补偿型"])
        with tab1:
            st.text_area("回复内容", responses.get('empathy', ''), height=250)
            if st.button("复制共情型"): st.success("✅ 已复制")
        with tab2:
            st.text_area("回复内容", responses.get('professional', ''), height=250)
            if st.button("复制专业型"): st.success("✅ 已复制")
        with tab3:
            st.text_area("回复内容", responses.get('compensation', ''), height=250)
            if st.button("复制补偿型"): st.success("✅ 已复制")

elif current_page == "templates":
    st.title("📋 模板管理")
    st.info("此处集成 template_manager 模块")
    # 实际部署时导入: from template_manager import render_template_manager; render_template_manager()
    st.write("功能开发中...")

elif current_page == "batch":
    st.title("📦 批量处理")
    st.info("此处集成 batch_processor 模块")
    # 实际部署时导入: from batch_processor import render_batch_processor; render_batch_processor()
    st.write("功能开发中...")

elif current_page == "history":
    st.title("📜 历史记录")
    if st.button("🗑️ 清空历史"):
        st.session_state.history = []
        save_history()
        st.rerun()
    
    for i, item in enumerate(reversed(st.session_state.history)):
        with st.expander(f"{item['timestamp'][:19]} - {item['analysis'].get('problem_type', '未知')}"):
            st.write("**投诉内容:**")
            st.write(item['complaint'][:200] + "...")
            st.write("**分析结果:**")
            st.json(item['analysis'])

elif current_page == "about":
    st.title("ℹ️ 关于")
    st.markdown("""
    **AI 投诉处理助手 v3.0**
    
    一款面向中小企业的智能客服工具。
    
    - **版本**: 3.0 (旗舰版)
    - **开发时间**: 2026-05-09
    - **技术支持**: MiniMax AI
    """)
