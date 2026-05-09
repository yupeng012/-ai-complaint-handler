import streamlit as st
import pandas as pd
import json
import os
from io import BytesIO
from ai_analyzer import analyze_complaint  # Import the helper function

# --- Configuration ---
st.set_page_config(page_title="AI Complaint Handler", page_icon="🤖", layout="wide")
TEMPLATE_FILE = "templates.json"

# --- Helper Functions: Template Management ---
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
        st.error(f"Failed to save template: {e}")
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
            st.error(f"Failed to delete template: {e}")
            return False
    return False

# --- Sidebar ---
with st.sidebar:
    st.title("🤖 AI Complaint Handler")
    st.markdown("**Features:**")
    st.markdown("- Single & Batch Analysis")
    st.markdown("- Smart Sentiment Detection")
    st.markdown("- Auto-classification & Suggestions")
    st.markdown("- Template Center")
    
    st.divider()
    st.markdown("📊 Status: **Online v3.0**")

# --- Main Interface ---
st.title("🤖 AI Complaint Handler System")
st.markdown("Automated complaint analysis platform powered by AI. Supports single entry and batch processing.")

# Initialize Session State
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "current_template_name" not in st.session_state:
    st.session_state.current_template_name = "Default Template"
if "template_config" not in st.session_state:
    # Default configuration
    st.session_state.template_config = {
        "dimensions": ["Sentiment Analysis", "Problem Classification", "Urgency", "Handling Suggestion"],
        "tone": "Professional and Empathetic",
        "language": "English"
    }

# Create three main tabs
tab_single, tab_batch, tab_templates = st.tabs(["📝 Single Analysis", "📊 Batch Processing", "📂 Template Center"])

# ==========================================
# Tab 1: Single Analysis
# ==========================================
with tab_single:
    st.header("Single Complaint Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        input_text = st.text_area("Enter complaint content:", height=200, placeholder="e.g., The product I purchased has quality issues, and the customer service attitude was terrible...")
    
    with col2:
        st.subheader("Analysis Configuration")
        st.info(f"Using: **{st.session_state.current_template_name}**")
        st.write("**Dimensions:**")
        for dim in st.session_state.template_config.get("dimensions", []):
            st.checkbox(dim, value=True, disabled=True) # Display only
        
        analyze_btn = st.button("Analyze", type="primary", use_container_width=True)
    
    if analyze_btn:
        if not input_text.strip():
            st.warning("Please enter complaint content before analyzing.")
        else:
            with st.spinner("AI is analyzing deeply, please wait..."):
                try:
                    # Call backend analysis logic
                    result = analyze_complaint(input_text, st.session_state.template_config)
                    st.session_state.analysis_result = result
                    st.success("Analysis complete!")
                except Exception as e:
                    st.error(f"Error during analysis: {e}")
                    st.session_state.analysis_result = None

    # Display Results
    if st.session_state.analysis_result:
        st.divider()
        st.subheader("📊 Analysis Results")
        res = st.session_state.analysis_result
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Sentiment", res.get("sentiment", "Unknown"))
        with c2:
            st.metric("Category", res.get("category", "Unknown"))
        with c3:
            st.metric("Urgency", res.get("urgency", "Normal"))
        
        st.markdown("### 💡 Detailed Analysis")
        st.markdown(res.get("analysis_detail", "No detailed analysis available"))
        
        st.markdown("### 🚀 Handling Suggestion")
        st.markdown(res.get("suggestion", "No specific suggestion"))

# ==========================================
# Tab 2: Batch Processing
# ==========================================
with tab_batch:
    st.header("📊 Excel Batch Processing")
    st.markdown("Upload an Excel file containing complaints to generate analysis reports in one click.")
    
    uploaded_file = st.file_uploader("Upload Excel file (.xlsx, .xls)", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            # Read Excel
            df_input = pd.read_excel(uploaded_file)
            st.write("✅ File read successfully! Preview (first 5 rows):")
            st.dataframe(df_input.head())
            
            # Select column
            columns = df_input.columns.tolist()
            text_col = st.selectbox("Select the column containing complaint text:", columns)
            
            if st.button("Start Batch Analysis", type="primary"):
                if not text_col:
                    st.warning("Please select the text column.")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    results = []
                    
                    total_rows = len(df_input)
                    
                    for i, row in df_input.iterrows():
                        text = str(row[text_col])
                        status_text.text(f"Analyzing {i+1}/{total_rows}...")
                        
                        try:
                            # Call analysis interface
                            res = analyze_complaint(text, st.session_state.template_config)
                            # Merge results
                            row_result = row.to_dict()
                            row_result["AI_Sentiment"] = res.get("sentiment", "")
                            row_result["AI_Category"] = res.get("category", "")
                            row_result["AI_Urgency"] = res.get("urgency", "")
                            row_result["AI_Summary"] = str(res.get("analysis_detail", ""))[:100] + "..." # Truncate
                            row_result["AI_Suggestion"] = res.get("suggestion", "")
                            results.append(row_result)
                        except Exception as e:
                            # Mark error
                            row_result = row.to_dict()
                            row_result["AI_Error"] = str(e)
                            results.append(row_result)
                        
                        progress_bar.progress((i + 1) / total_rows)
                    
                    # Generate result DataFrame
                    df_result = pd.DataFrame(results)
                    
                    st.success("Batch analysis complete!")
                    st.dataframe(df_result.head())
                    
                    # Provide download
                    output_buffer = BytesIO()
                    with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
                        df_result.to_excel(writer, index=False, sheet_name='Analysis Results')
                    
                    st.download_button(
                        label="📥 Download Results Excel",
                        data=output_buffer.getvalue(),
                        file_name="ai_complaint_analysis_result.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
        except Exception as e:
            st.error(f"Error processing file: {e}")
            st.write("Please ensure the uploaded file is a standard Excel file.")

# ==========================================
# Tab 3: Template Center
# ==========================================
with tab_templates:
    st.header("📂 Template Management Center")
    st.markdown("Save and load different analysis configurations for various business scenarios.")
    
    # 1. Save current config as template
    st.subheader("💾 Save Current Configuration")
    new_template_name = st.text_input("Template Name", placeholder="e.g., E-commerce Specialized")
    if st.button("Save as New Template"):
        if new_template_name:
            if save_template(new_template_name, st.session_state.template_config):
                st.success(f"Template '{new_template_name}' saved!")
                st.rerun()
            else:
                st.error("Save failed. Check permissions or disk space.")
        else:
            st.warning("Please enter a template name.")
    
    st.divider()
    
    # 2. Load/Delete existing templates
    st.subheader("📑 Existing Templates")
    templates = load_templates()
    
    if not templates:
        st.info("No saved templates yet.")
    else:
        for name, config in templates.items():
            with st.expander(f"📄 {name}"):
                st.write(f"**Config:** {config}")
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"Load Template", key=f"load_{name}"):
                        st.session_state.current_template_name = name
                        st.session_state.template_config = config
                        st.success(f"Loaded template: {name}")
                        st.rerun()
                with col_b:
                    if st.button(f"Delete Template", key=f"del_{name}"):
                        if delete_template(name):
                            st.success(f"Template '{name}' deleted")
                            st.rerun()
    
    st.divider()
    st.info("💡 Note: Templates are saved in the current deployment directory. In Streamlit Cloud, files may be lost after restart. Screenshot or export important configurations.")
