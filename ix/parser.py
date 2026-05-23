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
    r"(?:\s+as\s+(?P<output>[A-Za-z_][A-Za-z0-9_]*))?"
    r"(?:\s+with\s+(?P<arguments>.+))?$"
)


@dataclass(frozen=True)
class _LogicalLine:
    text: str
    line: int
    column: int


class IXParser:
    """Parse IX source text into a canonical AST."""

    def __init__(self, filename: str = "<memory>") -> None:
        self.filename = filename
        self._lines: list[_LogicalLine] = []
        self._position = 0

    def parse(self, source: str) -> Program:
        self._lines = list(self._logical_lines(source))
        self._position = 0
        statements = self._parse_statements(stop_on_closing_brace=False)
        span = SourceSpan(self.filename, 1, 1)
        return Program(span=span, statements=tuple(statements))

    def _parse_statements(self, *, stop_on_closing_brace: bool) -> list[Statement]:
        statements: list[Statement] = []

        while not self._at_end():
            current = self._peek()
            if current.text == "}":
                if stop_on_closing_brace:
                    self._advance()
                    return statements
                raise self._syntax("Unexpected closing brace", current)

            statements.append(self._parse_statement())

        if stop_on_closing_brace:
            last = self._lines[-1] if self._lines else _LogicalLine("", 1, 1)
            raise self._syntax("Missing closing brace", last)

        return statements

    def _parse_statement(self) -> Statement:
        current = self._advance()
        text = current.text
        span = self._span(current)

        agent_match = _AGENT_HEADER.match(text)
        if agent_match:
            self._consume_opening_brace("agent block", current)
            body = self._parse_statements(stop_on_closing_brace=True)
            return AgentBlock(span=span, name=agent_match.group("name"), statements=tuple(body))

        on_match = _ON_HEADER.match(text)
        if on_match:
            self._consume_opening_brace("event block", current)
            body = self._parse_statements(stop_on_closing_brace=True)
            return OnBlock(span=span, event=on_match.group("event"), statements=tuple(body))

        if text.startswith("let "):
            name, expression = self._parse_assignment(text[4:], current, "let")
            return LetStatement(span=span, name=name, expression=expression)

        if text.startswith("remember "):
            name, expression = self._parse_assignment(text[9:], current, "remember")
            return RememberStatement(span=span, name=name, expression=expression)

        if text.startswith("print "):
            return PrintStatement(span=span, expression=self._required_tail(text, "print", current))

        if text.startswith("reply "):
            return ReplyStatement(span=span, expression=self._required_tail(text, "reply", current))

        if text.startswith("recall "):
            name = self._required_tail(text, "recall", current)
            self._require_identifier(name, current, "recall target")
            return RecallStatement(span=span, name=name)

        if text.startswith("assert "):
            return AssertStatement(span=span, expression=self._required_tail(text, "assert", current))

        if text.startswith("trace "):
            return TraceStatement(span=span, message=self._required_tail(text, "trace", current))

        tool_match = _TOOL_CALL.match(text)
        if tool_match:
            arguments = self._parse_tool_arguments(tool_match.group("arguments") or "", current)
            return ToolCallStatement(
                span=span,
                tool_name=tool_match.group("tool"),
                output_name=tool_match.group("output"),
                arguments=tuple(arguments),
            )

        approval_match = _REQUIRE_APPROVAL.match(text)
        if approval_match:
            reason = approval_match.group("reason") or '"Human approval required"'
            return RequireApprovalStatement(span=span, reason=reason)

        policy_match = _POLICY.match(text)
        if policy_match:
            effect = policy_match.group("effect")
            target = policy_match.group("target")
            reason = policy_match.group("reason")
            if effect not in {"allow", "deny"}:
                raise self._syntax("Policy effect must be allow or deny", current)
            return PolicyStatement(span=span, effect=effect, target=target, reason=reason)

        raise self._syntax(f"Unsupported IX statement: {text!r}", current)

    def _consume_opening_brace(self, context: str, header: _LogicalLine) -> None:
        if self._at_end() or self._peek().text != "{":
            raise self._syntax(f"Expected '{{' after {context} header", header)
        self._advance()

    def _parse_assignment(self, raw: str, line: _LogicalLine, keyword: str) -> tuple[str, str]:
        match = _ASSIGNMENT.match(raw.strip())
        if not match:
            raise self._syntax(f"Expected {keyword} assignment in the form `{keyword} name = value`", line)
        name = match.group("name")
        expression = match.group("expr").strip()
        if not expression:
            raise self._syntax(f"Expected value for {keyword} assignment", line)
        return name, expression

    def _parse_tool_arguments(self, raw: str, line: _LogicalLine) -> list[ToolArgument]:
        if not raw.strip():
            return []

        arguments: list[ToolArgument] = []
        for segment in self._split_commas(raw):
            match = _ASSIGNMENT.match(segment.strip())
            if not match:
                raise self._syntax("Expected tool argument in the form name = value", line)
            arguments.append(
                ToolArgument(
                    name=match.group("name"),
                    expression=match.group("expr").strip(),
                )
            )
        return arguments

    def _split_commas(self, raw: str) -> list[str]:
        segments: list[str] = []
        token_start = 0
        in_quote: str | None = None
        escaped = False

        for index, char in enumerate(raw):
            if escaped:
                escaped = False
                continue
            if char == "\\":
                escaped = True
                continue
            if char in {'"', "'"}:
                if in_quote is None:
                    in_quote = char
                elif in_quote == char:
                    in_quote = None
                continue
            if char == "," and in_quote is None:
                segment = raw[token_start:index].strip()
                if segment:
                    segments.append(segment)
                token_start = index + 1

        segment = raw[token_start:].strip()
        if segment:
            segments.append(segment)
        return segments

    def _required_tail(self, text: str, keyword: str, line: _LogicalLine) -> str:
        tail = text[len(keyword) :].strip()
        if not tail:
            raise self._syntax(f"Expected value after `{keyword}`", line)
        return tail

    def _require_identifier(self, value: str, line: _LogicalLine, label: str) -> None:
        if not _IDENTIFIER.match(value):
            raise self._syntax(f"Invalid {label}: {value!r}", line)

    def _logical_lines(self, source: str) -> Iterable[_LogicalLine]:
        for line_number, raw_line in enumerate(source.splitlines(), start=1):
            cleaned = self._strip_comment(raw_line).strip()
            if not cleaned:
                continue

            for text, column in self._split_braces(cleaned, raw_line):
                if text:
                    yield _LogicalLine(text=text, line=line_number, column=column)

    def _strip_comment(self, raw_line: str) -> str:
        in_quote: str | None = None
        escaped = False
        for index, char in enumerate(raw_line):
            if escaped:
                escaped = False
                continue
            if char == "\\":
                escaped = True
                continue
            if char in {'"', "'"}:
                if in_quote is None:
                    in_quote = char
                elif in_quote == char:
                    in_quote = None
                continue
            if char == "#" and in_quote is None:
                return raw_line[:index]
        return raw_line

    def _split_braces(self, cleaned: str, raw_line: str) -> Iterable[tuple[str, int]]:
        token_start = 0
        in_quote: str | None = None
        escaped = False

        for index, char in enumerate(cleaned):
            if escaped:
                escaped = False
                continue
            if char == "\\":
                escaped = True
                continue
            if char in {'"', "'"}:
                if in_quote is None:
                    in_quote = char
                elif in_quote == char:
                    in_quote = None
                continue
            if char in "{}" and in_quote is None:
                before = cleaned[token_start:index].strip()
                if before:
                    yield before, self._column(raw_line, before)
                yield char, self._column(raw_line, char)
                token_start = index + 1

        after = cleaned[token_start:].strip()
        if after:
            yield after, self._column(raw_line, after)

    def _column(self, raw_line: str, token: str) -> int:
        index = raw_line.find(token)
        return 1 if index < 0 else index + 1

    def _peek(self) -> _LogicalLine:
        return self._lines[self._position]

    def _advance(self) -> _LogicalLine:
        current = self._peek()
        self._position += 1
        return current

    def _at_end(self) -> bool:
        return self._position >= len(self._lines)

    def _span(self, line: _LogicalLine) -> SourceSpan:
        return SourceSpan(self.filename, line.line, line.column)

    def _syntax(self, message: str, line: _LogicalLine) -> IXSyntaxError:
        return IXSyntaxError(message, self._span(line))


def parse_ix(source: str, *, filename: str = "<memory>") -> Program:
    """Parse IX source text into a :class:`Program`."""

    return IXParser(filename=filename).parse(source)
