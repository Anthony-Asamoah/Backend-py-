import re
from datetime import datetime
from typing import Union, List, Dict, Optional

import httpx
from django.core.exceptions import ImproperlyConfigured

from main import settings
from main.lifespan import singletons
from main.utils.logger import log
from notification.channels.sms._interface import SmsProvider


class ArkeselSmsService(SmsProvider):
    """
    A comprehensive utility class to send and manage SMS via Arkesel

    This class provides methods to:
    - Send SMS (single and bulk)
    - Schedule SMS
    - Check SMS status
    - View SMS history
    - Manage Sender name/titles
    - Check account balance
    """

    def __init__(self, sender_name: Optional[str] = None):
        self.response_format = 'json'

        sender_name = sender_name or settings.SMS_SENDER_NAME
        self._validate_sender_name(sender_name)

        self.config = dict(
            is_sandbox=settings.SMS_IS_DEBUG,
            api_key=settings.ARKESEL_API_KEY,
            base_url=settings.ARKESEL_BASE_URL,
            sender_name=sender_name,
            sender_char_limit=settings.ARKESEL_SENDER_CHAR_LIMIT,
        )

        missing_configs = [k for k, v in self.config.items() if v is None]
        if missing_configs: raise ImproperlyConfigured(
            f"Missing Arkesel SMS Service configuration: {', '.join(missing_configs)}"
        )

    def _parse_single_output(self, response: dict):
        """
        Return the sms id/reference from a given response or throw an exception
        """
        try:
            reference = response["data"][0]["id"]
        except (KeyError, IndexError):
            reference = None

        if not reference: raise KeyError(
            f"Unable to retrieve sms reference/id. response: {response}"
        )
        return reference

    def _parse_bulk_output(self, response: dict):
        """
        Return a formatted output from a given response or throw an exception
        """
        data = response.get("data")
        if not data: raise Exception("Bulk SMS operation failed")

        try:
            successful = [
                {"reference": record["id"], "recipient": record["recipient"]}
                for record in data if record.get("id")
            ]
        except (KeyError, IndexError):
            successful = []

        if not successful: raise Exception(
            f"Unable to retrieve sms references/ids. response: {response}"
        )
        invalid = data[-1].get("invalid numbers", [])

        return dict(
            successful=successful,
            invalid=invalid,
        )

    async def send_sms(self, recipient: str, message: str) -> str:
        """
        Send a single SMS

        Args:
            recipient: Recipient phone number
            message: SMS message content

        Returns:
            Response from API

        Raises:
            ValueError: If validation fails
            Exception: If API request fails
        """

        phone = self._clean_phone_number(recipient)
        if not phone: raise ValueError(f"Invalid phone number: {recipient}")

        data = {
            'recipients': [phone],
            'message': message,
            'sender': self.config['sender_name'],
            'sandbox': self.config['is_sandbox'],
        }

        response = await self._send_request('sms/send', data)
        if not response: raise Exception("Failed to send SMS")
        log.info(f"SMS sent successfully to {recipient}")
        log.debug(f"SMS message: {message}")

        return self._parse_single_output(response)

    async def send_bulk_sms(self, recipients: List[str], message: str) -> Dict:
        """
        Send bulk SMS to multiple recipients

        Args:
            recipients: Array of recipient phone numbers
            message: SMS message content

        Returns:
            Response from API

        Raises:
            ValueError: If validation fails
            Exception: If API request fails
        """
        valid_numbers = []
        invalid_numbers = []

        for recipient in recipients:
            if phone := self._clean_phone_number(recipient):
                valid_numbers.append(phone)
            else:
                invalid_numbers.append(recipient)

        if not valid_numbers: raise ValueError("No valid phone numbers provided")

        if invalid_numbers: log.warning(
            "Some phone numbers were invalid", {'invalid_numbers': invalid_numbers}
        )

        data = {
            'recipients': valid_numbers,
            'message': message,
            'sender': self.config['sender_name'],
            'sandbox': self.config['is_sandbox'],
        }

        response = await self._send_request('sms/send', data) or {}
        return self._parse_bulk_output(response)

    async def schedule_sms(
            self,
            recipients: Union[str, List[str]],
            message: str,
            scheduled_date_time: datetime,
    ) -> Dict:
        """
        Schedule an SMS to be sent later

        Args:
            recipients: Recipient phone number or array of numbers
            message: SMS message content
            scheduled_date_time: Date/time to send

        Returns:
            Response from API

        Raises:
            ValueError: If validation fails
            Exception: If API request fails
        """
        data = {
            'recipients': self._clean_phone_numbers(recipients),
            'message': message,
            'sender': self.config['sender_name'],
            'schedule_date': scheduled_date_time.strftime('%Y-%m-%d %H:%M:%S'),
            'sandbox': self.config['is_sandbox'],
        }

        response = await self._send_request('sms/send', data)
        if not response: raise Exception("Failed to schedule SMS")
        return self._parse_bulk_output(response)

    async def send_sms_with_callback(
            self,
            recipients: Union[str, List[str]],
            message: str,
            callback_url: str,
    ) -> Dict:
        """
        Send an SMS with delivery callback URL

        Args:
            recipients: Recipient phone number or array of numbers
            message: SMS message content
            callback_url: URL to receive delivery status updates

        Returns:
            Response from API

        Raises:
            ValueError: If validation fails
            Exception: If API request fails
        """
        valid_numbers = self._clean_phone_numbers(recipients)

        # Validate callback URL
        if not re.match(r'^https?://.+', callback_url): raise ValueError("Invalid callback URL")

        data = {
            'recipients': valid_numbers,
            'message': message,
            'sender': self.config['sender_name'],
            'callback_url': callback_url
        }

        response = await self._send_request('sms/send/callback', data)

        if not response: raise Exception("Failed to send SMS with callback")
        return self._parse_bulk_output(response)

    async def get_sms_status(self, sms_id: str) -> Dict:
        """
        Check the status of an SMS by id

        Args:
            sms_id: SMS ID returned from send operation

        Returns:
            Response from API with status information

        Raises:
            Exception: If API request fails
        """
        data = dict(sms_id=sms_id)

        response = await self._send_request(f'sms/{sms_id}', data, method='GET')
        if not response: raise Exception("Failed to check SMS status")

        result = response.get('data')
        if not result: raise Exception("Failed to get SMS status")

        return result

    async def get_bulk_sms_status(self, sms_ids: list[str]) -> Dict:
        """
        Get SMS status for the given sms ids

        Args:
            sms_ids: List of sms ids as strings

        Returns:
            Response from API with SMS history

        Raises:
            ValueError: If date validation fails
            Exception: If API request fails
        """
        data = {"msg_ids": sms_ids}
        response = await self._send_request('sms/message-reports', data)
        if not response: raise Exception("Failed to get bulk SMS status")

        result = response.get('data')
        if not result: raise Exception("Failed to get bulk SMS status")

        return result

    async def get_balance(self) -> Dict:
        """
        Get account SMS balance

        Returns:
            Response from API with balance information

        Raises:
            Exception: If API request fails
        """
        response = await self._send_request('clients/balance-details', method='GET')

        if not response: raise Exception("Failed to get account balance")

        result = response.get('data')
        if not result: raise Exception("Failed to get Arkesel balance")

        return result

    async def _send_request(self, endpoint: str, data: Optional[Dict] = None, method: str = 'POST') -> Optional[Dict]:
        """
        Send HTTP request to Arkesel API

        Args:
            endpoint: API endpoint
            data: Request data
            method: HTTP method (GET, POST, etc.)

        Returns:
            Response data as dictionary or None if request failed
        """
        url = f"{self.config['base_url']}/{endpoint}"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'api-key': self.config['api_key']
        }

        log.debug(f"Sending request to {url}", {'method': method, 'data': data})

        async def call_api():
            client: httpx.AsyncClient = singletons.get('http_client')

            if method.upper() == 'POST':
                response = await client.post(url, headers=headers, json=data)
            else:  # GET
                response = await client.get(url, headers=headers, params=data)

            response.raise_for_status()
            log.debug("API response received", {'response': response})
            return response

        for attempt in range(3):
            try:
                response = await call_api()
                return response.json()
            except httpx.RequestError as e:
                log.error(f"API request failed (attempt {attempt + 1}/3)", {'error': str(e)})
                if attempt == 2:
                    log.error("All retry attempts failed")
                continue
            except:
                if 'response' in locals():
                    log.exception(f"Arkesel Api call failed. Response: {response.text}")
                else:
                    log.error("Arkesel Api call failed")
                continue

        return None

    def get_sms_reference(self, response: dict) -> Optional[str]:
        try:
            reference = response[""]
        except:
            return None
        else:
            return reference

    @staticmethod
    def _clean_phone_number(phone_number: str) -> Optional[str]:
        """
        Validate the given phone number format

        Args:
            phone_number: Phone number to validate

        Returns:
            Formatted phone number or None if invalid
        """
        # Remove any non-numeric characters
        phone = re.sub(r'[^0-9]', '', phone_number)

        # Check if the number is empty after cleaning
        if not phone: return None

        # If the number starts with a plus, remove it
        if phone.startswith('+'): phone = phone[1:]

        # If the number starts with a 0, replace it with country code
        if phone.startswith('0'): phone = '233' + phone[1:]

        # If the number doesn't have a country code, add Ghana's code (default)
        if len(phone) <= 10: phone = '233' + phone

        return phone

    def _clean_phone_numbers(self, recipients: list[str]) -> list[str]:
        _valid_numbers = []

        if isinstance(recipients, str):
            phone = self._clean_phone_number(recipients)
            if phone:
                _valid_numbers.append(phone)
            else:
                raise ValueError(f"Invalid phone number: {recipients}")
        elif isinstance(recipients, list):
            for recipient in recipients:
                phone = self._clean_phone_number(recipient)
                if phone:
                    _valid_numbers.append(phone)

            if not _valid_numbers:
                raise ValueError("No valid phone numbers provided")
        else:
            raise ValueError("Recipients must be a string or list")
        return _valid_numbers

    @staticmethod
    def _validate_sender_name(sender_name: str) -> None:
        if not isinstance(sender_name, str): raise ValueError("sender_name must be a string")

        sender_name = sender_name.strip()
        if not sender_name: raise ValueError("Invalid sender name: None/empty string")

        if len(sender_name) > settings.ARKESEL_SENDER_CHAR_LIMIT: raise ValueError(
            "sender_name must be less than 12 characters")

    def _set_response_format(self, format_type: str) -> None:
        format_type = format_type.lower()
        if format_type not in ['json', 'xml']: raise ValueError(
            "Invalid response format. Use 'json' or 'xml'"
        )
        self.response_format = format_type

    def _format_response(self, response: Dict) -> Union[str, Dict]:
        """
        Convert response to (JSON dict or XML string)
        """
        if self.response_format == 'xml':
            # Simple XML conversion function
            def dict_to_xml(tag, d):
                elem = f"<{tag}>"
                for key, val in d.items():
                    if isinstance(val, dict):
                        elem += dict_to_xml(key, val)
                    elif isinstance(val, list):
                        for item in val:
                            if isinstance(item, dict):
                                elem += dict_to_xml(f"item", item)
                            else:
                                elem += f"<{key}>{item}</{key}>"
                    else:
                        elem += f"<{key}>{val}</{key}>"
                elem += f"</{tag}>"
                return elem

            return dict_to_xml("response", response)
        return response
