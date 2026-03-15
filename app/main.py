"""
Sarawak Tourism & Culture Synth - Streamlit Frontend
A beautiful web interface for exploring Sarawak tourism information.
"""

import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.tourism_swarm import TourismSwarm

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Sarawak Tourism & Culture Synth",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a5f2a 0%, #2d8f45 50%, #3cb371 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .main-header p {
        color: #e8f5e9;
        font-size: 1.1rem;
    }
    .agent-log {
        background: #f8f9fa;
        border-left: 4px solid #2d8f45;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
    }
    .response-box {
        background: linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%);
        border: 2px solid #ffc107;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .source-tag {
        background: #e3f2fd;
        color: #1565c0;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.25rem;
        display: inline-block;
    }
    .stButton>button {
        background: linear-gradient(135deg, #2d8f45 0%, #1a5f2a 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(45, 143, 69, 0.4);
    }
    .sidebar-content {
        background: #f0f7f0;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_swarm():
    """Initialize the Tourism Swarm agent."""
    if 'swarm' not in st.session_state:
        with st.spinner("🌴 Initializing Sarawak Tourism Agents..."):
            st.session_state.swarm = TourismSwarm()
    return st.session_state.swarm


def display_header():
    """Display the main header."""
    st.markdown("""
    <div class="main-header">
        <h1>🌴 Sarawak Tourism & Culture Synth</h1>
        <p>Your AI-powered guide to the Land of the Hornbills</p>
    </div>
    """, unsafe_allow_html=True)


def display_sidebar():
    """Display the sidebar with information."""
    with st.sidebar:
        st.markdown("### 🗺️ About This App")
        st.markdown("""
        <div class="sidebar-content">
        This AI assistant uses a <strong>3-agent swarm architecture</strong> to answer your questions about Sarawak, Malaysia:
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 🤖 Agent Pipeline")
        st.markdown("""
        1. **🔍 Trip Planner Agent**  
           Analyzes your question and extracts key topics
        
        2. **📚 Sarawak Info Agent**  
           Searches our knowledge base of official documents
        
        3. **🎯 Tour Guide Agent**  
           Synthesizes information into a friendly response
        """)
        
        st.markdown("---")
        
        st.markdown("### 💡 Example Questions")
        example_questions = [
            "What wildlife can I see at Bako National Park?",
            "Tell me about the Rainforest World Music Festival",
            "How do I explore the Mulu Caves?",
            "What is the Sarawak Cultural Village?",
            "Best time to visit Sarawak?",
            "Traditional food I should try in Sarawak?"
        ]
        
        for q in example_questions:
            if st.button(q, key=f"example_{q[:20]}"):
                st.session_state.user_query = q
                st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 📊 Knowledge Base")
        data_dir = Path("data")
        pdf_files = list(data_dir.glob("*.pdf"))
        
        if pdf_files:
            st.success(f"✅ {len(pdf_files)} documents loaded")
            with st.expander("View documents"):
                for pdf in pdf_files:
                    st.markdown(f"- 📄 {pdf.name}")
        else:
            st.warning("⚠️ No PDF documents found in /data folder")
            st.markdown("Add Sarawak tourism PDFs to enable RAG search.")


def display_agent_logs(logs):
    """Display the agent processing logs."""
    st.markdown("#### 🔄 Agent Processing")
    for log in logs:
        st.markdown(f'<div class="agent-log">{log}</div>', unsafe_allow_html=True)


def display_response(result):
    """Display the synthesized response."""
    st.markdown("#### 🎯 Your Sarawak Guide Says:")
    
    st.markdown(f"""
    <div class="response-box">
        {result['response']}
    </div>
    """, unsafe_allow_html=True)
    
    # Display sources
    if result['sources']:
        st.markdown("#### 📚 Sources")
        sources_html = ""
        for source in result['sources']:
            sources_html += f'<span class="source-tag">📄 {source}</span> '
        st.markdown(sources_html, unsafe_allow_html=True)


def main():
    """Main application function."""
    display_header()
    display_sidebar()
    
    # Initialize the swarm
    swarm = initialize_swarm()
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # User input
        user_query = st.text_input(
            "Ask me anything about Sarawak:",
            value=st.session_state.get('user_query', ''),
            placeholder="e.g., What can I see at Bako National Park?",
            key="query_input"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        submit_button = st.button("🔍 Ask", use_container_width=True)
    
    # Process query
    if submit_button and user_query:
        # Clear previous results
        if 'result' in st.session_state:
            del st.session_state.result
        
        # Process through agent swarm
        with st.spinner("🌴 Our AI agents are working on your question..."):
            result = swarm.process_query(user_query)
            st.session_state.result = result
        
        # Clear the example query
        if 'user_query' in st.session_state:
            del st.session_state.user_query
    
    # Display results
    if 'result' in st.session_state:
        result = st.session_state.result
        
        st.markdown("---")
        
        # Create two columns for logs and response
        log_col, response_col = st.columns([1, 2])
        
        with log_col:
            display_agent_logs(result['logs'])
        
        with response_col:
            display_response(result)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        🌴 <strong>Sarawak Tourism & Culture Synth</strong> | 
        Built with ❤️ for Q10 Hackathon | 
        Powered by Gemini 2.5 Flash & RAG
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
