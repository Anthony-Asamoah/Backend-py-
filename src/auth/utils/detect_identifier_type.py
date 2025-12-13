from pydantic import validate_email
from pydantic_core import PydanticCustomError

from auth.schema import IdentifierChoices
from main.utils.validators import validate_phone_number


def detect_identifier_type(identifier: str) -> IdentifierChoices:
    """
    Auto-detect whether identifier is email or phone number.

    Args:
        identifier: The username/identifier to validate

    Returns:
        IdentifierChoices.EMAIL if valid email
        IdentifierChoices.PHONE_NUMBER if valid phone number

    Raises:
        ValueError: If identifier is neither valid email nor phone number
    """
    # Try email first (more common for web apps)
    try:
        validate_email(identifier)
        return IdentifierChoices.EMAIL
    except (PydanticCustomError, ValueError):
        pass

    # Try phone number
    try:
        validate_phone_number(identifier)
        return IdentifierChoices.PHONE_NUMBER
    except (PydanticCustomError, ValueError):
        pass

    # Neither email nor phone number
    raise ValueError(f"Invalid email or phone number: {identifier}")
