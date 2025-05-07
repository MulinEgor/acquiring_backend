import smtplib
from email.message import EmailMessage

from loguru import logger

from src.core import constants
from src.core.settings import settings


class EmailService:
    """Сервис для отправки email."""

    @staticmethod
    def send(email: str, subject: str, body: str) -> None:
        """
        Отправить email, используя протокол SMTP.

        Args:
            email (str): email получателя.
            subject (str): тема письма.
            body (str): тело письма.
        """

        logger.info("Отправка email на почту: {}", email)

        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_SENDER_EMAIL
        msg["To"] = email

        try:
            with smtplib.SMTP(constants.SMTP_SERVER, constants.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_SENDER_EMAIL, settings.SMTP_SENDER_PASSWORD)
                server.sendmail(settings.SMTP_SENDER_EMAIL, [email], msg.as_string())

        except Exception as e:
            raise e
