"""Canonical parser for the IX language.

The parser is intentionally conservative. It accepts the executable language core
that the runtime supports, plus agent/event/policy/tool structures needed for
IX's evidence-bound agent contract direction. Unsupported lines fail closed with
a clear syntax error instead of being silently ignored.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from .ast import (
    AgentBlock,
    AssertStatement,
    LetStatement,
    OnBlock,
    PolicyStatement,
    PrintStatement,
    Program,
    RecallStatement,
    RememberStatement,
    ReplyStatement,
    RequireApprovalStatement,
    Statement,
    ToolArgument,
    ToolCallStatement,
    TraceStatement,
)
from .errors import IXSyntaxError, SourceSpan

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_ASSIGNMENT = re.compile(r"^(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<expr>.+)$")
_AGENT_HEADER = re.compile(r"^agent\s+(?P<name>[A-Za-z_][A-Za-z0-9_-]*)$")
_ON_HEADER = re.compile(r"^on\s+(?P<event>[A-Za-z_][A-Za-z0-9_.:-]*)$")
_POLICY = re.compile(
    r"^(?P<effect>allow|deny)\s+(?P<target>[A-Za-z_][A-Za-z0-9_.:-]*(?:\.\*)?)"
    r"(?:\s+reason\s+(?P<reason>.+))?$"
)
_REQUIRE_APPROVAL = re.compile(r"^require\s+human_approval(?:\s+reason\s+(?P<reason>.+))?$")
_TOOL_CALL = re.compile(
    r"^call\s+(?P<tool>[A-Za-z_][A-Za-z0-9_.:-]*)"
    r"(?:\s+as\s+(?P<output>[A-Za-z_][A-Za-z0-9_] *))?"
    r"(?:\s+with\s+(?P<arguments>.+))?$"
)
