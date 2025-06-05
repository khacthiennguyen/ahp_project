def format_decimal(value, decimal_places=4):
    """Format a decimal number to a specified number of decimal places"""
    return f"{value:.{decimal_places}f}"

def format_percentage(value, decimal_places=2):
    """Format a decimal as a percentage"""
    return f"{value * 100:.{decimal_places}f}%"