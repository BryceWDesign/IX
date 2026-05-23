import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from ix.ast import SendStatement
from ix.cli import main
from ix.formatting import format_ix
from ix.parser import parse_ix
from ix.runtime import IXRuntime, IXRuntimeError, run_ix


class TestIXMultiAgentOrchestration(unittest.TestCase):
    def test_parser_accepts_send_statement(self):
        program = parse_ix('send Reviewer.review as verdict with item = "request"')

        statement = program.statements[0]
        self.assertIsInstance(statement, SendStatement)
        self.assertEqual(statement.target_agent, "Reviewer")
        self.assertEqual(statement.target_event, "review")
        self.assertEqual(statement.output_name, "verdict")
        self.assertEqual(statement.arguments[0].name, "item")

    def test_runtime_executes_traceable_agent_handoff(self):
        program = parse_ix(
            '''
            agent Coordinator {
                on start {
                    send Reviewer.review as verdict with item = "launch request"
                    reply "Reviewer said: {verdict}"
                }
            }

            agent Reviewer {
                on review {
                    reply "approved {item}"
                }
            }
            '''
        )

        result = run_ix(program, agent="Coordinator")

        self.assertEqual(result.handoffs[0]["target_agent"], "Reviewer")
        self.assertEqual(result.handoffs[0]["target_event"], "review")
        self.assertEqual(result.variables["verdict"], "approved launch request")
        self.assertEqual(
            result.replies,
            ["approved launch request", "Reviewer said: approved launch request"],
        )
        trace_kinds = [event.kind for event in result.trace]
        self.assertIn("handoff.start", trace_kinds)
        self.assertIn("handoff.complete", trace_kinds)

    def test_handoff_can_use_tools_when_target_event_allows_them(self):
        program = parse_ix(
            '''
            agent Coordinator {
                on start {
                    send Worker.shout as answer with text = "hello"
                    reply answer
                }
            }

            agent Worker {
                on shout {
                    allow tool.upper reason "Worker may uppercase deterministic text"
                    call tool.upper as result with text = text
                    reply result
                }
            }
            '''
        )

        result = run_ix(program, agent="Coordinator")

        self.assertEqual(result.variables["answer"], "HELLO")
        self.assertEqual(result.tool_results[0]["result"], "HELLO")

    def test_missing_target_agent_fails_closed(self):
        program = parse_ix(
            '''
            agent Coordinator {
                on start {
                    send Missing.review as verdict with item = "request"
                }
            }
            '''
        )

        with self.assertRaises(IXRuntimeError):
            run_ix(program, agent="Coordinator")

    def test_handoff_depth_limit_prevents_unbounded_recursion(self):
        program = parse_ix(
            '''
            agent Loop {
                on start {
                    send Loop.start as again
                }
            }
            '''
        )

        with self.assertRaises(IXRuntimeError):
            IXRuntime(max_handoff_depth=2).run(program, agent="Loop")

    def test_formatter_supports_send_statement(self):
        program = parse_ix('send Reviewer.review as verdict with item="request"')

        self.assertEqual(
            format_ix(program),
            'send Reviewer.review as verdict with item = "request"\n',
        )

    def test_cli_orchestrate_requires_agent(self):
        ix_file = self._write_ix('reply "Ready"')

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(["orchestrate", str(ix_file)])

        self.assertEqual(code, 2)
        self.assertIn("--agent is required", stderr.getvalue())

    def test_cli_orchestrate_prints_handoff_summary(self):
        ix_file = self._write_ix(
            '''
            agent Coordinator {
                on start {
                    send Reviewer.review as verdict with item = "request"
                    reply "Final: {verdict}"
                }
            }

            agent Reviewer {
                on review {
                    reply "approved {item}"
                }
            }
            '''
        )

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(["orchestrate", str(ix_file), "--agent", "Coordinator"])

        self.assertEqual(code, 0)
        text = stdout.getvalue()
        self.assertIn("ORCHESTRATION COMPLETE: 1 handoff", text)
        self.assertIn("HANDOFF Reviewer.review -> verdict: approved request", text)
        self.assertIn("Final: approved request", text)

    def test_cli_orchestrate_json_emits_handoffs(self):
        ix_file = self._write_ix(
            '''
            agent Coordinator {
                on start {
                    send Reviewer.review as verdict with item = "request"
                }
            }

            agent Reviewer {
                on review {
                    reply "approved {item}"
                }
            }
            '''
        )

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(["orchestrate", str(ix_file), "--agent", "Coordinator", "--json"])

        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["handoffs"][0]["target_agent"], "Reviewer")
        self.assertEqual(payload["handoffs"][0]["output_value"], "approved request")

    def _write_ix(self, source: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "program.ix"
        path.write_text(source, encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
