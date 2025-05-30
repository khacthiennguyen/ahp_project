import streamlit as st
from utils.i18n import get_text, set_language
from db import init_db
from ui.create_analysis import show_create_analysis
from ui.input_matrices_new import show_input_matrices
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

# Language selector in sidebar
with st.sidebar:
    # About AHP section
    st.header(get_text("about_ahp"))
    st.write(get_text("ahp_description"))

# Main title
st.title(get_text("app_title"))

# App tabs
tab1, tab2, tab3 = st.tabs([
    get_text("create_new_analysis"), 
    get_text("input_matrices"), 
    get_text("view_results")
])

# Tab 1: Create New Analysis
with tab1:
    show_create_analysis()

# Tab 2: Input Matrices
with tab2:
    show_input_matrices()

# Tab 3: View Results
with tab3:
    show_view_results()

# Add a reset button
if st.sidebar.button(get_text("reset_application")):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()