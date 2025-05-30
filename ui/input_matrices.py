import streamlit as st
import numpy as np
import pandas as pd
from utils.i18n import get_text
from ahp import get_saaty_scale_description, calculate_all_results, calculate_weights, calculate_consistency_ratio
from db import save_results
from utils.formatting import format_decimal
from utils.validation import validate_matrix_consistency

def show_input_matrices():
    """Show the input matrices UI"""
    if st.session_state.criteria_matrix is not None:
        st.header(get_text("pairwise_comparison"))
        st.info(get_text("saaty_scale_info"))
        
        # Create tabs for criteria and each alternative comparison
        tab_titles = [get_text("criteria_comparison")]
        for criterion in st.session_state.criteria:
            tab_titles.append(f"{get_text('alternative_comparison')} {criterion}")
        
        # Initialize session state variables for tab navigation if they don't exist
        if 'current_matrix_tab' not in st.session_state:
            st.session_state.current_matrix_tab = 0
        
        # Track whether matrices are consistent for tab navigation
        if 'matrix_consistency' not in st.session_state:
            st.session_state.matrix_consistency = {
                'criteria': False
            }
            for criterion in st.session_state.criteria:
                st.session_state.matrix_consistency[criterion] = False
        
        # Ensure current tab is within valid range
        st.session_state.current_matrix_tab = min(st.session_state.current_matrix_tab, len(tab_titles) - 1)
        
        # Use radio buttons for tab selection instead of st.tabs for better control
        current_tab = st.radio("", tab_titles, index=st.session_state.current_matrix_tab, horizontal=True, label_visibility="collapsed")
        current_tab_index = tab_titles.index(current_tab)
        
        # Update the current tab in session state
        st.session_state.current_matrix_tab = current_tab_index
        
        # Criteria comparison tab
        with matrix_tabs[0]:
            input_method = st.radio(
                "Input Method",
                options=[get_text("dropdown_input"), get_text("manual_input")],
                horizontal=True,
                key="criteria_input_method"
            )
            
            criteria_matrix = st.session_state.criteria_matrix
            n_criteria = len(st.session_state.criteria)
            
            if input_method == get_text("dropdown_input"):
                # Display criteria matrix as a form with dropdowns
                for i in range(n_criteria):
                    for j in range(i+1, n_criteria):
                        col1, col2, col3 = st.columns([2, 1, 2])
                        with col1:
                            st.write(st.session_state.criteria[i])
                        with col2:
                            value = st.selectbox(
                                f"{get_text('compare')} {st.session_state.criteria[i]} {get_text('vs')} {st.session_state.criteria[j]}",
                                options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 1/2, 1/3, 1/4, 1/5, 1/6, 1/7, 1/8, 1/9],
                                format_func=lambda x: f"{x} - {get_saaty_scale_description(int(x), st.session_state.language) if x >= 1 else f'1/{int(1/x)} - {get_text('inverse_of')} {get_saaty_scale_description(int(1/x), st.session_state.language)}'}",
                                key=f"criteria_{i}_{j}",
                                index=0
                            )
                            criteria_matrix[i, j] = value
                            criteria_matrix[j, i] = 1 / value
                        with col3:
                            st.write(st.session_state.criteria[j])
            else:  # Manual input
                # Create a DataFrame for manual input
                matrix_df = pd.DataFrame(
                    data=np.zeros((n_criteria, n_criteria)),
                    columns=st.session_state.criteria,
                    index=st.session_state.criteria
                )
                
                # Fill the diagonal with 1s
                for i in range(n_criteria):
                    matrix_df.iloc[i, i] = 1.0
                
                # Fill the upper triangle with current values
                for i in range(n_criteria):
                    for j in range(i+1, n_criteria):
                        matrix_df.iloc[i, j] = criteria_matrix[i, j]
                
                # Create an editable dataframe
                st.write("Enter values in the upper triangle only. Lower triangle will be calculated automatically.")
                
                # Instead of using disabled parameter, we'll use a callback to handle edits
                edited_matrix_df = st.data_editor(
                    matrix_df,
                    key="criteria_matrix_editor"
                )
                
                # Update the criteria matrix with edited values, but only from the upper triangle
                for i in range(n_criteria):
                    for j in range(i+1, n_criteria):
                        value = edited_matrix_df.iloc[i, j]
                        criteria_matrix[i, j] = value
                        criteria_matrix[j, i] = 1 / value
                
                # Display the complete matrix with lower triangle calculated
                complete_matrix = edited_matrix_df.copy()
                for i in range(n_criteria):
                    for j in range(i):
                        complete_matrix.iloc[i, j] = 1 / complete_matrix.iloc[j, i] if complete_matrix.iloc[j, i] != 0 else 0
                
                st.write("Complete matrix with calculated lower triangle:")
                st.dataframe(complete_matrix)
            
            st.session_state.criteria_matrix = criteria_matrix
            
            # Calculate and display weights and consistency ratio
            criteria_weights = calculate_weights(criteria_matrix)
            cr_criteria = calculate_consistency_ratio(criteria_matrix, criteria_weights)
            
            # Create a DataFrame for criteria weights
            weights_df = pd.DataFrame({
                get_text("criterion"): st.session_state.criteria,
                get_text("weight"): [format_decimal(w) for w in criteria_weights]
            })
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(get_text("criteria_weights"))
                st.dataframe(weights_df, hide_index=True)
            
            with col2:
                st.subheader(get_text("consistency_ratios"))
                st.write(f"{get_text('consistency_ratio_for')} {get_text('criteria')}: {format_decimal(cr_criteria)}")
                
                # Display message about consistency
                valid_consistency, message = validate_matrix_consistency(cr_criteria)
                if valid_consistency:
                    st.success(get_text("consistency_acceptable"))
                else:
                    st.error(message)
            
            # Store the calculated values in session state
            if 'temp_criteria_weights' not in st.session_state:
                st.session_state.temp_criteria_weights = {}
            st.session_state.temp_criteria_weights['criteria'] = criteria_weights
            
            if 'temp_consistency_ratios' not in st.session_state:
                st.session_state.temp_consistency_ratios = {}
            st.session_state.temp_consistency_ratios['criteria'] = cr_criteria
            
            # Track consistency status and provide navigation
            valid_consistency, _ = validate_matrix_consistency(cr_criteria)
            st.session_state.matrix_consistency['criteria'] = valid_consistency
            
            # Add navigation button if matrix is consistent
            st.markdown("---")
            if valid_consistency and len(st.session_state.criteria) > 0:
                if st.button("Next: " + tab_titles[1], type="primary", key="next_criteria"):
                    st.session_state.current_matrix_tab = 1
                    st.rerun()
            else:
                st.warning("Please ensure the consistency ratio is acceptable (< 0.1) before proceeding.")
        
        # Alternative comparison tabs for each criterion
        for criterion_idx, criterion in enumerate(st.session_state.criteria):
            with matrix_tabs[criterion_idx + 1]:
                input_method = st.radio(
                    "Input Method",
                    options=[get_text("dropdown_input"), get_text("manual_input")],
                    horizontal=True,
                    key=f"alt_input_method_{criterion_idx}"
                )
                
                alternative_matrix = st.session_state.alternative_matrices[criterion]
                n_alternatives = len(st.session_state.alternatives)
                
                if input_method == get_text("dropdown_input"):
                    # Display alternative matrix as a form with dropdowns
                    for i in range(n_alternatives):
                        for j in range(i+1, n_alternatives):
                            col1, col2, col3 = st.columns([2, 1, 2])
                            with col1:
                                st.write(st.session_state.alternatives[i])
                            with col2:
                                value = st.selectbox(
                                    f"{get_text('compare')} {st.session_state.alternatives[i]} {get_text('vs')} {st.session_state.alternatives[j]} {get_text('for')} {criterion}",
                                    options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 1/2, 1/3, 1/4, 1/5, 1/6, 1/7, 1/8, 1/9],
                                    format_func=lambda x: f"{x} - {get_saaty_scale_description(int(x), st.session_state.language) if x >= 1 else f'1/{int(1/x)} - {get_text('inverse_of')} {get_saaty_scale_description(int(1/x), st.session_state.language)}'}",
                                    key=f"alt_{criterion_idx}_{i}_{j}",
                                    index=0
                                )
                                alternative_matrix[i, j] = value
                                alternative_matrix[j, i] = 1 / value
                            with col3:
                                st.write(st.session_state.alternatives[j])
                else:  # Manual input
                    # Create a DataFrame for manual input
                    matrix_df = pd.DataFrame(
                        data=np.zeros((n_alternatives, n_alternatives)),
                        columns=st.session_state.alternatives,
                        index=st.session_state.alternatives
                    )
                    
                    # Fill the diagonal with 1s
                    for i in range(n_alternatives):
                        matrix_df.iloc[i, i] = 1.0
                    
                    # Fill the upper triangle with current values
                    for i in range(n_alternatives):
                        for j in range(i+1, n_alternatives):
                            matrix_df.iloc[i, j] = alternative_matrix[i, j]
                    
                    # Create an editable dataframe
                    st.write("Enter values in the upper triangle only. Lower triangle will be calculated automatically.")
                    
                    # Instead of using disabled parameter, we'll use a callback to handle edits
                    edited_matrix_df = st.data_editor(
                        matrix_df,
                        key=f"alt_matrix_editor_{criterion_idx}"
                    )
                    
                    # Update the alternative matrix with edited values, but only from the upper triangle
                    for i in range(n_alternatives):
                        for j in range(i+1, n_alternatives):
                            value = edited_matrix_df.iloc[i, j]
                            alternative_matrix[i, j] = value
                            alternative_matrix[j, i] = 1 / value
                    
                    # Display the complete matrix with lower triangle calculated
                    complete_matrix = edited_matrix_df.copy()
                    for i in range(n_alternatives):
                        for j in range(i):
                            complete_matrix.iloc[i, j] = 1 / complete_matrix.iloc[j, i] if complete_matrix.iloc[j, i] != 0 else 0
                    
                    st.write("Complete matrix with calculated lower triangle:")
                    st.dataframe(complete_matrix)
                
                st.session_state.alternative_matrices[criterion] = alternative_matrix
                
                # Calculate and display weights and consistency ratio
                alt_weights = calculate_weights(alternative_matrix)
                cr_alt = calculate_consistency_ratio(alternative_matrix, alt_weights)
                
                # Create a DataFrame for alternative weights
                weights_df = pd.DataFrame({
                    get_text("alternative"): st.session_state.alternatives,
                    get_text("weight"): [format_decimal(w) for w in alt_weights]
                })
                
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader(f"{get_text('weights_for')} {criterion}")
                    st.dataframe(weights_df, hide_index=True)
                
                with col2:
                    st.subheader(get_text("consistency_ratios"))
                    st.write(f"{get_text('consistency_ratio_for')} {criterion}: {format_decimal(cr_alt)}")
                    
                    # Display message about consistency
                    valid_consistency, message = validate_matrix_consistency(cr_alt)
                    if valid_consistency:
                        st.success(get_text("consistency_acceptable"))
                    else:
                        st.error(message)
                
                # Store the calculated values in session state
                if 'temp_alternative_weights' not in st.session_state:
                    st.session_state.temp_alternative_weights = {}
                st.session_state.temp_alternative_weights[criterion] = alt_weights
                
                if 'temp_consistency_ratios' not in st.session_state:
                    st.session_state.temp_consistency_ratios = {}
                st.session_state.temp_consistency_ratios[criterion] = cr_alt
                
                # Track consistency status and provide navigation
                valid_consistency, _ = validate_matrix_consistency(cr_alt)
                st.session_state.matrix_consistency[criterion] = valid_consistency
                
                # Add navigation buttons
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                current_tab_index = criterion_idx + 1
                with col1:
                    if current_tab_index > 1:
                        prev_criterion = st.session_state.criteria[criterion_idx - 1]
                        if st.button(f"Previous: {get_text('alternative_comparison')} {prev_criterion}", key=f"prev_{criterion_idx}"):
                            st.session_state.current_matrix_tab = current_tab_index - 1
                            st.rerun()
                
                with col2:
                    # If this is not the last tab and the current matrix is consistent
                    if valid_consistency and current_tab_index < len(tab_titles) - 1:
                        next_criterion = st.session_state.criteria[criterion_idx + 1]
                        if st.button(f"Next: {get_text('alternative_comparison')} {next_criterion}", type="primary", key=f"next_{criterion_idx}"):
                            st.session_state.current_matrix_tab = current_tab_index + 1
                            st.rerun()
                
                if not valid_consistency:
                    st.warning("Please ensure the consistency ratio is acceptable (< 0.1) before proceeding.")
        
        # Calculate results button
        st.markdown("---")
        if st.button(get_text("calculate_results"), type="primary"):
            # Check consistency ratios for all matrices
            all_consistent = True
            inconsistent_matrices = []
            
            # Check criteria matrix
            if 'matrix_consistency' in st.session_state and 'criteria' in st.session_state.matrix_consistency:
                valid_criteria = st.session_state.matrix_consistency['criteria']
                if not valid_criteria:
                    all_consistent = False
                    inconsistent_matrices.append(get_text("criteria_comparison"))
            else:
                # Fallback to direct calculation if matrix_consistency not set
                if 'temp_consistency_ratios' in st.session_state and 'criteria' in st.session_state.temp_consistency_ratios:
                    cr_criteria = st.session_state.temp_consistency_ratios['criteria']
                    valid_criteria, _ = validate_matrix_consistency(cr_criteria)
                    if not valid_criteria:
                        all_consistent = False
                        inconsistent_matrices.append(get_text("criteria_comparison"))
            
            # Check alternative matrices for each criterion
            for criterion in st.session_state.criteria:
                if 'matrix_consistency' in st.session_state and criterion in st.session_state.matrix_consistency:
                    valid_alt = st.session_state.matrix_consistency[criterion]
                    if not valid_alt:
                        all_consistent = False
                        inconsistent_matrices.append(f"{get_text('alternative_comparison')} {criterion}")
                elif ('temp_consistency_ratios' in st.session_state and 
                    criterion in st.session_state.temp_consistency_ratios):
                    cr_alt = st.session_state.temp_consistency_ratios[criterion]
                    valid_alt, _ = validate_matrix_consistency(cr_alt)
                    if not valid_alt:
                        all_consistent = False
                        inconsistent_matrices.append(f"{get_text('alternative_comparison')} {criterion}")
            
            if all_consistent:
                # Calculate all results
                results = calculate_all_results(
                    st.session_state.criteria_matrix,
                    st.session_state.alternative_matrices,
                    st.session_state.criteria,
                    st.session_state.alternatives
                )
                
                # Store results in session state
                st.session_state.criteria_weights = results['criteria_weights']
                st.session_state.alternative_weights = results['alternative_weights']
                st.session_state.final_scores = results['final_scores']
                st.session_state.consistency_ratios = results['consistency_ratios']
                
                # Save results to database
                save_results()
                
                st.success(get_text("results_calculated"))
            else:
                # Show error message with inconsistent matrices
                error_msg = get_text("error_consistency_ratio") + "\n" + ", ".join(inconsistent_matrices)
                st.error(error_msg)
    else:
        st.info(get_text("initialize_first"))