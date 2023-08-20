"""Various miscellaneous utilities."""

def validate_phone_number(phone_number: str) -> str:
    """Standardize and validate input phone number. Raise ValueError if invalid."""
    try:
        phone_number = str(phone_number)
    except ValueError:
        raise ValueError(f"Couldn't interpret {phone_number} as a string.")
        
    if not phone_number:
        raise ValueError("Phone number was given as an empty string.")

    # Remove the plus if given, ex. Twilio does
    if phone_number[0] == "+":
        phone_number = phone_number[1:]

    if not phone_number.isnumeric():
        raise ValueError(f"Resulting phone number {phone_number} is not numeric.")

    if len(phone_number) != 11:
        raise ValueError(
            f"Phone number {phone_number} isn't 11 digits. Does it have a country code?"
        )
        
    # Otherwise, if all looks good
    return phone_number
