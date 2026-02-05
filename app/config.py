from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field, field_validator

def _env_bool(name: str,
              default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def _default_templates_dir() -> str:
    return str((Path(__file__).resolve().parent.parent / "templates"))


class Settings(BaseModel):
    log_level: str = Field(default="INFO", alias="NA_LOG_LEVEL")

    #filtering
    filter_mode: str = Field(default="all", alias="NA_FILTER_MODE")  # all|any
    filters_json: dict[str, Any] = Field(default_factory=dict, alias="NA_FILTERS_JSON")

    #templates
    templates_dir: str = Field(default_factory=_default_templates_dir, alias="NA_TEMPLATES_DIR")
    template_map_json: dict[str, str] = Field(default_factory=dict, alias="NA_TEMPLATE_MAP_JSON")
    template_default: str = Field(default="default", alias="NA_TEMPLATE_DEFAULT")
    template_strict_undefined: bool = Field(default=False, alias="NA_TEMPLATE_STRICT_UNDEFINED")

    #email addressing defaults
    email_from: str | None = Field(default=None, alias="NA_EMAIL_FROM")
    email_to: list[str] = Field(default_factory=list, alias="NA_EMAIL_TO")
    email_cc: list[str] = Field(default_factory=list, alias="NA_EMAIL_CC")
    email_bcc: list[str] = Field(default_factory=list, alias="NA_EMAIL_BCC")
    email_subject_prefix: str = Field(default="", alias="NA_EMAIL_SUBJECT_PREFIX")

    #email client
    email_client: str = Field(default="yagmail", alias="NA_EMAIL_CLIENT")
    dry_run: bool = Field(default=False, alias="NA_DRY_RUN")

    #yagmail
    yagmail_user: str | None = Field(default=None, alias="NA_YAGMAIL_USER")
    yagmail_password: str | None = Field(default=None, alias="NA_YAGMAIL_PASSWORD")
    yagmail_host: str | None = Field(default=None, alias="NA_YAGMAIL_HOST")
    yagmail_port: int | None = Field(default=None, alias="NA_YAGMAIL_PORT")
    yagmail_smtp_starttls: bool | None = Field(default=None, alias="NA_YAGMAIL_SMTP_STARTTLS")
    yagmail_smtp_ssl: bool | None = Field(default=None, alias="NA_YAGMAIL_SMTP_SSL")

    @field_validator("filter_mode")
    @classmethod
    def _validate_filter_mode(cls, v: str) -> str:
        v2 = v.strip().lower()
        if v2 not in {"all", "any"}:
            raise ValueError("NA_FILTER_MODE must be 'all' or 'any'")
        return v2

    @field_validator("filters_json", mode="before")
    @classmethod
    def _parse_filters_json(cls, v: Any) -> dict[str, Any]:
        if v in (None, ""):
            return {}
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            return json.loads(v)
        raise TypeError("NA_FILTERS_JSON must be a JSON object string")

    @field_validator("template_map_json", mode="before")
    @classmethod
    def _parse_template_map_json(cls, v: Any) -> dict[str, str]:
        if v in (None, ""):
            return {}
        if isinstance(v, dict):
            return {str(k): str(val) for k, val in v.items()}
        if isinstance(v, str):
            obj = json.loads(v)
            if not isinstance(obj, dict):
                raise ValueError("NA_TEMPLATE_MAP_JSON must be a JSON object")
            return {str(k): str(val) for k, val in obj.items()}
        raise TypeError("NA_TEMPLATE_MAP_JSON must be a JSON object string")

    @field_validator("email_to", "email_cc", "email_bcc", mode="before")
    @classmethod
    def _parse_recipients(cls, v: Any) -> list[str]:
        if v in (None, ""):
            return []
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, str):
            return _parse_csv(v)
        raise TypeError("Recipients must be comma-separated string or JSON list")


def load_settings() -> Settings:
    env: dict[str, Any] = dict(os.environ)
    return Settings.model_validate(env)
