import streamlit as st
from utils.i18n import get_text

def validate_name(name, existing_names):
    """Validate a name (criterion or alternative)"""
    if not name.strip():
        return False, get_text("error_empty_name")
    
    if name in existing_names:
        return False, get_text("error_duplicate_name")
    
    return True, ""

def validate_analysis_setup():
    """Validate that the analysis setup is complete"""
    if len(st.session_state.criteria) == 0 or len(st.session_state.alternatives) == 0:
        return False, get_text("error_no_criteria_alternatives")
    
    return True, ""