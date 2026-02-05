from __future__ import annotations
from abc import ABC, abstractmethod
from ..models import EmailMessage


class EmailClient(ABC):
    @abstractmethod
    def send(self, message: EmailMessage) -> None:
        raise NotImplementedError
