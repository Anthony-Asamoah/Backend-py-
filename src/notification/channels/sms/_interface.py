from abc import ABC, abstractmethod
from typing import Union, List, Dict, Any


class SmsProvider(ABC):
    """
    Abstract base class interface for SMS channels.

    Any concrete SMS provider implementation must inherit from this class
    and implement all abstract methods.
    """

    @abstractmethod
    def _parse_single_output(self, response: dict) -> str:
        """
        Parse the response from an api call to send a single sms or throw an exception.

        Args:
            response: Response dictionary from the api call

        Returns:
            Sms id or reference as a string.
        """
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def _parse_bulk_output(self, response: dict):
        """
        Parse the response from an api call to send bulk sms into a desired format or throw an exception.

        Args:
            response: Response dictionary from the api call

        Returns:
            dict with two lists of [successful message_reference and recipient] and [invalid recipient phone numbers].
            Example: {
                'successful': [{'reference': <str>, 'recipient': <str>}, ],
                'invalid': [<str>, ],
            }
        """
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    async def send_sms(
            self,
            recipient: str,
            message: str,
    ) -> str:
        """
        Send a single SMS

        Args:
            recipient: Recipient phone number
            message: SMS message content

        Returns:
            sms id/reference
        """
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    async def send_bulk_sms(
            self,
            recipients: List[str],
            message: str,
    ) -> dict[str, Any]:
        """
        Send bulk SMS to multiple recipients

        Args:
            recipients: Array of recipient phone numbers
            message: SMS message content

        Returns:
            dict with two lists of [successful message_reference and recipient] and [invalid recipient phone numbers].
            Example: {
                'successful': [{'reference': <str>, 'recipient': <str>}, ],
                'invalid': [<str>, ],
            }

        """
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    async def schedule_sms(
            self,
            recipients: Union[str, List[str]],
            message: str,
            scheduled_date_time: str,
    ) -> List[dict[str, str]]:
        """
        Schedule an SMS to be sent later

        Args:
            recipients: Recipient phone number or array of numbers
            message: SMS message content
            scheduled_date_time: Date/time to send (format: YYYY-MM-DD HH:MM:SS)

        Returns:
            Response from API
        """
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    async def get_sms_status(
            self,
            sms_id: str
    ) -> Dict:
        """
        Check the status of a sent SMS

        Args:
            sms_id: SMS ID returned from send operation

        Returns:
            Response from API with status information
        """
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    async def get_balance(self) -> Dict:
        """
        Get account SMS balance

        Returns:
            Response from API with balance information
        """
        raise NotImplementedError("Method not implemented")
