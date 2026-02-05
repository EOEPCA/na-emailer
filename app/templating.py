from __future__ import annotations
import os
from typing import Any
from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound
from .config import Settings
from .models import EventContext


class TemplateRenderer:
    def __init__(self, settings: Settings):
        env_kwargs: dict[str, Any] = {
            "loader": FileSystemLoader(settings.templates_dir),
            "autoescape": True,
        }
        if settings.template_strict_undefined:
            env_kwargs["undefined"] = StrictUndefined

        self.env = Environment(**env_kwargs)
        self.settings = settings

    def _template_base_for_type(self, ce_type: str) -> str:
        return self.settings.template_map_json.get(ce_type, self.settings.template_default)

    def render(self, ctx: EventContext) -> tuple[str, str | None, str | None]:
        base = self._template_base_for_type(ctx.type)
        context: dict[str, Any] = ctx.as_template_dict()

        subject = self.env.get_template(f"{base}.subject.j2").render(**context).strip()

        text = None
        try:
            text = self.env.get_template(f"{base}.txt.j2").render(**context)
        except TemplateNotFound:
            pass

        html = None
        try:
            html = self.env.get_template(f"{base}.html.j2").render(**context)
        except TemplateNotFound:
            pass

        if text is None and html is None:
            raise FileNotFoundError(
                f"No body template found for base '{base}' (expected {base}.txt.j2 or {base}.html.j2) in {os.path.abspath(self.settings.templates_dir)}"
            )

        return subject, text, html
