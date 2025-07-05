# frontend/streamlit_app.py
"""
Simplified Streamlit frontend for Literature Review System.
Clean, focused UI with essential features only.
"""

import streamlit as st
import asyncio
import os
from datetime import datetime
from pathlib import Path
import sys

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

# Import backend services
from literature_review_service import (
    LiteratureReviewService,
    ReviewConfig,
    ReviewStatus,
    ReviewProgress,
    create_literature_review_service
)

# Configure page
st.set_page_config(
    page_title="📚 Literature Review Assistant",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .search-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 2rem;
    }
    
    .result-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 2rem;
    }
    
    .status-processing {
        background: #dbeafe;
        border-left: 4px solid #3b82f6;
        color: #1e40af;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .status-completed {
        background: #dcfce7;
        border-left: 4px solid #22c55e;
        color: #166534;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .status-error {
        background: #fee2e2;
        border-left: 4px solid #ef4444;
        color: #dc2626;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .metric-box {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    
    .metric-box h3 {
        color: #1f2937;
        font-size: 1.5rem;
        margin: 0;
    }
    
    .metric-box p {
        color: #6b7280;
        font-size: 0.9rem;
        margin: 0.5rem 0 0 0;
    }
    
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        height: 3rem;
    }
    
    .progress-bar {
        background: #f1f5f9;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'lit_service' not in st.session_state:
        st.session_state.lit_service = create_literature_review_service()
    
    if 'current_result' not in st.session_state:
        st.session_state.current_result = None
    
    if 'is_processing' not in st.session_state:
        st.session_state.is_processing = False
    
    if 'progress_history' not in st.session_state:
        st.session_state.progress_history = []


def render_header():
    """Render main header"""
    st.markdown("""
    <div class="main-header">
        <h1>📚 Literature Review Assistant</h1>
        <p>AI-Powered Research Analysis with AutoGen Multi-Agent System</p>
    </div>
    """, unsafe_allow_html=True)


def render_search_interface():
    """Render search interface"""
    st.markdown('<div class="search-card">', unsafe_allow_html=True)
    
    # Research topic input
    st.markdown("### 🔍 Enter Research Topic")
    topic = st.text_input(
        "",
        placeholder="e.g., transformer architectures, federated learning, quantum computing",
        help="Be specific for better results. Use academic terminology when possible.",
        disabled=st.session_state.is_processing,
        label_visibility="collapsed"
    )
    
    # Controls in columns
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        # Number of papers
        max_papers = st.slider(
            "📄 Number of papers to analyze",
            min_value=1,
            max_value=10,
            value=5,
            disabled=st.session_state.is_processing
        )
    
    with col2:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.markdown(f"<h3>{max_papers}</h3>", unsafe_allow_html=True)
        st.markdown("<p>Papers</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.markdown("<h3>2</h3>", unsafe_allow_html=True)
        st.markdown("<p>AI Agents</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.markdown("<h3>arXiv</h3>", unsafe_allow_html=True)
        st.markdown("<p>Source</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Action buttons
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    
    # Check API key
    api_key_exists = bool(os.getenv("OPENAIROUTER_API_KEY"))
    
    with col_btn1:
        start_button = st.button(
            "🚀 Start Literature Review",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.is_processing or not api_key_exists
        )
    
    with col_btn2:
        clear_button = st.button(
            "🗑️ Clear Results",
            use_container_width=True,
            disabled=st.session_state.is_processing
        )
    
    with col_btn3:
        if st.session_state.current_result and st.session_state.current_result.success:
            st.download_button(
                "📥 Download Results",
                data=st.session_state.current_result.content,
                file_name=f"literature_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    # API key warning
    if not api_key_exists:
        st.error("❌ Please set the OPENAIROUTER_API_KEY environment variable to use this app.")
    
    return topic, max_papers, start_button, clear_button


def render_progress(progress_list):
    """Render progress tracking"""
    if not progress_list:
        return
    
    st.markdown('<div class="progress-bar">', unsafe_allow_html=True)
    st.markdown("### 📈 Progress")
    
    # Latest progress
    latest_progress = progress_list[-1]
    
    # Progress bar
    progress_bar = st.progress(latest_progress.progress_percent / 100)
    
    # Status message
    status_class = "status-processing"
    if latest_progress.status == ReviewStatus.ERROR:
        status_class = "status-error"
    elif latest_progress.status == ReviewStatus.COMPLETED:
        status_class = "status-completed"
    
    st.markdown(
        f'<div class="{status_class}"><strong>{latest_progress.status.value.replace("_", " ").title()}:</strong> {latest_progress.message}</div>',
        unsafe_allow_html=True
    )
    
    # Show recent progress steps
    if len(progress_list) > 1:
        with st.expander("📋 View Details"):
            for progress in reversed(progress_list[-5:]):
                timestamp = progress.timestamp.strftime("%H:%M:%S")
                st.text(f"[{timestamp}] {progress.status.value}: {progress.message}")
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_results(result):
    """Render literature review results"""
    if not result:
        return
    
    st.markdown("---")
    
    if result.success:
        # Success header
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### 📄 Literature Review Results")
        with col2:
            st.success(f"✅ Completed in {result.execution_time:.1f}s")
        
        # Results content
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown(result.content)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Review details
        with st.expander("ℹ️ Review Details"):
            st.json({
                "Topic": result.config.topic,
                "Papers Analyzed": result.config.max_results,
                "Execution Time": f"{result.execution_time:.2f} seconds",
                "Status": "Completed Successfully"
            })
    
    else:
        # Error display
        st.markdown("### ❌ Review Failed")
        st.markdown(f'<div class="status-error"><strong>Error:</strong> {result.error_message}</div>', unsafe_allow_html=True)


async def run_literature_review(config: ReviewConfig):
    """Run literature review with progress tracking"""
    progress_placeholder = st.empty()
    
    def progress_callback(progress: ReviewProgress):
        """Update progress in real-time"""
        st.session_state.progress_history.append(progress)
        with progress_placeholder.container():
            render_progress(st.session_state.progress_history)
    
    # Execute review
    result = await st.session_state.lit_service.run_review(config, progress_callback)
    st.session_state.current_result = result
    st.session_state.is_processing = False
    
    return result


def main():
    """Main application"""
    
    # Initialize
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Render search interface
    topic, max_papers, start_button, clear_button = render_search_interface()
    
    # Handle clear button
    if clear_button:
        st.session_state.current_result = None
        st.session_state.progress_history = []
        st.rerun()
    
    # Handle start button
    if start_button:
        if not topic.strip():
            st.warning("⚠️ Please enter a research topic before starting the review.")
        else:
            # Set processing state
            st.session_state.is_processing = True
            st.session_state.progress_history = []
            
            # Create review configuration
            config = ReviewConfig(
                topic=topic.strip(),
                max_results=max_papers,
                model_name="deepseek/deepseek-chat",  # Default model
                max_turns=2,  # Default turns
                api_key=os.getenv("OPENAIROUTER_API_KEY")
            )
            
            # Run review
            try:
                print("Starting literature review...")
                result = asyncio.run(run_literature_review(config))
                print(f"Review completed: {result.success}")
                st.rerun()
            except Exception as e:
                st.session_state.is_processing = False
                st.error(f"❌ Unexpected error: {str(e)}")
    
    # Render progress if processing
    if st.session_state.is_processing and st.session_state.progress_history:
        render_progress(st.session_state.progress_history)
    
    # Render results if available
    if st.session_state.current_result:
        render_results(st.session_state.current_result)


if __name__ == "__main__":
    main()