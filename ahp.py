import numpy as np

def calculate_weights(matrix):
    """Calculate weights from pairwise comparison matrix"""
    # Normalize the matrix
    col_sums = np.sum(matrix, axis=0)
    normalized_matrix = matrix / col_sums
    
    # Calculate weights as row averages
    weights = np.mean(normalized_matrix, axis=1)
    return weights / np.sum(weights)  # Ensure weights sum to 1

def calculate_consistency_ratio(matrix, weights):
    """Calculate consistency ratio to check if comparisons are consistent"""
    n = len(weights)
    
    # Random consistency index values
    RI = {1: 0, 2: 0, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49, 11: 1.51, 12: 1.54, 13: 1.56, 14: 1.57, 15: 1.59}
    # For n > 15, use the last known RI value

    
    # Calculate lambda max
    weighted_sum = np.dot(matrix, weights)
    consistency_vector = weighted_sum / weights
    lambda_max = np.mean(consistency_vector)
    
    # Calculate consistency index
    CI = (lambda_max - n) / (n - 1) if n > 1 else 0
    
    # Calculate consistency ratio
    CR = CI / RI[n] if n >= 1 and n <= 15 and n > 1 else (CI / RI[15] if n > 15 and n > 1 else 0)
    
    # Return a tuple of (CR, Lambda_max, CI)
    return (CR, lambda_max, CI)

def get_saaty_scale_description(value, language="en"):
    """Return description for Saaty scale values in the selected language"""
    if language == "en":
        scale = {
            1: "Equal importance",
            2: "Weak or slight importance",
            3: "Moderate importance",
            4: "Moderate plus importance",
            5: "Strong importance",
            6: "Strong plus importance",
            7: "Very strong importance",
            8: "Very, very strong importance",
            9: "Extreme importance"
        }
    else:  # Vietnamese
        scale = {
            1: "Tầm quan trọng bằng nhau",
            2: "Tầm quan trọng yếu hoặc nhẹ",
            3: "Tầm quan trọng vừa phải",
            4: "Tầm quan trọng vừa phải cộng",
            5: "Tầm quan trọng mạnh",
            6: "Tầm quan trọng mạnh cộng",
            7: "Tầm quan trọng rất mạnh",
            8: "Tầm quan trọng rất, rất mạnh",
            9: "Tầm quan trọng cực kỳ"
        }
    return scale.get(value, "")

def calculate_all_results(criteria_matrix, alternative_matrices, criteria, alternatives):
    """Calculate all AHP results"""
    # Calculate criteria weights
    criteria_weights = calculate_weights(criteria_matrix)
    
    # Calculate consistency metrics for criteria
    cr_criteria, lambda_max_criteria, ci_criteria = calculate_consistency_ratio(criteria_matrix, criteria_weights)
    consistency_ratios = {'criteria': cr_criteria}
    lambda_max_values = {'criteria': lambda_max_criteria}
    consistency_indices = {'criteria': ci_criteria}
    
    # Calculate alternative weights for each criterion
    alternative_weights = {}
    for criterion_idx, criterion in enumerate(criteria):
        alt_weights = calculate_weights(alternative_matrices[criterion])
        alternative_weights[criterion] = alt_weights
        
        # Calculate consistency metrics for alternatives
        cr_alt, lambda_max_alt, ci_alt = calculate_consistency_ratio(alternative_matrices[criterion], alt_weights)
        consistency_ratios[criterion] = cr_alt
        lambda_max_values[criterion] = lambda_max_alt
        consistency_indices[criterion] = ci_alt
    
    # Calculate final scores
    n_alternatives = len(alternatives)
    final_scores = np.zeros(n_alternatives)
    
    for i, criterion in enumerate(criteria):
        criterion_weight = criteria_weights[i]
        alt_weights = alternative_weights[criterion]
        final_scores += criterion_weight * alt_weights
    
    return {
        'criteria_weights': criteria_weights,
        'alternative_weights': alternative_weights,
        'final_scores': final_scores,
        'consistency_ratios': consistency_ratios,
        'lambda_max_values': lambda_max_values,
        'consistency_indices': consistency_indices
    }