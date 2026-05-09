#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📦 批量导入处理模块
功能：
1. 支持 CSV/Excel 格式导入投诉列表
2. 批量调用 AI 分析
3. 导出批量处理结果
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from io import StringIO, BytesIO

# 导入 AI 分析模块
try:
    from ai_analyzer import AIComplaintAnalyzer
except ImportError:
    st.error("❌ 无法找到 AI 分析模块，请确保 ai_analyzer.py 在同一目录下")

def render_batch_processor():
    """渲染批量处理界面"""
    st.header("📦 批量导入处理")
    st.markdown("支持 CSV/Excel 格式，一次处理多条投诉")
    
    # 1. 文件上传
    uploaded_file = st.file_uploader("上传 CSV/Excel 文件", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file is None:
        st.info("👆 请先上传文件")
        return None
    
    # 2. 读取数据
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ 成功读取 {len(df)} 条数据")
        st.write("数据预览:", df.head())
        
    except Exception as e:
        st.error(f"❌ 读取文件失败：{e}")
        return None
    
    # 3. 列映射
    st.subheader("列映射")
    st.markdown("请确认哪一列是投诉内容：")
    
    columns = df.columns.tolist()
    if not columns:
        st.error("文件没有列")
        return None
        
    content_col = st.selectbox("投诉内容列", columns)
    id_col = st.selectbox("订单号/ID 列 (可选)", ["无"] + columns)
    
    # 4. 批量处理
    if st.button("🚀 开始批量分析", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        results = []
        analyzer = AIComplaintAnalyzer(use_mock=True)  # 默认模拟模式，避免消耗 API
        
        for i, row in df.iterrows():
            status_text.text(f"正在处理第 {i+1}/{len(df)} 条...")
            
            complaint = str(row[content_col])
            order_id = row[id_col] if id_col != "无" else f"Row_{i+1}"
            
            # 分析
            try:
                analysis = analyzer.analyze(complaint)
                responses = analyzer.generate_responses(complaint, analysis)
                
                results.append({
                    'order_id': order_id,
                    'complaint': complaint,
                    'emotion': analysis.get('emotion', ''),
                    'problem_type': analysis.get('problem_type', ''),
                    'response_empathy': responses.get('empathy', ''),
                    'response_professional': responses.get('professional', ''),
                    'response_compensation': responses.get('compensation', ''),
                    'status': 'Success'
                })
            except Exception as e:
                results.append({
                    'order_id': order_id,
                    'status': f'Error: {str(e)}'
                })
            
            # 更新进度
            progress_bar.progress((i + 1) / len(df))
        
        status_text.text("✅ 处理完成！")
        
        # 5. 结果展示与导出
        st.subheader("处理结果")
        results_df = pd.DataFrame(results)
        st.write(results_df[['order_id', 'emotion', 'problem_type', 'status']].head(10))
        
        # 导出 CSV
        csv = results_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 下载 CSV 结果",
            data=csv,
            file_name=f"batch_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # 导出 JSON (包含完整回复)
        json_str = json.dumps(results, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 下载 JSON 结果 (含完整回复)",
            data=json_str,
            file_name=f"batch_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
        
        return results_df

# 测试运行
if __name__ == "__main__":
    st.set_page_config(page_title="批量处理", layout="wide")
    render_batch_processor()
