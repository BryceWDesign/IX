import unittest

from ix.parser import parse_ix
from ix.runtime import IXRuntime, IXRuntimeError, run_ix


class TestCanonicalIXRuntime(unittest.TestCase):
    def test_runs_basic_program_with_trace(self):
        program = parse_ix(
            '''
            let name = "Bryce"
            remember mission = "evidence"
            print "Hello {name}"
            reply "Mission: {mission}"
            assert name == "Bryce"
            trace "done for {name}"
            '''
        )

        result = run_ix(program)

        self.assertEqual(result.status, "completed")
        self.assertEqual(result.outputs, ["Hello Bryce"])
        self.assertEqual(result.replies, ["Mission: evidence"])
        self.assertEqual(result.memory["mission"], "evidence")
        self.assertGreaterEqual(len(result.trace), 8)
        self.assertEqual(result.trace[0].kind, "run.start")
        self.assertEqual(result.trace[-1].kind, "run.complete")

    def test_runs_selected_agent_event(self):
        program = parse_ix(
            '''
            agent Router {
                on start {
                    reply "Ready"
                }
                on user_message {
                    reply "You said: {input_text}"
                }
            }
            '''
        )

        result = IXRuntime().run(
            program,
            agent="Router",
            event="user_message",
            inputs={"input_text": "hello"},
        )

        self.assertEqual(result.replies, ["You said: hello"])
        self.assertEqual(result.variables["input_text"], "hello")

    def test_records_policy_and_human_approval(self):
        program = parse_ix(
            '''
            deny tool.email.send reason "No email without review"
            require human_approval reason "Sensitive action"
            '''
        )

        result = run_ix(program)

        self.assertEqual(result.policies[0]["effect"], "deny")
        self.assertEqual(result.policies[0]["target"], "tool.email.send")
        self.assertEqual(result.approvals_required, ["Sensitive action"])

    def test_failed_assertion_raises_runtime_error(self):
        program = parse_ix('assert "safe" == "unsafe"')

        with self.assertRaises(IXRuntimeError):
            run_ix(program)


if __name__ == "__main__":
    unittest.main()
