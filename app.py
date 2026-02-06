"""
AI Pharma Lead Generation Platform - Web Interface
Streamlit-based dashboard for lead generation
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config import (
    SERPAPI_KEY, GROQ_API_KEY, OPENAI_API_KEY,
    SEARCH_KEYWORDS, OUTPUT_DIR, OUTPUT_FILENAME
)
from database.storage import LeadStorage
from pipeline.agent import run_pipeline

# Page config
st.set_page_config(
    page_title="🏭 Pharma Lead Generator",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-top: 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1rem;
        font-size: 1.1rem;
        border-radius: 10px;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)


def get_storage():
    """Get storage instance"""
    return LeadStorage()


def load_leads():
    """Load leads from database"""
    storage = get_storage()
    companies = storage.get_all_companies()
    if companies:
        df = pd.DataFrame(companies)
        return df
    return pd.DataFrame()


def show_sidebar():
    """Sidebar with configuration status"""
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # API Status
        st.markdown("### API Status")
        
        if SERPAPI_KEY:
            st.success("✅ SerpAPI Connected")
        else:
            st.error("❌ SerpAPI Key Missing")
        
        if GROQ_API_KEY:
            st.success("✅ Groq (FREE) Connected")
        elif OPENAI_API_KEY:
            st.success("✅ OpenAI Connected")
        else:
            st.info("ℹ️ Using Keyword Classification")
        
        st.markdown("---")
        
        # Search Keywords Preview
        st.markdown("### 🔍 Search Keywords")
        with st.expander("View Keywords", expanded=False):
            for kw in SEARCH_KEYWORDS:
                st.markdown(f"- {kw}")
        
        st.markdown("---")
        
        # Quick Stats
        storage = get_storage()
        total = storage.count()
        st.markdown("### 📊 Database Stats")
        st.metric("Total Leads", total)


def show_dashboard(df):
    """Main dashboard with visualizations"""
    
    if df.empty:
        st.info("📭 No leads in database yet. Run the pipeline to discover leads!")
        return
    
    # Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🏢 Total Companies", len(df))
    
    with col2:
        marketing = len(df[df['business_model'] == 'marketing']) if 'business_model' in df else 0
        st.metric("📣 Marketing Only", marketing)
    
    with col3:
        manufacturing = len(df[df['business_model'] == 'manufacturing']) if 'business_model' in df else 0
        st.metric("🏭 Manufacturing", manufacturing)
    
    with col4:
        if 'outsourcing_score' in df.columns:
            high_score = len(df[df['outsourcing_score'] >= 7])
        else:
            high_score = 0
        st.metric("🎯 High Priority", high_score)
    
    with col5:
        contacts = len(df[df['contact_found'] == 1]) if 'contact_found' in df else 0
        st.metric("📇 With Contacts", contacts)
    
    st.markdown("---")
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Business Model Distribution")
        if 'business_model' in df.columns:
            model_counts = df['business_model'].value_counts()
            fig = px.pie(
                values=model_counts.values,
                names=model_counts.index,
                color_discrete_sequence=['#667eea', '#764ba2', '#f093fb']
            )
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Outsourcing Score Distribution")
        if 'outsourcing_score' in df.columns:
            fig = px.histogram(
                df, x='outsourcing_score',
                nbins=10,
                color_discrete_sequence=['#667eea']
            )
            fig.update_layout(
                xaxis_title="Score",
                yaxis_title="Count",
                margin=dict(t=0, b=0, l=0, r=0)
            )
            st.plotly_chart(fig, use_container_width=True)


def show_leads_table(df):
    """Display leads in a table"""
    
    if df.empty:
        return
    
    st.markdown("### 📋 Lead Database")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'business_model' in df.columns:
            models = ['All'] + list(df['business_model'].unique())
            selected_model = st.selectbox("Business Model", models)
    
    with col2:
        if 'outsourcing_score' in df.columns:
            min_score = st.slider("Min Score", 1, 10, 1)
    
    with col3:
        search = st.text_input("🔍 Search Company")
    
    # Filter data
    filtered_df = df.copy()
    
    if 'business_model' in df.columns and selected_model != 'All':
        filtered_df = filtered_df[filtered_df['business_model'] == selected_model]
    
    if 'outsourcing_score' in df.columns:
        filtered_df = filtered_df[filtered_df['outsourcing_score'] >= min_score]
    
    if search:
        filtered_df = filtered_df[
            filtered_df['company_name'].str.contains(search, case=False, na=False)
        ]
    
    # Display columns
    display_cols = [
        'company_name', 'website', 'location', 'business_model',
        'outsourcing_score', 'emails', 'notes'
    ]
    display_cols = [c for c in display_cols if c in filtered_df.columns]
    
    st.dataframe(
        filtered_df[display_cols],
        use_container_width=True,
        height=400
    )
    
    st.markdown(f"*Showing {len(filtered_df)} of {len(df)} leads*")


def run_pipeline_ui():
    """Run pipeline with UI feedback"""
    
    st.markdown("### 🚀 Run Lead Discovery Pipeline")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        test_mode = st.checkbox("🧪 Test Mode (fewer searches)", value=True)
    
    with col2:
        run_button = st.button("▶️ Start Pipeline", type="primary")
    
    if run_button:
        if not SERPAPI_KEY:
            st.error("❌ SerpAPI key required. Add SERPAPI_KEY to .env file.")
            return
        
        # Modify config for test mode
        if test_mode:
            import config.config as cfg
            cfg.SEARCH_KEYWORDS = cfg.SEARCH_KEYWORDS[:2]
            cfg.MAX_RESULTS_PER_KEYWORD = 5
            cfg.MAX_RESULTS_PER_DIRECTORY = 5
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("🔍 Phase 1: Collecting data from Google & directories...")
            progress_bar.progress(10)
            
            # Run pipeline
            result = run_pipeline()
            
            progress_bar.progress(100)
            status_text.text("✅ Pipeline complete!")
            
            # Results
            st.success(f"""
            **Pipeline Complete!**
            - 📥 Raw results: {len(result.get('search_results', []))}
            - 🏢 Companies processed: {len(result.get('companies', []))}
            - 💾 New saved: {result.get('saved_count', 0)}
            - ⏭️ Duplicates skipped: {result.get('duplicate_count', 0)}
            """)
            
            if result.get('errors'):
                with st.expander("⚠️ Errors"):
                    for e in result['errors']:
                        st.warning(e)
            
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Pipeline failed: {e}")


def export_csv():
    """Export leads to CSV"""
    storage = get_storage()
    
    if storage.count() == 0:
        st.warning("No leads to export")
        return
    
    try:
        filepath = storage.export_to_csv()
        
        # Read file for download
        with open(filepath, 'r') as f:
            csv_data = f.read()
        
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"pharma_leads_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Export failed: {e}")


def main():
    """Main app"""
    
    # Header
    st.markdown('<p class="main-header">🏭 AI Pharma Lead Generator</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Discover pharmaceutical companies that outsource manufacturing</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    show_sidebar()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🚀 Run Pipeline", "📥 Export"])
    
    # Load data
    df = load_leads()
    
    with tab1:
        show_dashboard(df)
        show_leads_table(df)
    
    with tab2:
        run_pipeline_ui()
    
    with tab3:
        st.markdown("### 📥 Export Leads")
        st.markdown("Download all leads as a CSV file.")
        export_csv()


if __name__ == "__main__":
    main()
