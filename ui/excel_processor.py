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
        return False, "Excel file could not be read or is empty", None    # Remove any unnamed columns (which pandas creates for empty columns)
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
        return False, f"Matrix must be {len(expected_labels)}×{len(expected_labels)}. Found {data_df.shape[0]}×{data_df.shape[1]}.", None

    # Create a new matrix with the right dimensions
    matrix = np.ones((len(expected_labels), len(expected_labels)))

    try:
        # Convert all values to float
        for i in range(len(expected_labels)):
            for j in range(len(expected_labels)):
                if i != j:  # Skip diagonal (already 1)
                    value = float(data_df.iloc[i, j])
                    matrix[i, j] = value

        # Check if the matrix is valid (diagonal = 1, i,j = 1/j,i)
        for i in range(len(expected_labels)):
            for j in range(i + 1, len(expected_labels)):
                if abs(matrix[i, j] * matrix[j, i] - 1.0) > 0.01:  # Allow small floating point errors
                    return False, f"Matrix is not reciprocal at position ({i + 1},{j + 1}) and ({j + 1},{i + 1})", None

        return True, "Matrix is valid", matrix
    except ValueError:
        return False, "Matrix must contain only numeric values", None
    except Exception as e:
        return False, f"Error validating matrix: {str(e)}", None

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
        return False, f"Error reading Excel file: {str(e)}", None

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
