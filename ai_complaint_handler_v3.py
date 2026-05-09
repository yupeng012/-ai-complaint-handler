import streamlit as st
import pandas as pd
import json
import os
from io import BytesIO
from ai_analyzer import analyze_complaint, ComplaintAnalysis  # 假设 ai_analyzer.py 中有这些接口

# --- 配置 ---
st.set_page_config(page_title="AI 投诉处理专家", page_icon="🤖", layout="wide")
TEMPLATE_FILE = "templates.json"

# --- 辅助函数：模板管理 ---
def load_templates():
    if os.path.exists(TEMPLATE_FILE):
        try:
            with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_template(name, config):
    templates = load_templates()
    templates[name] = config
    try:
        with open(TEMPLATE_FILE, "w", encoding="utf-8") as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"保存模板失败：{e}")
        return False

def delete_template(name):
    templates = load_templates()
    if name in templates:
        del templates[name]
        try:
            with open(TEMPLATE_FILE, "w", encoding="utf-8") as f:
                json.dump(templates, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"删除模板失败：{e}")
            return False
    return False

# --- 侧边栏 ---
with st.sidebar:
    st.title("🤖 AI 投诉处理专家")
    st.markdown("**功能列表:**")
    st.markdown("- 单条/批量分析")
    st.markdown("- 智能情绪识别")
    st.markdown("- 自动分类与建议")
    st.markdown("- 模板中心")
    
    st.divider()
    st.markdown("📊 当前状态：已上线 v3.0")

# --- 主界面 ---
st.title("🤖 AI 投诉处理专家系统")
st.markdown("基于人工智能的自动化投诉分析平台，支持单条精析与批量处理。")

# 初始化 Session State
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "current_template_name" not in st.session_state:
    st.session_state.current_template_name = "默认模板"
if "template_config" not in st.session_state:
    # 默认配置
    st.session_state.template_config = {
        "dimensions": ["情绪分析", "问题分类", "紧急程度", "处理建议"],
        "tone": "专业且富有同理心",
        "language": "中文"
    }

# 创建三个主要标签页
tab_single, tab_batch, tab_templates = st.tabs(["📝 单条分析", "📊 批量处理", "📂 模板中心"])

# ==========================================
# 标签页 1: 单条分析
# ==========================================
with tab_single:
    st.header("单条投诉分析")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        input_text = st.text_area("请输入投诉内容:", height=200, placeholder="例如：我购买的产品出现了质量问题，客服态度也很差...")
    
    with col2:
        st.subheader("分析配置")
        # 这里可以简化，直接使用当前激活的模板配置，或者允许微调
        st.info(f"当前使用：**{st.session_state.current_template_name}**")
        st.write("**分析维度:**")
        for dim in st.session_state.template_config.get("dimensions", []):
            st.checkbox(dim, value=True, disabled=True) # 仅展示
        
        analyze_btn = st.button("开始分析", type="primary", use_container_width=True)
    
    if analyze_btn:
        if not input_text.strip():
            st.warning("请输入投诉内容后再进行分析。")
        else:
            with st.spinner("AI 正在深度分析中，请稍候..."):
                try:
                    # 调用后端分析逻辑
                    # 注意：这里假设 ai_analyzer.py 中的 analyze_complaint 函数接受文本和配置
                    result = analyze_complaint(input_text, st.session_state.template_config)
                    st.session_state.analysis_result = result
                    st.success("分析完成！")
                except Exception as e:
                    st.error(f"分析过程中出错：{e}")
                    st.session_state.analysis_result = None

    # 展示结果
    if st.session_state.analysis_result:
        st.divider()
        st.subheader("📊 分析结果")
        res = st.session_state.analysis_result
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("情绪倾向", res.get("sentiment", "未知"))
        with c2:
            st.metric("问题分类", res.get("category", "未知"))
        with c3:
            st.metric("紧急程度", res.get("urgency", "普通"))
        
        st.markdown("### 💡 详细分析")
        st.markdown(res.get("analysis_detail", "无详细分析内容"))
        
        st.markdown("### 🚀 处理建议")
        st.markdown(res.get("suggestion", "无具体建议"))
        
        # 下载报告 (可选，如果需要单条报告)
        # st.download_button(...)

