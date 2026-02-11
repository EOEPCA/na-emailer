from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class EmailMessage:
    subject: str
    text: str | None = None
    html: str | None = None
    sender: str | None = None
    to: Sequence[str] = field(default_factory=list)
    cc: Sequence[str] = field(default_factory=list)
    bcc: Sequence[str] = field(default_factory=list)
    headers: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class EventContext:
    #ce attributes
    id: str
    source: str
    type: str
    subject: str | None
    time: str | None
    dataschema: str | None
    datacontenttype: str | None
    #raw data
    data: Any
    extensions: Mapping[str, Any]

    def as_template_dict(self) -> dict[str, Any]:
        return {
            "ce": {
                "id": self.id,
                "source": self.source,
                "type": self.type,
                "subject": self.subject,
                "time": self.time,
                "dataschema": self.dataschema,
                "datacontenttype": self.datacontenttype,
                **self.extensions,
            },
            "data": self.data,
        }
