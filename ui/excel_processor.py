import numpy as np
import pandas as pd
import logging

def validate_excel_matrix(df, expected_labels):
    """
    Validate that a DataFrame has the correct format for an AHP matrix:
    - Must be square
    - Only the matrix data is validated (headers and indices are ignored)

    Returns:
        tuple: (is_valid, message, processed_matrix)
    """
    # Check if DataFrame is valid
    if df is None or df.empty:
        error_msg = f"❌ **Lỗi đọc file Excel**\n\n"
        error_msg += f"• File Excel không thể đọc được hoặc rỗng\n"
        error_msg += f"• Kiểm tra lại định dạng file (.xlsx)\n"
        error_msg += f"• Đảm bảo file không bị hỏng\n"
        error_msg += f"• Sử dụng mẫu Excel được cung cấp"
        return False, error_msg, None    # Remove any unnamed columns (which pandas creates for empty columns)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    logging.debug(f"Original DataFrame shape: {df.shape}")
    logging.debug(f"Expected labels count: {len(expected_labels)}")
    logging.debug(f"Expected labels: {expected_labels}")
    logging.debug(f"DataFrame columns: {df.columns.tolist()}")
    logging.debug(f"DataFrame index: {df.index.tolist()}")    # Extract the numeric matrix part
    # Try different slicing approaches to find valid data
    data_df = None
    
    # First try: Skip first row and column (standard approach)
    data_df1 = df.iloc[1:, 1:]
    logging.debug(f"Approach 1 - data_df shape: {data_df1.shape}")
    
    # Second try: Skip only first row (if first column contains numeric labels)
    data_df2 = df.iloc[1:, :]
    logging.debug(f"Approach 2 - data_df shape: {data_df2.shape}")
    
    # Third try: Use whole DataFrame (if no header/index labels)
    data_df3 = df
    logging.debug(f"Approach 3 - data_df shape: {data_df3.shape}")
    
    # Choose the approach that gives a square matrix closest to expected size
    approaches = [
        (data_df1, abs((data_df1.shape[0] * data_df1.shape[1]) - (len(expected_labels) * len(expected_labels)))),
        (data_df2, abs((data_df2.shape[0] * data_df2.shape[1]) - (len(expected_labels) * len(expected_labels)))),
        (data_df3, abs((data_df3.shape[0] * data_df3.shape[1]) - (len(expected_labels) * len(expected_labels))))
    ]
    
    # Sort by closest to expected size and prefer square matrices
    approaches.sort(key=lambda x: (x[1], abs(x[0].shape[0] - x[0].shape[1])))
    data_df = approaches[0][0]
    logging.debug(f"Selected data_df shape: {data_df.shape}")
    
    # Display a sample of the extracted data for debugging
    try:
        logging.debug(f"Data sample (first 3x3):")
        for i in range(min(3, data_df.shape[0])):
            row_values = []
            for j in range(min(3, data_df.shape[1])):
                try:
                    row_values.append(str(data_df.iloc[i, j]))
                except:
                    row_values.append("ERROR")
            logging.debug(f"Row {i}: {', '.join(row_values)}")
    except Exception as e:
        logging.debug(f"Error displaying sample: {e}")
    
    # If the matrix is larger than expected, trim it to the expected size
    if data_df.shape[0] >= len(expected_labels) and data_df.shape[1] >= len(expected_labels):
        data_df = data_df.iloc[:len(expected_labels), :len(expected_labels)]
        logging.debug(f"Trimmed data_df shape: {data_df.shape}")
    
    # Check dimensions
    if data_df.shape[0] != len(expected_labels) or data_df.shape[1] != len(expected_labels):
        error_msg = f"❌ **Lỗi kích thước ma trận**\n\n"
        error_msg += f"• **Hiện tại**: {data_df.shape[0]}×{data_df.shape[1]}\n"
        error_msg += f"• **Yêu cầu**: {len(expected_labels)}×{len(expected_labels)}\n\n"
        error_msg += f"💡 **Hướng dẫn**: Sử dụng mẫu Excel để đảm bảo đúng kích thước"
        return False, error_msg, None

    # Create a new matrix with the right dimensions
    matrix = np.ones((len(expected_labels), len(expected_labels)))
    
    # Check for non-numeric data and collect error details
    non_numeric_cells = []
    invalid_values = []
    text_cells = []
    empty_cells = []
    negative_cells = []

    try:
        # Convert all values to float and track any issues
        for i in range(len(expected_labels)):
            for j in range(len(expected_labels)):
                if i != j:  # Skip diagonal (already 1)
                    cell_value = data_df.iloc[i, j]
                    cell_position = f"({i+1},{j+1})"
                    
                    # Check if cell contains text or non-numeric data
                    if pd.isna(cell_value):
                        non_numeric_cells.append(cell_position)
                        invalid_values.append("Ô trống")
                        empty_cells.append(cell_position)
                        continue
                    
                    # Try to convert to string first to check content
                    str_value = str(cell_value).strip()
                    
                    # Check if it's clearly text (contains letters)
                    if any(char.isalpha() for char in str_value):
                        non_numeric_cells.append(cell_position)
                        invalid_values.append(f"'{str_value}'")
                        text_cells.append(f"{cell_position}: '{str_value}'")
                        continue
                    
                    # Try to convert to float
                    try:
                        value = float(cell_value)
                        
                        # Check for negative values
                        if value <= 0:
                            non_numeric_cells.append(cell_position)
                            invalid_values.append(f"{value} (phải > 0)")
                            negative_cells.append(f"{cell_position}: {value}")
                            continue
                            
                        matrix[i, j] = value
                    except (ValueError, TypeError):
                        non_numeric_cells.append(cell_position)
                        invalid_values.append(f"'{str_value}'")
                        continue

        # If there are non-numeric cells, return detailed error message
        if non_numeric_cells:
            error_msg = f"❌ **Phát hiện {len(non_numeric_cells)} ô dữ liệu không hợp lệ**\n\n"
            
            # Categorize errors
            if text_cells:
                error_msg += f"📝 **Chứa văn bản** ({len(text_cells)} ô):\n"
                for cell in text_cells[:3]:  # Show max 3 examples
                    error_msg += f"• {cell}\n"
                if len(text_cells) > 3:
                    error_msg += f"• ...và {len(text_cells) - 3} ô khác\n"
                error_msg += "\n"
            
            if empty_cells:
                error_msg += f"❌ **Ô trống** ({len(empty_cells)} ô):\n"
                for cell in empty_cells[:3]:  # Show max 3 examples
                    error_msg += f"• {cell}\n"
                if len(empty_cells) > 3:
                    error_msg += f"• ...và {len(empty_cells) - 3} ô khác\n"
                error_msg += "\n"
            
            if negative_cells:
                error_msg += f"🔢 **Số ≤ 0** ({len(negative_cells)} ô):\n"
                for cell in negative_cells[:3]:  # Show max 3 examples
                    error_msg += f"• {cell}\n"
                if len(negative_cells) > 3:
                    error_msg += f"• ...và {len(negative_cells) - 3} ô khác\n"
                error_msg += "\n"
            
            error_msg += f"📋 **Yêu cầu**: Ma trận {len(expected_labels)}×{len(expected_labels)} chỉ chứa số dương\n"
            error_msg += f"💡 **Mẹo**: Sử dụng mẫu Excel và nhập số như: 1, 2.5, 0.33"
            
            return False, error_msg, None

        # Check if the matrix is valid (diagonal = 1, i,j = 1/j,i)
        for i in range(len(expected_labels)):
            for j in range(i + 1, len(expected_labels)):
                if abs(matrix[i, j] * matrix[j, i] - 1.0) > 0.01:  # Allow small floating point errors
                    error_msg = f"❌ **Lỗi tính chất đối xứng AHP**\n\n"
                    error_msg += f"• **Vị trí**: Ô ({i + 1},{j + 1}) và ({j + 1},{i + 1})\n"
                    error_msg += f"• **Giá trị**: {matrix[i, j]:.3f} và {matrix[j, i]:.3f}\n"
                    error_msg += f"• **Quy tắc**: Nếu A[i,j] = x thì A[j,i] = 1/x\n"
                    error_msg += f"• **Ví dụ**: A[1,2] = 3 → A[2,1] = 0.333"
                    return False, error_msg, None

        return True, "Ma trận hợp lệ", matrix
    except Exception as e:
        error_msg = f"❌ **Lỗi xử lý file Excel**\n\n"
        error_msg += f"• **Chi tiết**: {str(e)}\n"
        error_msg += f"• Kiểm tra định dạng dữ liệu\n"
        error_msg += f"• Sử dụng mẫu Excel được cung cấp"
        return False, error_msg, None

