def is_valid_phone_number(phone):
    # A basic check: starts with a "+" and is long enough to be valid
    return phone.startswith("+") and len(phone) >= 10
