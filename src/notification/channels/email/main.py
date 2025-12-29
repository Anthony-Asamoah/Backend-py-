import mimetypes
import smtplib
from datetime import datetime
from email.message import EmailMessage
from os import path
from pathlib import Path
from typing import Union, List, Optional, Dict, Tuple, Sequence
from urllib.parse import urlparse

import httpx
from django.core.exceptions import ImproperlyConfigured
from jinja2 import Environment, FileSystemLoader, nodes

from main import settings
from main.lifespan import singletons
from main.utils.logger import log


class EmailSender:
    def __init__(
            self,
            template_dir: Union[str, Path] = settings.EMAIL_TEMPLATE_DIR,
    ):
        """
        Initialize the EmailSender with template directory and SMTP configuration.

        Args:
            template_dir: Directory containing email templates
        """
        self.template_env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.smtp_config = dict(
            host=settings.MAIL_SERVER,
            port=settings.MAIL_PORT,
            username=settings.MAIL_USERNAME,
            password=settings.MAIL_PASSWORD,
            from_email=settings.MAIL_FROM,
            use_tls=settings.MAIL_USE_TLS,
            batch_size=settings.SMTP_RECIPIENTS_LIMIT
        )

        missing_configs = [k for k, v in self.smtp_config.items() if v is None]
        if missing_configs: raise ImproperlyConfigured(
            f"Missing SMTP configuration: {', '.join(missing_configs)}"
        )

    async def send_email(
            self,
            recipient: str,
            subject: str,
            heading: str,
            content: str,
            links: Optional[List[dict]] = None,
    ):
        """
        Links should come in the following format: [{
            "label": "Link Button Text",
            "url": "https://example.com"
        },]
        """
        msg = EmailMessage()

        msg['Subject'] = subject
        msg['From'] = self.smtp_config['from_email']
        msg['To'] = recipient

        content = self.render_basic_template(subject=subject, header=heading, body=content, links=links)
        msg.set_content(content, subtype='html')

        await self._send(msg)

    async def _send(self, msg: EmailMessage):
        try:
            with smtplib.SMTP(self.smtp_config["host"], self.smtp_config["port"], timeout=60) as smtp:
                log.debug("SMTP connection established")

                if self.smtp_config["use_tls"]:
                    smtp.starttls()
                    log.debug("TLS started")

                smtp.login(self.smtp_config["username"], self.smtp_config["password"])
                log.debug("SMTP authentication successful")

                smtp.send_message(msg)
                log.info(f"Email sent successfully to {msg['To']}")

        except smtplib.SMTPConnectError:
            log.error("Failed to connect to the SMTP server. Service not available.")
            raise
        except smtplib.SMTPAuthenticationError:
            log.error("Invalid SMTP username or password. Authentication failed.")
            raise
        except smtplib.SMTPRecipientsRefused as err:
            log.error(f"Recipient email addresses refused: {err}")
            raise
        except:
            log.exception(f"An unexpected error occurred while sending the email.")
            raise

    @staticmethod
    async def _download_file_from_url(url: str, timeout: int = 60) -> tuple[bytes, str]:
        # get http client from cache
        client: httpx.AsyncClient = singletons.get('http_client')
        try:
            response = await client.get(url, timeout=timeout)
            response.raise_for_status()

            # Get filename from URL or Content-Disposition header
            filename = None
            if 'content-disposition' in response.headers:
                content_disp = response.headers['content-disposition']
                if 'filename=' in content_disp:
                    filename = content_disp.split('filename=')[1].strip('"\'')

            if not filename:
                # Extract filename from URL path
                parsed_url = urlparse(url)
                filename = path.basename(parsed_url.path) or 'downloaded_file'

                # Add extension based on content-type if missing
                if '.' not in filename and 'content-type' in response.headers:
                    content_type = response.headers['content-type']
                    if content_type.startswith('image/'):
                        ext = content_type.split('/')[-1]
                        filename += f'.{ext}'
                    elif content_type == 'application/pdf':
                        filename += '.pdf'
                    elif content_type.startswith('text/'):
                        filename += '.txt'

            content = response.content
            return content, filename

        except Exception as e:
            log.error(f"Failed to download file from {url}: {e}")
            raise

    @staticmethod
    def _is_url(path: str) -> bool:
        """Check if a string is a valid URL"""
        try:
            result = urlparse(path)
            return all([result.scheme, result.netloc])
        except:
            return False

    @staticmethod
    def _get_main_and_sub_types(filename: str) -> Tuple[str, str]:
        content_type, encoding = mimetypes.guess_type(filename)
        if content_type is None:
            maintype, subtype = 'application', 'octet-stream'
        else:
            maintype, subtype = content_type.split('/', 1)
        return maintype, subtype

    def _render_template(self, template_name: str, context: dict) -> Dict[str, str]:
        template = self.template_env.get_template(template_name)
        rendered_html = template.render(**context)
        subject = self._render_subject(template_name, context)
        return dict(subject=subject, html_body=rendered_html)

    def render_basic_template(
            self, *,
            subject: str,
            header: str,
            body: str,
            links: List[dict] = None,
    ) -> str:
        """
        Links should come in the following format: [{
            "label": "Link Button Text",
            "url": "https://example.com"
        },]
        """
        template = self.template_env.get_template('simple_base.html')

        context: dict[str, Union[str, int, float, Sequence]] = {
            'subject': subject,
            'header': header,
            'body': body,
            '_year': datetime.now().year
        }
        if links and isinstance(links, list): context['links'] = links
        return template.render(context)

    def _get_subject_macro_args(self, template_name: str) -> list:
        template_source = self.template_env.loader.get_source(self.template_env, template_name)[0]
        parsed_template = self.template_env.parse(template_source)

        subject_macro = None
        for node in parsed_template.find_all(nodes.Macro):
            if node.name == 'subject': subject_macro = node; break

        if subject_macro is None: return []

        arg_names = [arg.name for arg in subject_macro.args]
        return arg_names

    def _render_subject(self, template_name: str, context: dict) -> str:
        subject_arg_names = self._get_subject_macro_args(template_name)
        subject_context = {arg: context.get(arg) for arg in subject_arg_names}
        template = self.template_env.get_template(template_name)
        subject = template.module.subject(**subject_context).strip()
        return subject