def process_excel_file(uploaded_file, expected_labels):
    """
    Process an uploaded Excel file and extract the AHP matrix
    
    Args:
        uploaded_file: Streamlit uploaded file
        expected_labels: List of expected labels (criteria or alternatives)
        
    Returns:
        tuple: (is_valid, message, processed_matrix)
    """
    try:
        # Read the Excel file
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        logging.debug(f"Excel file shape after reading: {df.shape}")
        logging.debug(f"Expected labels: {expected_labels}")
        
        # Validate the matrix format
        is_valid, message, matrix = validate_excel_matrix(df, expected_labels)
        logging.debug(f"validate_excel_matrix returned: is_valid={is_valid}, message={message}, matrix_shape={matrix.shape if matrix is not None else None}")
        
        return is_valid, message, matrix
    except Exception as e:
        # Ensure three values are always returned
        logging.error(f"Error in process_excel_file: {str(e)}")
        error_msg = f"❌ **Lỗi đọc file Excel**:\n\n"
        error_msg += f"• **Chi tiết lỗi**: {str(e)}\n"
        error_msg += f"• Kiểm tra định dạng file (.xlsx)\n"
        error_msg += f"• Đảm bảo file không bị hỏng\n"
        error_msg += f"• Thử tải lại file hoặc sử dụng mẫu Excel"
        return False, error_msg, None

def create_excel_template(labels, file_path):
    """
    Create an Excel template file with the given labels
    
    Args:
        labels: List of criteria or alternatives
        file_path: Path to save the Excel file
    """
    # Create a DataFrame with ones on the diagonal and zeros elsewhere
    n = len(labels)
    matrix = np.ones((n, n))
    
    # Set diagonal to 1 and other cells to example values for AHP
    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i, j] = 1.0  # Diagonal
            elif i < j:
                matrix[i, j] = 1.0  # Upper triangle (placeholder)
            else:
                matrix[i, j] = 1.0  # Lower triangle (placeholder)
    
    df = pd.DataFrame(matrix, columns=labels, index=labels)
    
    # Save to Excel
    df.to_excel(file_path, index=True)
    
    # Log template creation
    logging.debug(f"Created Excel template with {n}x{n} matrix for labels: {labels}")
    
    return file_path
