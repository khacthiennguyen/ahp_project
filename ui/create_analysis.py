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
        session_name = st.text_input(
            get_text("analysis_name"), 
            key="session_name",
            placeholder="Nhập tên phân tích...(bắt buộc)",
            help="Tên phân tích là bắt buộc để tạo phiên làm việc"
        )
        
        session_description = st.text_area(
            get_text("description"), 
            key="session_description",
            placeholder="Mô tả chi tiết về phân tích (tùy chọn)..."
        )
    
    # with col2:
    #     st.info(get_text("step_1"))
    
    st.header(get_text("step_2"))
    
    # Criteria section with improved UI
    col1, col2 = st.columns(2)
    
    with col1:
        # Initialize clear flag for criteria text area
        if 'clear_criteria_input' not in st.session_state:
            st.session_state.clear_criteria_input = False
            
        # Reset text area value if clear flag is set
        criteria_value = "" if st.session_state.clear_criteria_input else None
        
        # Replace single-line input with multi-line text area for batch input
        new_criteria_batch = st.text_area(
            get_text("add_criterion_batch"),
            placeholder="Tiêu chí 1\nTiêu chí 2\nTiêu chí 3",
            help="Nhập mỗi tiêu chí trên một dòng để thêm nhiều tiêu chí cùng lúc (Tối đa 9 tiêu chí)",
            value=criteria_value,
            key="criteria_input"
        )
        
        add_criterion_clicked = st.button(get_text("add_criterion_button"))
        
        if add_criterion_clicked and new_criteria_batch:
            # Split the text by newlines to get individual criteria
            criteria_list = [c.strip() for c in new_criteria_batch.split('\n') if c.strip()]
            
            # Check current count and validate limits
            current_count = len(st.session_state.criteria)
            added_count = 0
            rejected_count = 0
            rejected_items = []
            
            # Process each criterion with limit check
            for criterion in criteria_list:
                # Check if adding this criterion would exceed the limit
                if current_count + added_count >= 9:
                    rejected_count += 1
                    rejected_items.append(criterion)
                    continue
                
                valid, message = validate_name(criterion, st.session_state.criteria)
                if valid:
                    st.session_state.criteria.append(criterion)
                    added_count += 1
                else:
                    st.error(f"{criterion}: {message}")
            
            # Show results
            if added_count > 0:
                st.toast(f"Đã thêm {added_count} tiêu chí thành công!", icon="✅")
                # Set flag to clear text area on next run
                st.session_state.clear_criteria_input = True
                st.rerun()
            
            # Show warning for rejected items
            if rejected_count > 0:
                st.toast(f"Giới hạn tối đa 9 tiêu chí!", icon="⚠️")
        
        # Reset clear flag after text area is rendered
        if st.session_state.clear_criteria_input:
            st.session_state.clear_criteria_input = False
    
    with col2:
        st.subheader(get_text("current_criteria"))
        
        if st.session_state.criteria:
            # Initialize editing state for criteria
            if 'editing_criterion_index' not in st.session_state:
                st.session_state.editing_criterion_index = None
            if 'edit_criterion_text' not in st.session_state:
                st.session_state.edit_criterion_text = ""
            
            # Display criteria as tags/cards
            st.markdown(f"**Tổng số: {len(st.session_state.criteria)} tiêu chí**")
            
            # Create CSS for beautiful tags
            st.markdown("""
            <style>
            .criterion-tag {
                display: inline-block;
                background: linear-gradient(45deg, #4CAF50, #45a049);
                color: white;
                padding: 8px 12px;
                margin: 4px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 500;
                box-shadow: 0 2px 6px rgba(0,0,0,0.15);
                transition: all 0.3s ease;
                position: relative;
                cursor: pointer;
                border: none;
                min-width: 80px;
                text-align: center;
            }
            .criterion-tag:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                background: linear-gradient(45deg, #45a049, #4CAF50);
            }
            .delete-icon {
                background: #ff4444;
                color: white;
                border-radius: 50%;
                width: 20px;
                height: 20px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: bold;
                margin-left: 8px;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            .delete-icon:hover {
                background: #cc0000;
                transform: scale(1.1);
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Display tags in a grid
            for i, criterion in enumerate(st.session_state.criteria):
                # Check if this criterion is being edited
                if st.session_state.editing_criterion_index == i:
                    # Show edit input
                    new_name = st.text_input(
                        f"Chỉnh sửa tiêu chí {i+1}:",
                        value=st.session_state.edit_criterion_text,
                        key=f"edit_criterion_{i}",
                        placeholder="Nhập tên tiêu chí mới..."
                    )
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.button("💾 Lưu", key=f"save_criterion_{i}", type="primary"):
                            if new_name and new_name.strip():
                                # Validate new name
                                other_criteria = [c for j, c in enumerate(st.session_state.criteria) if j != i]
                                valid, message = validate_name(new_name.strip(), other_criteria)
                                if valid:
                                    st.session_state.criteria[i] = new_name.strip()
                                    st.session_state.editing_criterion_index = None
                                    st.session_state.edit_criterion_text = ""
                                    st.toast(f"✅ Đã cập nhật tiêu chí: {new_name.strip()}", icon="✅")
                                    st.rerun()
                                else:
                                    st.error(message)
                            else:
                                st.error("Tên tiêu chí không được để trống")
                    
                    with col_cancel:
                        if st.button("❌ Hủy", key=f"cancel_criterion_{i}"):
                            st.session_state.editing_criterion_index = None
                            st.session_state.edit_criterion_text = ""
                            st.rerun()
                else:
                    # Show tag with edit and delete buttons in same row
                    col_edit, col_delete = st.columns([8, 1])
                    
                    with col_edit:
                        if st.button(f"✏️ {criterion}", 
                                   key=f"edit_btn_criterion_{i}",
                                   help=f"Click để chỉnh sửa: {criterion}"):
                            st.session_state.editing_criterion_index = i
                            st.session_state.edit_criterion_text = criterion
                            st.rerun()
                    
                    with col_delete:
                        if st.button("🗑️", 
                                   key=f"delete_criterion_{i}",
                                   help=f"Xóa tiêu chí: {criterion}",
                                   type="secondary"):
                            st.session_state.criteria.remove(criterion)
                            st.toast(f"🗑️ Đã xóa tiêu chí: {criterion}", icon="🗑️")
                            st.rerun()
        else:
            st.info(get_text("add_criterion"))
    
    st.header(get_text("step_3"))
    
    # Alternatives section with improved UI
    col1, col2 = st.columns(2)
    
    with col1:
        # Initialize clear flag for alternatives text area
        if 'clear_alternatives_input' not in st.session_state:
            st.session_state.clear_alternatives_input = False
            
        # Reset text area value if clear flag is set
        alternatives_value = "" if st.session_state.clear_alternatives_input else None
        
        # Replace single-line input with multi-line text area for batch input
        new_alternatives_batch = st.text_area(
            get_text("add_alternative_batch"),
            placeholder="Phương án 1\nPhương án 2\nPhương án 3",
            help="Nhập mỗi phương án trên một dòng để thêm nhiều phương án cùng lúc (Tối đa 15 phương án)",
            value=alternatives_value,
            key="alternatives_input"
        )
        
        add_alternative_clicked = st.button(get_text("add_alternative_button"))
        
        if add_alternative_clicked and new_alternatives_batch:
            # Split the text by newlines to get individual alternatives
            alternatives_list = [a.strip() for a in new_alternatives_batch.split('\n') if a.strip()]
            
            # Check current count and validate limits
            current_count = len(st.session_state.alternatives)
            added_count = 0
            rejected_count = 0
            rejected_items = []
            
            # Process each alternative with limit check
            for alternative in alternatives_list:
                # Check if adding this alternative would exceed the limit
                if current_count + added_count >= 15:
                    rejected_count += 1
                    rejected_items.append(alternative)
                    continue
                
                valid, message = validate_name(alternative, st.session_state.alternatives)
                if valid:
                    st.session_state.alternatives.append(alternative)
                    added_count += 1
                else:
                    st.error(f"{alternative}: {message}")
            
            # Show results
            if added_count > 0:
                st.toast(f"Đã thêm {added_count} phương án thành công!", icon="✅")
                # Set flag to clear text area on next run
                st.session_state.clear_alternatives_input = True
                st.rerun()
            
            # Show warning for rejected items
            if rejected_count > 0:
                st.toast(f"Giới hạn tối đa 15 phương án!", icon="⚠️")
        
        # Reset clear flag after text area is rendered
        if st.session_state.clear_alternatives_input:
            st.session_state.clear_alternatives_input = False
    
    with col2:
        st.subheader(get_text("current_alternatives"))
        
        if st.session_state.alternatives:
            # Initialize editing state for alternatives
            if 'editing_alternative_index' not in st.session_state:
                st.session_state.editing_alternative_index = None
            if 'edit_alternative_text' not in st.session_state:
                st.session_state.edit_alternative_text = ""
            
            # Display alternatives as tags/cards
            st.markdown(f"**Tổng số: {len(st.session_state.alternatives)} phương án**")
            
            # Create CSS for beautiful alternative tags
            st.markdown("""
            <style>
            .alternative-tag {
                display: inline-block;
                background: linear-gradient(45deg, #2196F3, #1976D2);
                color: white;
                padding: 8px 12px;
                margin: 4px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 500;
                box-shadow: 0 2px 6px rgba(0,0,0,0.15);
                transition: all 0.3s ease;
                position: relative;
                cursor: pointer;
                border: none;
                min-width: 80px;
                text-align: center;
            }
            .alternative-tag:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                background: linear-gradient(45deg, #1976D2, #2196F3);
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Display tags in a grid
            for i, alternative in enumerate(st.session_state.alternatives):
                # Check if this alternative is being edited
                if st.session_state.editing_alternative_index == i:
                    # Show edit input (use full width when editing)
                    new_name = st.text_input(
                        f"Chỉnh sửa phương án {i+1}:",
                        value=st.session_state.edit_alternative_text,
                        key=f"edit_alternative_{i}",
                        placeholder="Nhập tên phương án mới..."
                    )
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.button("💾 Lưu", key=f"save_alternative_{i}", type="primary"):
                            if new_name and new_name.strip():
                                # Validate new name
                                other_alternatives = [a for j, a in enumerate(st.session_state.alternatives) if j != i]
                                valid, message = validate_name(new_name.strip(), other_alternatives)
                                if valid:
                                    st.session_state.alternatives[i] = new_name.strip()
                                    st.session_state.editing_alternative_index = None
                                    st.session_state.edit_alternative_text = ""
                                    st.toast(f"Đã cập nhật phương án: {new_name.strip()}", icon="✅")
                                    st.rerun()
                                else:
                                    st.error(message)
                            else:
                                st.error("Tên phương án không được để trống")
                    
                    with col_cancel:
                        if st.button("❌ Hủy", key=f"cancel_alternative_{i}"):
                            st.session_state.editing_alternative_index = None
                            st.session_state.edit_alternative_text = ""
                            st.rerun()
                else:
                    # Show tag with edit and delete buttons in same row
                    col_edit, col_delete = st.columns([8, 1])
                    
                    with col_edit:
                        if st.button(f"✏️ {alternative}", 
                                   key=f"edit_btn_alternative_{i}",
                                   help=f"Click để chỉnh sửa: {alternative}"):
                            st.session_state.editing_alternative_index = i
                            st.session_state.edit_alternative_text = alternative
                            st.rerun()
                    
                    with col_delete:
                        if st.button("🗑️", 
                                   key=f"delete_alternative_{i}",
                                   help=f"Xóa phương án: {alternative}",
                                   type="secondary"):
                            st.session_state.alternatives.remove(alternative)
                            st.toast(f"Đã xóa phương án: {alternative}", icon="🗑️")
                            st.rerun()
        else:
            st.info(get_text("add_alternative"))
    
    # Initialize matrices button with validation
    st.markdown("---")
    
    # Clear any temporary calculations when re-initializing
    criteria_count = len(st.session_state.criteria)
    alternatives_count = len(st.session_state.alternatives)
    if 'temp_criteria_weights' in st.session_state:
        del st.session_state.temp_criteria_weights
    if 'temp_alternative_weights' in st.session_state:
        del st.session_state.temp_alternative_weights
    if 'temp_consistency_ratios' in st.session_state:
        del st.session_state.temp_consistency_ratios
    
    # Initialize matrices button with enhanced validation
    is_name_empty = not session_name or not session_name.strip()
    init_button = st.button(
        get_text("initialize_matrices"), 
        type="primary", 
        disabled=(criteria_count < 2 or alternatives_count < 2 or is_name_empty)
    )
    
    if init_button:
        # Check if analysis name is provided (this shouldn't happen due to disabled state, but just in case)
        if is_name_empty:
            st.toast("⚠️ Vui lòng nhập tên phân tích!", icon="⚠️")
            return
        
        valid, message = validate_analysis_setup()
        if valid:
            n_criteria = len(st.session_state.criteria)
            st.session_state.criteria_matrix = np.ones((n_criteria, n_criteria))
            
            # Initialize alternative matrices for each criterion
            st.session_state.alternative_matrices = {}
            for criterion in st.session_state.criteria:
                n_alternatives = len(st.session_state.alternatives)
                st.session_state.alternative_matrices[criterion] = np.ones((n_alternatives, n_alternatives))
            
            st.session_state.current_session_name = session_name.strip()
            st.session_state.current_session_description = session_description
            
            # Set flag to switch to input matrices tab
            st.session_state.switch_to_input_tab = True
            
            # Show success message
            st.toast("✅ Ma trận đã được khởi tạo thành công!", icon="✅")
            
            # Trigger rerun to activate tab switch
            st.rerun()
        else:
            st.error(message)
    
    # Show error messages for validation
    error_messages = []
    
    if is_name_empty:
        error_messages.append("- Cần nhập tên phân tích")
    
    if criteria_count < 2:
        error_messages.append("- Cần ít nhất 2 tiêu chí")
        
    if alternatives_count < 2:
        error_messages.append("- Cần ít nhất 2 phương án")
    
    if error_messages:
        st.error("❌ **Cần hoàn thành các yêu cầu sau:**\n\n" + "\n".join(error_messages))