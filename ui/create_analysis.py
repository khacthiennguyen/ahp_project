import streamlit as st
import numpy as np
import pandas as pd
from utils.i18n import get_text
from utils.validation import validate_name, validate_analysis_setup

def show_create_analysis():
    """Show the create analysis UI"""
    st.header(get_text("step_1"))
    
    col1, col2 = st.columns(2)
    
    with col1:
        session_name = st.text_input(get_text("analysis_name"), key="session_name")
        session_description = st.text_area(get_text("description"), key="session_description")
    
    with col2:
        st.info(get_text("step_1"))
    
    st.header(get_text("step_2"))
    
    # Criteria section with improved UI
    col1, col2 = st.columns(2)
    
    with col1:
        # Replace single-line input with multi-line text area for batch input
        new_criteria_batch = st.text_area(
            get_text("add_criterion_batch"),
            placeholder="Tiêu chí 1\nTiêu chí 2\nTiêu chí 3",
            help="Nhập mỗi tiêu chí trên một dòng để thêm nhiều tiêu chí cùng lúc"
        )
        
        add_criterion_clicked = st.button(get_text("add_criterion_button"))
        
        if add_criterion_clicked and new_criteria_batch:
            # Split the text by newlines to get individual criteria
            criteria_list = [c.strip() for c in new_criteria_batch.split('\n') if c.strip()]
            
            # Process each criterion
            added_count = 0
            for criterion in criteria_list:
                valid, message = validate_name(criterion, st.session_state.criteria)
                if valid:
                    st.session_state.criteria.append(criterion)
                    added_count += 1
                else:
                    st.error(f"{criterion}: {message}")
            
            if added_count > 0:
                st.success(f"Đã thêm {added_count} tiêu chí")
    
    with col2:
        st.subheader(get_text("current_criteria"))
        
        if st.session_state.criteria:
            # Create a DataFrame for criteria with numbering
            criteria_df = pd.DataFrame({
                "STT": range(1, len(st.session_state.criteria) + 1),
                get_text("criterion"): st.session_state.criteria,
            })
            
            # Use an editable dataframe with custom styling
            edited_criteria_df = st.data_editor(
                criteria_df,
                column_config={
                    "STT": st.column_config.NumberColumn(
                        "STT",
                        width="small",
                        disabled=True,
                    ),
                    get_text("criterion"): st.column_config.TextColumn(
                        get_text("criterion"),
                        width="large",
                    ),
                },
                hide_index=True,
                use_container_width=True,
                key="criteria_editor",
                num_rows="dynamic"
            )
            
            # Update criteria if edited
            if len(edited_criteria_df) > 0:
                new_criteria = edited_criteria_df[get_text("criterion")].tolist()
                
                # Validate new criteria names
                valid_criteria = []
                for criterion in new_criteria:
                    if criterion and criterion.strip():
                        # Check for duplicates in the new list
                        if criterion not in valid_criteria:
                            valid_criteria.append(criterion)
                        else:
                            st.error(f"{criterion}: {get_text('error_duplicate_name')}")
                
                st.session_state.criteria = valid_criteria
        else:
            st.info(get_text("add_criterion"))
    
    st.header(get_text("step_3"))
    
    # Alternatives section with improved UI
    col1, col2 = st.columns(2)
    
    with col1:
        # Replace single-line input with multi-line text area for batch input
        new_alternatives_batch = st.text_area(
            get_text("add_alternative_batch"),
            placeholder="Phương án 1\nPhương án 2\nPhương án 3",
            help="Nhập mỗi phương án trên một dòng để thêm nhiều phương án cùng lúc"
        )
        
        add_alternative_clicked = st.button(get_text("add_alternative_button"))
        
        if add_alternative_clicked and new_alternatives_batch:
            # Split the text by newlines to get individual alternatives
            alternatives_list = [a.strip() for a in new_alternatives_batch.split('\n') if a.strip()]
            
            # Process each alternative
            added_count = 0
            for alternative in alternatives_list:
                valid, message = validate_name(alternative, st.session_state.alternatives)
                if valid:
                    st.session_state.alternatives.append(alternative)
                    added_count += 1
                else:
                    st.error(f"{alternative}: {message}")
            
            if added_count > 0:
                st.success(f"Đã thêm {added_count} phương án")
    
    with col2:
        st.subheader(get_text("current_alternatives"))
        
        if st.session_state.alternatives:
            # Create a DataFrame for alternatives with numbering
            alternatives_df = pd.DataFrame({
                "STT": range(1, len(st.session_state.alternatives) + 1),
                get_text("alternative"): st.session_state.alternatives,
            })
            
            # Use an editable dataframe with custom styling
            edited_alternatives_df = st.data_editor(
                alternatives_df,
                column_config={
                    "STT": st.column_config.NumberColumn(
                        "STT",
                        width="small",
                        disabled=True,
                    ),
                    get_text("alternative"): st.column_config.TextColumn(
                        get_text("alternative"),
                        width="large",
                    ),
                },
                hide_index=True,
                use_container_width=True,
                key="alternatives_editor",
                num_rows="dynamic"
            )
            
            # Update alternatives if edited
            if len(edited_alternatives_df) > 0:
                new_alternatives = edited_alternatives_df[get_text("alternative")].tolist()
                
                # Validate new alternative names
                valid_alternatives = []
                for alternative in new_alternatives:
                    if alternative and alternative.strip():
                        # Check for duplicates in the new list
                        if alternative not in valid_alternatives:
                            valid_alternatives.append(alternative)
                        else:
                            st.error(f"{alternative}: {get_text('error_duplicate_name')}")
                
                st.session_state.alternatives = valid_alternatives
        else:
            st.info(get_text("add_alternative"))
    
    # Initialize matrices button with validation
    st.markdown("---")
    
    # Display current count of criteria and alternatives
    col1, col2 = st.columns(2)
    with col1:
        criteria_count = len(st.session_state.criteria)
        alternatives_count = len(st.session_state.alternatives)
        st.info(f"{get_text('current_criteria')}: {criteria_count}")
    with col2:
        st.info(f"{get_text('current_alternatives')}: {alternatives_count}")
    
    # Clear any temporary calculations when re-initializing
    if 'temp_criteria_weights' in st.session_state:
        del st.session_state.temp_criteria_weights
    if 'temp_alternative_weights' in st.session_state:
        del st.session_state.temp_alternative_weights
    if 'temp_consistency_ratios' in st.session_state:
        del st.session_state.temp_consistency_ratios
    
    # Initialize matrices button with enhanced validation
    init_button = st.button(get_text("initialize_matrices"), type="primary", disabled=(criteria_count < 2 or alternatives_count < 2))
    if init_button:
        valid, message = validate_analysis_setup()
        if valid:
            n_criteria = len(st.session_state.criteria)
            st.session_state.criteria_matrix = np.ones((n_criteria, n_criteria))
            
            # Initialize alternative matrices for each criterion
            st.session_state.alternative_matrices = {}
            for criterion in st.session_state.criteria:
                n_alternatives = len(st.session_state.alternatives)
                st.session_state.alternative_matrices[criterion] = np.ones((n_alternatives, n_alternatives))
            
            st.session_state.current_session_name = session_name
            st.session_state.current_session_description = session_description
            
            st.success(get_text("matrices_initialized"))
        else:
            st.error(message)
    
    # Show an error message if the criteria or alternatives are insufficient
    if criteria_count < 2 or alternatives_count < 2:
        st.error(get_text("error_min_criteria_alternatives"))