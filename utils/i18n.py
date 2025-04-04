import streamlit as st

# Dictionary of translations
translations = {
    "en": {
        # App general
        "app_title": "AHP Decision Support System",
        "reset_application": "Reset Application",
        "about_ahp": "Steps in AHP:",
        "ahp_description": """
        
        1. Define the problem and criteria
        2. Structure the decision hierarchy
        3. Construct pairwise comparison matrices
        4. Calculate weights and consistency ratios
        5. Synthesize results to find the best alternative
        
        Saaty Scale:
        - 1: Equal importance
        - 3: Moderate importance
        - 5: Strong importance
        - 7: Very strong importance
        - 9: Extreme importance
        - 2, 4, 6, 8: Intermediate values
        """,
        
        # Tabs
        "create_new_analysis": "Create New Analysis",
        "input_matrices": "Input Matrices",
        "view_results": "View Results",
        
        # Create Analysis
        "step_1": "Step 1: Define Problem",
        "analysis_name": "Analysis Name",
        "description": "Description",
        "step_2": "Step 2: Define Criteria",
        "add_criterion": "Add Criterion",
        "add_criterion_button": "Add Criterion",
        "current_criteria": "Current Criteria",
        "step_3": "Step 3: Define Alternatives",
        "add_alternative": "Add Alternative",
        "add_alternative_button": "Add Alternative",
        "current_alternatives": "Current Alternatives",
        "initialize_matrices": "Initialize Matrices",
        "error_empty_name": "Name cannot be empty",
        "error_duplicate_name": "Name already exists",
        "error_no_criteria_alternatives": "Please add at least one criterion and one alternative",
        "matrices_initialized": "Matrices initialized! Go to the 'Input Matrices' tab.",
        "edit": "Edit",
        "remove": "Remove",
        "save": "Save",
        "cancel": "Cancel",

        "add_criterion_batch": "Add Multiple Criteria (one per line)",
        "add_alternative_batch": "Add Multiple Alternatives (one per line)",
        "inverse_of": "Inverse of",
        
        # Input Matrices
        "pairwise_comparison": "Pairwise Comparison Matrices",
        "saaty_scale_info": "Use the Saaty scale (1-9) for comparisons. 1 = equal importance, 9 = extreme importance.",
        "criteria_comparison": "Criteria Comparison",
        "alternative_comparison": "Alternative Comparison for",
        "compare": "Compare",
        "vs": "vs",
        "for": "for",
        "calculate_results": "Calculate Results",
        "results_calculated": "Results calculated and saved! Go to the 'View Results' tab.",
        "initialize_first": "Please initialize matrices in the 'Create New Analysis' tab first.",
        "manual_input": "Manual Input",
        "dropdown_input": "Dropdown Input",
        
        # View Results
        "current_results": "Current Results",
        "past_results": "Past Results",
        "criteria_weights": "Criteria Weights",
        "consistency_ratios": "Consistency Ratios",
        "consistency_ratio_for": "Consistency Ratio for",
        "consistency_acceptable": "Consistency is acceptable if CR < 0.1",
        "alternative_weights_by_criterion": "Alternative Weights by Criterion",
        "weights_for": "Weights for",
        "final_scores": "Final Scores and Ranking",
        "visualization": "Visualization",
        "criterion": "Criterion",
        "weight": "Weight",
        "alternative": "Alternative",
        "score": "Score",
        "rank": "Rank",
        "select_past_analysis": "Select a past analysis:",
        "analysis": "Analysis",
        "date": "Date",
        "no_results": "No results to display. Please calculate results first.",
        "no_past_analyses": "No past analyses found."
    },
    "vi": {
        # App general
        "app_title": "Hệ Thống Hỗ Trợ Quyết Định AHP",
        "reset_application": "Reset",
        "about_ahp": "Các bước trong AHP",
        "ahp_description": """
        
        1. Xác định vấn đề và tiêu chí
        2. Cấu trúc hệ thống phân cấp quyết định
        3. Xây dựng ma trận so sánh cặp
        4. Tính toán trọng số và tỷ số nhất quán
        5. Tổng hợp kết quả để tìm phương án tốt nhất
        
        Thang đo Saaty:
        - 1: Tầm quan trọng bằng nhau
        - 3: Tầm quan trọng vừa phải
        - 5: Tầm quan trọng mạnh
        - 7: Tầm quan trọng rất mạnh
        - 9: Tầm quan trọng cực kỳ
        - 2, 4, 6, 8: Các giá trị trung gian
        """,
        "add_criterion_batch": "Thêm Nhiều Tiêu Chí (mỗi dòng một tiêu chí)",
        "add_alternative_batch": "Thêm Nhiều Phương Án (mỗi dòng một phương án)",\
        "inverse_of": "Nghịch đảo của",
        
        # Tabs
        "create_new_analysis": "Tạo Phân Tích Mới",
        "input_matrices": "Nhập Ma Trận",
        "view_results": "Xem Kết Quả",
        
        # Create Analysis
        "step_1": "Bước 1: Xác Định Vấn Đề",
        "analysis_name": "Tên Phân Tích",
        "description": "Mô Tả",
        "step_2": "Bước 2: Xác Định Tiêu Chí",
        "add_criterion": "Thêm Tiêu Chí",
        "add_criterion_button": "Thêm Tiêu Chí",
        "current_criteria": "Tiêu Chí Hiện Tại",
        "step_3": "Bước 3: Xác Định Phương Án",
        "add_alternative": "Thêm Phương Án",
        "add_alternative_button": "Thêm Phương Án",
        "current_alternatives": "Phương Án Hiện Tại",
        "initialize_matrices": "Khởi Tạo Ma Trận",
        "error_empty_name": "Tên không được để trống",
        "error_duplicate_name": "Tên đã tồn tại",
        "error_no_criteria_alternatives": "Vui lòng thêm ít nhất một tiêu chí và một phương án",
        "matrices_initialized": "Ma trận đã được khởi tạo! Chuyển đến tab 'Nhập Ma Trận'.",
        "edit": "Sửa",
        "remove": "Xóa",
        "save": "Lưu",
        "cancel": "Hủy",

        
        # Input Matrices
        "pairwise_comparison": "Ma Trận So Sánh Cặp",
        "saaty_scale_info": "Sử dụng thang đo Saaty (1-9) cho so sánh. 1 = tầm quan trọng bằng nhau, 9 = tầm quan trọng cực kỳ.",
        "criteria_comparison": "So Sánh Tiêu Chí",
        "alternative_comparison": "So Sánh Phương Án cho",
        "compare": "So sánh",
        "vs": "với",
        "for": "cho",
        "calculate_results": "Tính Toán Kết Quả",
        "results_calculated": "Kết quả đã được tính toán và lưu! Chuyển đến tab 'Xem Kết Quả'.",
        "initialize_first": "Vui lòng khởi tạo ma trận trong tab 'Tạo Phân Tích Mới' trước.",
        "manual_input": "Nhập Thủ Công",
        "dropdown_input": "Nhập Bằng Dropdown",
        
        # View Results
        "current_results": "Kết Quả Hiện Tại",
        "past_results": "Kết Quả Trước Đây",
        "criteria_weights": "Trọng Số Tiêu Chí",
        "consistency_ratios": "Tỷ Số Nhất Quán",
        "consistency_ratio_for": "Tỷ Số Nhất Quán cho",
        "consistency_acceptable": "Tính nhất quán được chấp nhận nếu CR < 0.1",
        "alternative_weights_by_criterion": "Trọng Số Phương Án Theo Tiêu Chí",
        "weights_for": "Trọng số cho",
        "final_scores": "Điểm Số Cuối Cùng và Xếp Hạng",
        "visualization": "Biểu Đồ",
        "criterion": "Tiêu Chí",
        "weight": "Trọng Số",
        "alternative": "Phương Án",
        "score": "Điểm",
        "rank": "Xếp Hạng",
        "select_past_analysis": "Chọn phân tích trước đây:",
        "analysis": "Phân Tích",
        "date": "Ngày",
        "no_results": "Không có kết quả để hiển thị. Vui lòng tính toán kết quả trước.",
        "no_past_analyses": "Không tìm thấy phân tích trước đây."
    }
}

def set_language(language):
    """Set the current language"""
    if language not in ["en", "vi"]:
        language = "en"
    st.session_state.language = language

def get_text(key):
    """Get translated text for the current language"""
    language = st.session_state.language
    return translations.get(language, translations["en"]).get(key, key)