from __future__ import annotations
from ..config import Settings
from .base import EmailClient
from .yagmail_client import YagmailClient


def create_email_client(settings: Settings) -> EmailClient:
    name = settings.email_client.strip().lower()
    if name == "yagmail":
        return YagmailClient(settings)
    raise ValueError(f"Unsupported NA_EMAIL_CLIENT: {settings.email_client}")
