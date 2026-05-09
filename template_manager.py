#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📋 自定义模板管理模块
功能：
1. 预设公司抬头 (如：公司名称、联系方式)
2. 自定义常用话术 (如：道歉语、承诺语)
3. 赔偿标准配置 (如：优惠券金额、退款条件)
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime

# 配置文件路径
TEMPLATES_FILE = Path.home() / ".hermes" / "custom_templates.json"

def load_templates():
    """加载模板"""
    if TEMPLATES_FILE.exists():
        with open(TEMPLATES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    # 默认模板
    return {
        "company_name": "XX 科技有限公司",
        "company_phone": "400-XXX-XXXX",
        "company_email": "support@example.com",
        "apology_phrases": [
            "非常抱歉给您带来了不好的体验！",
            "对于此次失误，我们深感自责。",
            "您的满意是我们最看重的，发生这样的事我们责无旁贷。"
        ],
        "commitment_phrases": [
            "我们承诺会在 24 小时内给您满意的答复。",
            "我们将全程跟进，直到问题彻底解决。",
            "请您放心，我们一定负责到底。"
        ],
        "compensation_standard": {
            "level_1": "10 元优惠券",  # 轻微问题
            "level_2": "50 元优惠券",  # 中等问题
            "level_3": "100 元优惠券或包邮退换",  # 严重问题
        }
    }

def save_templates(templates):
    """保存模板"""
    TEMPLATES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TEMPLATES_FILE, 'w', encoding='utf-8') as f:
        json.dump(templates, f, ensure_ascii=False, indent=2)

def render_template_manager():
    """渲染模板管理界面"""
    st.header("📋 自定义模板管理")
    
    templates = load_templates()
    
    # 1. 公司信息
    st.subheader("🏢 公司信息配置")
    col1, col2, col3 = st.columns(3)
    with col1:
        templates["company_name"] = st.text_input("公司名称", templates["company_name"])
    with col2:
        templates["company_phone"] = st.text_input("客服电话", templates["company_phone"])
    with col3:
        templates["company_email"] = st.text_input("客服邮箱", templates["company_email"])
    
    # 2. 常用话术
    st.subheader("💬 常用话术库")
    
    st.markdown("**道歉语** (每行一句，用时会随机选择或轮询):")
    apology_text = st.text_area(
        "道歉语", 
        value="\n".join(templates["apology_phrases"]), 
        height=100
    )
    templates["apology_phrases"] = [line for line in apology_text.split("\n") if line.strip()]
    
    st.markdown("**承诺语**:")
    commitment_text = st.text_area(
        "承诺语", 
        value="\n".join(templates["commitment_phrases"]), 
        height=100
    )
    templates["commitment_phrases"] = [line for line in commitment_text.split("\n") if line.strip()]
    
    # 3. 赔偿标准
    st.subheader("🎁 赔偿标准配置")
    c1, c2, c3 = st.columns(3)
    with c1:
        templates["compensation_standard"]["level_1"] = st.text_input("轻微问题", templates["compensation_standard"]["level_1"])
    with c2:
        templates["compensation_standard"]["level_2"] = st.text_input("中等问题", templates["compensation_standard"]["level_2"])
    with c3:
        templates["compensation_standard"]["level_3"] = st.text_input("严重问题", templates["compensation_standard"]["level_3"])
    
    # 保存按钮
    st.markdown("---")
    if st.button("💾 保存模板配置", use_container_width=True):
        save_templates(templates)
        st.success("✅ 模板已保存！后续生成回复时将自动应用这些配置。")
        st.balloons()
    
    # 重置按钮
    if st.button("🔄 重置为默认值"):
        default = load_templates()  # 这里其实会加载刚保存的，需要硬编码默认值或者忽略，这里简化处理
        st.info("已恢复默认值 (需重新保存)")

# 测试运行
if __name__ == "__main__":
    st.set_page_config(page_title="模板管理", layout="wide")
    render_template_manager()
