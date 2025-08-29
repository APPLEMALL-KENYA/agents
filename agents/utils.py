import random
import string

def generate_unique_reference():
    """Generate a random 8-character alphanumeric reference code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
