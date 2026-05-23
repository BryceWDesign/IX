"""Governed built-in tool registry for IX.

The built-in tools are deliberately small, deterministic, and side-effect free.
They exist so IX can prove the governance pattern first: tool calls must be
explicitly allowed, are traceable, and fail closed when policy does not permit
use.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from .errors import IXError


class IXToolError(IXError):
    """Raised when an IX tool cannot be invoked."""


@dataclass(frozen=True)
class ToolSpec:
    """Description of a safe built-in IX tool."""

    name: str
    description: str
    handler: Callable[[Mapping[str, Any]], Any]


class BuiltInToolRegistry:
    """Registry of deterministic, side-effect-free IX tools."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}
        self.register(ToolSpec("tool.echo", "Return the provided message or text.", _tool_echo))
        self.register(ToolSpec("tool.upper", "Uppercase the provided text.", _tool_upper))
        self.register(ToolSpec("tool.lower", "Lowercase the provided text.", _tool_lower))
        self.register(ToolSpec("tool.length", "Return the length of the provided text.", _tool_length))
        self.register(ToolSpec("tool.sha256", "Return a SHA-256 hash of the provided text.", _tool_sha256))

    def register(self, spec: ToolSpec) -> None:
        """Register a tool specification."""

        if spec.name in self._tools:
            raise IXToolError(f"Tool already registered: {spec.name}")
        self._tools[spec.name] = spec

    def names(self) -> tuple[str, ...]:
        """Return registered tool names."""

        return tuple(sorted(self._tools))

    def invoke(self, name: str, arguments: Mapping[str, Any]) -> Any:
        """Invoke a registered built-in tool."""

        if name not in self._tools:
            known = ", ".join(self.names())
            raise IXToolError(f"Unknown tool: {name}. Known tools: {known}")
        return self._tools[name].handler(arguments)


def _text_argument(arguments: Mapping[str, Any], *, primary: str = "text") -> str:
    for key in (primary, "message", "value"):
        if key in arguments:
            return str(arguments[key])
    raise IXToolError(f"Missing required argument: {primary}")


def _tool_echo(arguments: Mapping[str, Any]) -> str:
    return _text_argument(arguments, primary="message")


def _tool_upper(arguments: Mapping[str, Any]) -> str:
    return _text_argument(arguments).upper()


def _tool_lower(arguments: Mapping[str, Any]) -> str:
    return _text_argument(arguments).lower()


def _tool_length(arguments: Mapping[str, Any]) -> int:
    return len(_text_argument(arguments))


def _tool_sha256(arguments: Mapping[str, Any]) -> str:
    text = _text_argument(arguments)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
