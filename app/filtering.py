from __future__ import annotations
from typing import Any
from .models import EventContext


def _get_attr(ctx: EventContext,
              key: str) -> Any:
    #Support CloudEvent top-level attributes and extensions only.
    if hasattr(ctx, key):
        return getattr(ctx, key)
    return ctx.extensions.get(key)


def matches_filters(ctx: EventContext,
                    filters: dict[str, Any],
                    mode: str = "all") -> bool:
    if not filters:
        return True
    results: list[bool] = []
    for k, expected in filters.items():
        actual = _get_attr(ctx, k)
        if isinstance(expected, (list, tuple, set)):
            results.append(actual in expected)
        else:
            results.append(actual == expected)
    return all(results) if mode == "all" else any(results)
