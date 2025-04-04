import streamlit as st
import numpy as np
import pandas as pd
from utils.i18n import get_text
from ahp import get_saaty_scale_description, calculate_all_results
from db import save_results
from utils.formatting import format_decimal

def show_input_matrices():
    """Show the input matrices UI"""
    if st.session_state.criteria_matrix is not None:
        st.header(get_text("pairwise_comparison"))
        st.info(get_text("saaty_scale_info"))
        
        # Create tabs for criteria and each alternative comparison
        tab_titles = [get_text("criteria_comparison")]
        for criterion in st.session_state.criteria:
            tab_titles.append(f"{get_text('alternative_comparison')} {criterion}")
        
        matrix_tabs = st.tabs(tab_titles)
        
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
        
        # Calculate results button
        st.markdown("---")
        if st.button(get_text("calculate_results"), type="primary"):
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
        st.info(get_text("initialize_first"))