# ==========================================
# 标签页 2: 批量处理
# ==========================================
with tab_batch:
    st.header("📊 Excel 批量处理")
    st.markdown("上传包含投诉内容的 Excel 文件，一键生成分析报告。")
    
    uploaded_file = st.file_uploader("上传 Excel 文件 (.xlsx, .xls)", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            # 读取 Excel
            df_input = pd.read_excel(uploaded_file)
            st.write("✅ 文件读取成功！前 5 行预览：")
            st.dataframe(df_input.head())
            
            # 选择列
            columns = df_input.columns.tolist()
            text_col = st.selectbox("请选择包含投诉文本的列名:", columns)
            
            if st.button("开始批量分析", type="primary"):
                if not text_col:
                    st.warning("请选择文本列。")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    results = []
                    
                    total_rows = len(df_input)
                    
                    for i, row in df_input.iterrows():
                        text = str(row[text_col])
                        status_text.text(f"正在分析第 {i+1}/{total_rows} 条...")
                        
                        try:
                            # 调用分析接口
                            res = analyze_complaint(text, st.session_state.template_config)
                            # 合并结果
                            row_result = row.to_dict()
                            row_result["AI_情绪"] = res.get("sentiment", "")
                            row_result["AI_分类"] = res.get("category", "")
                            row_result["AI_紧急度"] = res.get("urgency", "")
                            row_result["AI_分析摘要"] = str(res.get("analysis_detail", ""))[:100] + "..." # 截断以防过长
                            row_result["AI_处理建议"] = res.get("suggestion", "")
                            results.append(row_result)
                        except Exception as e:
                            # 出错则标记
                            row_result = row.to_dict()
                            row_result["AI_错误"] = str(e)
                            results.append(row_result)
                        
                        progress_bar.progress((i + 1) / total_rows)
                    
                    # 生成结果 DataFrame
                    df_result = pd.DataFrame(results)
                    
                    st.success("批量分析完成！")
                    st.dataframe(df_result.head())
                    
                    # 提供下载
                    output_buffer = BytesIO()
                    with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
                        df_result.to_excel(writer, index=False, sheet_name='分析结果')
                    
                    st.download_button(
                        label="📥 下载分析结果 Excel",
                        data=output_buffer.getvalue(),
                        file_name="ai_complaint_analysis_result.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
        except Exception as e:
            st.error(f"处理文件时出错：{e}")
            st.write("请确保上传的是标准的 Excel 文件。")

# ==========================================
# 标签页 3: 模板中心
# ==========================================
with tab_templates:
    st.header("📂 模板管理中心")
    st.markdown("保存和加载不同的分析配置，适应不同业务场景。")
    
    # 1. 保存当前配置为模板
    st.subheader("💾 保存当前配置")
    new_template_name = st.text_input("模板名称", placeholder="例如：电商专用模板")
    if st.button("保存为新模板"):
        if new_template_name:
            if save_template(new_template_name, st.session_state.template_config):
                st.success(f"模板 '{new_template_name}' 已保存！")
                st.rerun()
            else:
                st.error("保存失败，请检查权限或磁盘空间。")
        else:
            st.warning("请输入模板名称。")
    
    st.divider()
    
    # 2. 加载/删除已有模板
    st.subheader("📑 已有模板列表")
    templates = load_templates()
    
    if not templates:
        st.info("暂无已保存的模板。")
    else:
        for name, config in templates.items():
            with st.expander(f"📄 {name}"):
                st.write(f"**配置:** {config}")
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"加载此模板", key=f"load_{name}"):
                        st.session_state.current_template_name = name
                        st.session_state.template_config = config
                        st.success(f"已加载模板：{name}")
                        st.rerun()
                with col_b:
                    if st.button(f"删除此模板", key=f"del_{name}"):
                        if delete_template(name):
                            st.success(f"模板 '{name}' 已删除")
                            st.rerun()
    
    st.divider()
    st.info("💡 提示：模板保存在当前部署目录下。在 Streamlit Cloud 中，文件可能在重启后丢失，建议重要配置截图保存或导出。")
