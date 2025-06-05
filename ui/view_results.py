import streamlit as st
import pandas as pd
import numpy as np
from utils.i18n import get_text
from db import get_past_sessions, get_session_data
from utils.formatting import format_decimal, format_percentage
import io
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from utils.export_utils import export_to_excel, export_to_pdf

def show_view_results():
    """Show the view results UI"""
    st.header(get_text("view_results"))
    
    # Option to view current results or past results
    view_option = st.radio(
        "Select view option:",
        [get_text("current_results"), get_text("past_results")],
        horizontal=True
    )
    
    if view_option == get_text("current_results"):
        show_current_results()
    else:  # Past Results
        show_past_results()

def show_current_results():
    """Show current results"""
    if st.session_state.final_scores is not None:
        # Create a 3-column layout for better organization
        col1, col2 = st.columns(2)
        
        # Column 1: Criteria Weights and Consistency Ratios
        with col1:
            # Display criteria weights - Use decimal format instead of percentage
            st.subheader(get_text("criteria_weights"))
            criteria_weights_df = pd.DataFrame({
                get_text("criterion"): st.session_state.criteria,
                get_text("weight"): [format_decimal(w) for w in st.session_state.criteria_weights]
            })
            criteria_weights_df = criteria_weights_df.sort_values(get_text("weight"), ascending=False)
            
            # Apply styling to the dataframe
            st.dataframe(
                criteria_weights_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Display consistency metrics
            st.subheader(get_text("consistency_metrics"))
            st.write(f"λ_max: {format_decimal(st.session_state.lambda_max_values['criteria'])}")
            st.write(f"CI: {format_decimal(st.session_state.consistency_indices['criteria'])}")
            st.write(f"CR: {format_decimal(st.session_state.consistency_ratios['criteria'])}")
            st.write(get_text("consistency_acceptable"))
            
            # Create a dataframe for consistency metrics
            cr_data = {
                get_text("criterion"): [],
                "λ_max": [],
                "CI": [],
                "CR": []
            }
            
            for criterion in st.session_state.criteria:
                cr_data[get_text("criterion")].append(criterion)
                cr_data["λ_max"].append(format_decimal(st.session_state.lambda_max_values[criterion]))
                cr_data["CI"].append(format_decimal(st.session_state.consistency_indices[criterion]))
                cr_data["CR"].append(format_decimal(st.session_state.consistency_ratios[criterion]))
            
            cr_df = pd.DataFrame(cr_data)
            st.dataframe(
                cr_df,
                use_container_width=True,
                hide_index=True
            )
        
        # Column 2: Alternative Weights by Criterion
        with col2:
            st.subheader(get_text("alternative_weights_by_criterion"))
            
            # Create tabs for each criterion
            criterion_tabs = st.tabs(st.session_state.criteria)
            
            for i, criterion in enumerate(st.session_state.criteria):
                with criterion_tabs[i]:
                    # Use decimal format instead of percentage for alternative weights
                    alt_weights_df = pd.DataFrame({
                        get_text("alternative"): st.session_state.alternatives,
                        get_text("weight"): [format_decimal(w) for w in st.session_state.alternative_weights[criterion]]
                    })
                    alt_weights_df = alt_weights_df.sort_values(get_text("weight"), ascending=False)
                    # Apply styling to the dataframe
                    st.dataframe(
                        alt_weights_df,
                        use_container_width=True,
                        hide_index=True
                    )
                    # Hiển thị chỉ số nhất quán của bảng phương án theo tiêu chí nếu có
                    if (
                        hasattr(st.session_state, 'lambda_max_values') and
                        hasattr(st.session_state, 'consistency_indices') and
                        hasattr(st.session_state, 'consistency_ratios') and
                        criterion in st.session_state.lambda_max_values and
                        criterion in st.session_state.consistency_indices and
                        criterion in st.session_state.consistency_ratios
                    ):
                        st.markdown(f"**Chỉ số nhất quán cho bảng phương án theo tiêu chí '{criterion}':**")
                        st.write(f"λ_max: {format_decimal(st.session_state.lambda_max_values[criterion])}")
                        st.write(f"CI: {format_decimal(st.session_state.consistency_indices[criterion])}")
                        st.write(f"CR: {format_decimal(st.session_state.consistency_ratios[criterion])}")
        
        # Final Scores and Ranking (full width) - Keep percentage format
        st.markdown("---")
        st.subheader(get_text("final_scores"))
        final_scores_df = pd.DataFrame({
            get_text("alternative"): st.session_state.alternatives,
            get_text("score"): [format_percentage(s) for s in st.session_state.final_scores]
        })
        final_scores_df = final_scores_df.sort_values(get_text("score"), ascending=False)
        final_scores_df[get_text("rank")] = range(1, len(final_scores_df) + 1)
        
        # Apply styling to the dataframe
        st.dataframe(
            final_scores_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Visualization
        st.subheader(get_text("visualization"))
        
        # Convert percentage strings back to floats for the chart
        chart_data = pd.DataFrame({
            'Alternative': st.session_state.alternatives,
            'Score': st.session_state.final_scores
        })
        chart_data = chart_data.sort_values('Score', ascending=False)
        
        st.bar_chart(chart_data.set_index('Alternative')['Score'])
        
        # Add export functionality
        st.markdown("---")
        st.subheader(get_text("export_results"))
        
        col1, col2 = st.columns(2)
        with col1:
            # Export to Excel
            excel_data = export_to_excel(None, is_current=True, st=st)
            st.download_button(
                label=get_text("export_excel"),
                data=excel_data,
                file_name="ahp_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        
        with col2:
            # Export to PDF
            pdf_data = export_to_pdf(None, is_current=True, st=st)
            st.download_button(
                label=get_text("export_pdf"),
                data=pdf_data,
                file_name="ahp_results.pdf",
                mime="application/pdf",
            )
    else:
        st.info(get_text("no_results"))

def show_past_results():
    """Show past results"""
    # Fetch past sessions from database
    past_sessions = get_past_sessions()
    
    if past_sessions:
        session_options = [f"{session[1]} ({session[2]})" for session in past_sessions]
        session_ids = [session[0] for session in past_sessions]
        
        selected_session_idx = st.selectbox(
            get_text("select_past_analysis"),
            range(len(session_options)),
            format_func=lambda x: session_options[x]
        )
        selected_session_id = session_ids[selected_session_idx]
        
        # Fetch selected session data
        session_data = get_session_data(selected_session_id)
        
        if session_data:
            # Display session info
            st.subheader(f"{get_text('analysis')}: {session_data['name']}")
            st.write(f"{get_text('description')}: {session_data['description']}")
            st.write(f"{get_text('date')}: {session_data['timestamp']}")
            
            # Create a 3-column layout for better organization
            col1, col2 = st.columns(2)
            
            # Column 1: Criteria Weights and Consistency Ratios
            with col1:
                # Display criteria weights - Use decimal format instead of percentage
                st.subheader(get_text("criteria_weights"))
                criteria_weights_df = pd.DataFrame({
                    get_text("criterion"): session_data['criteria'],
                    get_text("weight"): [format_decimal(w) for w in session_data['criteria_weights']]
                })
                criteria_weights_df = criteria_weights_df.sort_values(get_text("weight"), ascending=False)
                
                # Apply styling to the dataframe
                st.dataframe(
                    criteria_weights_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Display consistency metrics
                st.subheader(get_text("consistency_metrics"))
                if 'lambda_max_values' in session_data and 'consistency_indices' in session_data:
                    st.write(f"λ_max: {format_decimal(session_data['lambda_max_values']['criteria'])}")
                    st.write(f"CI: {format_decimal(session_data['consistency_indices']['criteria'])}")
                    st.write(f"CR: {format_decimal(session_data['consistency_ratios']['criteria'])}")
                else:
                    st.write(f"CR: {format_decimal(session_data['consistency_ratios']['criteria'])}")
                st.write(get_text("consistency_acceptable"))
                
                # Create a dataframe for consistency metrics
                cr_data = {
                    get_text("criterion"): [],
                }
                
                if 'lambda_max_values' in session_data and 'consistency_indices' in session_data:
                    cr_data["λ_max"] = []
                    cr_data["CI"] = []
                    cr_data["CR"] = []
                else:
                    cr_data[get_text("consistency_ratio_for")] = []
                
                for criterion in session_data['criteria']:
                    cr_data[get_text("criterion")].append(criterion)
                    if 'lambda_max_values' in session_data and 'consistency_indices' in session_data:
                        cr_data["λ_max"].append(format_decimal(session_data['lambda_max_values'][criterion]))
                        cr_data["CI"].append(format_decimal(session_data['consistency_indices'][criterion]))
                        cr_data["CR"].append(format_decimal(session_data['consistency_ratios'][criterion]))
                    else:
                        cr_data[get_text("consistency_ratio_for")].append(format_decimal(session_data['consistency_ratios'][criterion]))
                
                cr_df = pd.DataFrame(cr_data)
                st.dataframe(
                    cr_df,
                    use_container_width=True,
                    hide_index=True
                )
            
            # Column 2: Alternative Weights by Criterion
            with col2:
                st.subheader(get_text("alternative_weights_by_criterion"))
                
                # Create tabs for each criterion
                criterion_tabs = st.tabs(session_data['criteria'])
                
                for i, criterion in enumerate(session_data['criteria']):
                    with criterion_tabs[i]:
                        # Use decimal format instead of percentage for alternative weights
                        alt_weights_df = pd.DataFrame({
                            get_text("alternative"): session_data['alternatives'],
                            get_text("weight"): [format_decimal(w) for w in session_data['alternative_weights'][criterion]]
                        })
                        alt_weights_df = alt_weights_df.sort_values(get_text("weight"), ascending=False)
                        
                        # Apply styling to the dataframe
                        st.dataframe(
                            alt_weights_df,
                            use_container_width=True,
                            hide_index=True
                        )
                        # Hiển thị chỉ số nhất quán của bảng phương án theo tiêu chí nếu có
                        if (
                            'lambda_max_values' in session_data and
                            'consistency_indices' in session_data and
                            'consistency_ratios' in session_data and
                            criterion in session_data['lambda_max_values'] and
                            criterion in session_data['consistency_indices'] and
                            criterion in session_data['consistency_ratios']
                        ):
                            st.markdown(f"**Chỉ số nhất quán cho bảng phương án theo tiêu chí '{criterion}':**")
                            st.write(f"λ_max: {format_decimal(session_data['lambda_max_values'][criterion])}")
                            st.write(f"CI: {format_decimal(session_data['consistency_indices'][criterion])}")
                            st.write(f"CR: {format_decimal(session_data['consistency_ratios'][criterion])}")
            
            # Final Scores and Ranking (full width) - Keep percentage format
            st.markdown("---")
            st.subheader(get_text("final_scores"))
            final_scores_df = pd.DataFrame({
                get_text("alternative"): session_data['alternatives'],
                get_text("score"): [format_percentage(s) for s in session_data['final_scores']]
            })
            final_scores_df = final_scores_df.sort_values(get_text("score"), ascending=False)
            final_scores_df[get_text("rank")] = range(1, len(final_scores_df) + 1)
            
            # Apply styling to the dataframe
            st.dataframe(
                final_scores_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Visualization
            st.subheader(get_text("visualization"))
            
            # Convert percentage strings back to floats for the chart
            chart_data = pd.DataFrame({
                'Alternative': session_data['alternatives'],
                'Score': session_data['final_scores']
            })
            chart_data = chart_data.sort_values('Score', ascending=False)
            
            st.bar_chart(chart_data.set_index('Alternative')['Score'])
            
            # Add export functionality
            st.markdown("---")
            st.subheader(get_text("export_results"))
            
            col1, col2 = st.columns(2)
            with col1:
                # Export to Excel
                excel_data = export_to_excel(session_data, is_current=False, st=st)
                st.download_button(
                    label=get_text("export_excel"),
                    data=excel_data,
                    file_name=f"ahp_results_{session_data['id']}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            with col2:
                # Export to PDF
                pdf_data = export_to_pdf(session_data, is_current=False, st=st)
                st.download_button(
                    label=get_text("export_pdf"),
                    data=pdf_data,
                    file_name=f"ahp_results_{session_data['id']}.pdf",
                    mime="application/pdf",
                )
            # Nút xóa phân tích
            st.markdown("---")
            if st.button("🗑️ Xóa phân tích này", type="secondary"):
                from db import delete_session
                delete_session(session_data['id'])
                st.toast("Đã xóa phân tích thành công!", icon="✅")
                st.rerun()
    else:
        st.info(get_text("no_past_analyses"))