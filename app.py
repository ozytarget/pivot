import streamlit as st
import pandas as pd
import numpy as np

# ============================================================================
# CONFIGURACIÓN DE STREAMLIT
# ============================================================================

st.set_page_config(
    page_title="Pivot - OI Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# ESTILOS
# ============================================================================

st.markdown("""
    <style>
        body { background-color: #0E1117; color: #FAFAFA; }
        .main { background-color: #0E1117; }
        .stTabs [data-baseweb="tab-list"] { background-color: #262730; }
        h1, h2, h3 { color: #58A6FF; }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================

st.title("📊 Pivot - Open Interest Analysis Tool")
st.markdown("---")

# ============================================================================
# SIDEBAR
# ============================================================================

st.sidebar.title("⚙️ Configuration")
analysis_type = st.sidebar.radio(
    "Select Analysis Type:",
    ["📈 Upload CSV", "📝 Manual Input", "ℹ️ About"]
)

# ============================================================================
# MAIN CONTENT
# ============================================================================

if analysis_type == "📈 Upload CSV":
    st.header("📥 Upload Options Data")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        help="Supported formats: strike,option_type,open_interest,volume OR Strike,CALL_OI,PUT_OI"
    )
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            
            st.subheader("📋 Data Preview")
            st.dataframe(df.head(10))
            
            st.subheader("📊 Analysis Results")
            
            # Estadísticas básicas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Rows", len(df))
            with col2:
                st.metric("Total Strikes", df.iloc[:, 0].nunique())
            with col3:
                if 'open_interest' in df.columns:
                    st.metric("Total OI", f"{df['open_interest'].sum():,.0f}")
                else:
                    st.metric("Total OI", "N/A")
            with col4:
                st.metric("Memory Used", f"{df.memory_usage().sum() / 1024:.1f} KB")
            
            st.success("✅ Data loaded successfully!")
            
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")
    else:
        st.info("👆 Upload a CSV file to get started")

elif analysis_type == "📝 Manual Input":
    st.header("✍️ Enter Data Manually")
    
    data_format = st.radio(
        "Select data format:",
        [
            "Format 1: strike,option_type,open_interest,volume",
            "Format 2: Strike,CallOI,PutOI",
            "Format 3: Strike,CALL_Gamma,PUT_Gamma,CALL_OI,PUT_OI"
        ]
    )
    
    data_input = st.text_area(
        "Paste your data (header + rows):",
        height=200,
        placeholder="strike,option_type,open_interest,volume\n5.0,call,1022,43\n5.0,put,0,0"
    )
    
    if data_input and st.button("🔍 Analyze"):
        try:
            lines = data_input.strip().split('\n')
            
            if len(lines) < 2:
                st.error("❌ Need at least header + 1 data row")
            else:
                from io import StringIO
                df = pd.read_csv(StringIO(data_input))
                
                st.subheader("📊 Analysis Results")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Rows", len(df))
                with col2:
                    st.metric("Columns", len(df.columns))
                with col3:
                    st.metric("Data Size", f"{df.memory_usage().sum() / 1024:.1f} KB")
                with col4:
                    st.metric("Format", f"{len(df.columns)} cols")
                
                st.dataframe(df)
                st.success("✅ Data parsed successfully!")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

elif analysis_type == "ℹ️ About":
    st.header("ℹ️ About Pivot")
    
    st.markdown("""
    ### 🎯 What is Pivot?
    
    **Pivot** is an Open Interest (OI) analysis tool designed for options traders.
    It helps you identify:
    - **Concentration Zones**: Where most OI is concentrated
    - **Max Pain**: Strike with highest theoretical loss
    - **Gamma Exposure**: Areas of highest gamma risk
    
    ### 📊 Supported Formats
    
    **Format 1 - Vertical (Long)**
    ```
    strike,option_type,open_interest,volume
    5.0,call,1022,43
    5.0,put,0,0
    ```
    
    **Format 2 - Compact**
    ```
    Strike,CallOI,PutOI
    100,1000,500
    105,800,600
    ```
    
    **Format 3 - Gamma Exposure**
    ```
    Strike,CALL_Gamma,PUT_Gamma,CALL_OI,PUT_OI
    100.0,0.0,0.0,0,0
    105.0,3.37e-16,0.0,0,100
    ```
    
    ### 🚀 Quick Start
    
    1. Upload a CSV or paste data manually
    2. Select your format
    3. View analysis results
    4. Export results
    
    ### 📚 Resources
    
    - **GitHub**: https://github.com/ozytarget/pivot
    - **Docs**: Check INTEGRATION_GUIDE.md
    - **TradingView**: Use OI_Zones_DataImport.pine
    
    ### 💡 Pro Tips
    
    - Larger OI = More concentration
    - Multiple formats supported automatically
    - Max Pain indicates equilibrium
    - Use with technical analysis
    
    ---
    
    **Version**: 1.0.0  
    **Last Updated**: January 22, 2026
    """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 12px;'>
        📊 Pivot v1.0.0 | Local: 8504 | Cloud: pivo.up.railway.app | GitHub: ozytarget/pivot
    </div>
""", unsafe_allow_html=True)
