def generate_unique_reference():
    # Example: generate a simple unique string
    import uuid
    return f"REF-{uuid.uuid4().hex[:8].upper()}"
