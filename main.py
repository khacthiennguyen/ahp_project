import streamlit as st
from utils.i18n import get_text, set_language
from db import init_db
from ui.create_analysis import show_create_analysis
from ui.input_matrices import show_input_matrices
from ui.view_results import show_view_results

# Set up the page
st.set_page_config(page_title="AHP Decision Support System", layout="wide")

# Mặc định luôn là tiếng Việt
set_language('vi')

# Initialize database
init_db()

# Initialize session state
if 'criteria' not in st.session_state:
    st.session_state.criteria = []
if 'alternatives' not in st.session_state:
    st.session_state.alternatives = []
if 'criteria_matrix' not in st.session_state:
    st.session_state.criteria_matrix = None
if 'alternative_matrices' not in st.session_state:
    st.session_state.alternative_matrices = {}
if 'criteria_weights' not in st.session_state:
    st.session_state.criteria_weights = None
if 'alternative_weights' not in st.session_state:
    st.session_state.alternative_weights = {}
if 'final_scores' not in st.session_state:
    st.session_state.final_scores = None
if 'consistency_ratios' not in st.session_state:
    st.session_state.consistency_ratios = {}
if 'current_session_name' not in st.session_state:
    st.session_state.current_session_name = ""
if 'current_session_description' not in st.session_state:
    st.session_state.current_session_description = ""
if 'language' not in st.session_state:
    st.session_state.language = "en"
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "create_new_analysis"

# Language selector in sidebar
with st.sidebar:
    # About AHP section
    st.header(get_text("about_ahp"))
    st.write(get_text("ahp_description"))

# Main title
st.title(get_text("app_title"))

# Check if we need to show success message and switch tab
if 'switch_to_input_tab' in st.session_state and st.session_state.switch_to_input_tab:
    st.session_state.switch_to_input_tab = False
    st.session_state.current_tab = "input_matrices"
    
    # Show toast notification
    st.toast(get_text("analysis_created_successfully"), icon="✅")
    
    # Add custom CSS for toast styling
    st.markdown("""
    <style>
    .stToast {
        position: fixed !important;
        bottom: 20px !important;
        right: 20px !important;
        z-index: 9999 !important;
        background-color: #4CAF50 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 12px 20px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        animation: slideInRight 0.5s ease-out !important;
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Check if we need to switch to view results tab after calculation
if 'switch_to_view_results_tab' in st.session_state and st.session_state.switch_to_view_results_tab:
    st.session_state.switch_to_view_results_tab = False
    st.session_state.current_tab = "view_results"
    
    # Show toast notification for successful calculation
    st.toast("Kết quả đã được tính toán thành công!", icon="🎉")
    
    # Add custom CSS for calculation success toast
    st.markdown("""
    <style>
    .stToast {
        position: fixed !important;
        bottom: 20px !important;
        right: 20px !important;
        z-index: 9999 !important;
        background-color: #2E8B57 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 12px 20px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        animation: slideInRight 0.5s ease-out !important;
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Tab selection interface
col1, col2, col3 = st.columns(3)

with col1:
    if st.button(get_text("create_new_analysis"), key="tab1", 
                 use_container_width=True,
                 type="primary" if st.session_state.current_tab == "create_new_analysis" else "secondary"):
        st.session_state.current_tab = "create_new_analysis"
        st.rerun()

with col2:
    if st.button(get_text("input_matrices"), key="tab2", 
                 use_container_width=True,
                 type="primary" if st.session_state.current_tab == "input_matrices" else "secondary"):
        st.session_state.current_tab = "input_matrices"
        st.rerun()

with col3:
    if st.button(get_text("view_results"), key="tab3", 
                 use_container_width=True,
                 type="primary" if st.session_state.current_tab == "view_results" else "secondary"):
        st.session_state.current_tab = "view_results"
        st.rerun()

# st.divider()

# Show content based on selected tab
if st.session_state.current_tab == "create_new_analysis":
    show_create_analysis()
elif st.session_state.current_tab == "input_matrices":
    show_input_matrices()
elif st.session_state.current_tab == "view_results":
    show_view_results()

# Add a reset button
if st.sidebar.button(get_text("reset_application")):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()