def anonymize_data(data: dict) -> dict:
    """Anonymizes user data by replacing all values with [REDACTED]."""
    anonymized_data = {}
    for key in data:
        anonymized_data[key] = "[REDACTED]"
    return anonymized_data
