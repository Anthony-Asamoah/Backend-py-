"""Reusable validation utilities."""
import phonenumbers
from phonenumbers import NumberParseException


def validate_str(value: str) -> str:
    """Validate a non empty string"""

    if not value.strip(): raise ValueError("Field cannot be empty")
    return value


def validate_phone_number(phone: str, default_region: str = "GH") -> str:
    """
    Validate and format phone number using Google's libphonenumber.

    Args:
        phone: Phone number string to validate
        default_region: Default region code (ISO 3166-1 alpha-2)

    Returns:
        Formatted phone number in E164 format (e.g., +12345678900)

    Raises:
        ValueError: If phone number is invalid
    """
    if not phone: raise ValueError("Phone number cannot be empty")

    try:
        # Parse the phone number
        parsed = phonenumbers.parse(phone, default_region)

        # Check if the number is valid
        if not phonenumbers.is_valid_number(parsed):
            raise ValueError(f"Invalid phone number: {phone}")

        # Return formatted number in E164 format
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

    except NumberParseException as e:
        raise ValueError(f"Invalid phone number format: {phone}. Error: {str(e)}")
