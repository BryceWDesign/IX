import unittest

from ix.ast import AgentBlock, LetStatement, OnBlock, ReplyStatement, TraceStatement
from ix.errors import IXSyntaxError
from ix.parser import parse_ix
from ix.validator import validate_ix


class TestCanonicalIXParser(unittest.TestCase):
    def test_parse_basic_statements(self):
        program = parse_ix(
            '''
            let name = "Bryce"
            remember mission = "evidence-bound agents"
            print name
            reply "Ready"
            trace "reply emitted"
            '''
        )

        self.assertEqual(len(program.statements), 5)
        self.assertIsInstance(program.statements[0], LetStatement)
        self.assertIsInstance(program.statements[3], ReplyStatement)
        self.assertIsInstance(program.statements[4], TraceStatement)

    def test_parse_agent_event_block_with_inline_braces(self):
        program = parse_ix(
            '''
            agent Router {
                on start { reply "Ready" }
                on user_message {
                    trace "message received"
                    reply "Acknowledged"
                }
            }
            '''
        )

        self.assertEqual(len(program.statements), 1)
        agent = program.statements[0]
        self.assertIsInstance(agent, AgentBlock)
        self.assertEqual(agent.name, "Router")
        self.assertEqual(len(agent.statements), 2)
        self.assertIsInstance(agent.statements[0], OnBlock)
        self.assertEqual(agent.statements[0].event, "start")

    def test_rejects_unknown_statement(self):
        with self.assertRaises(IXSyntaxError):
            parse_ix("teleport now")

    def test_validation_rejects_top_level_event(self):
        program = parse_ix('on start { reply "Ready" }')
        diagnostics = validate_ix(program)

        self.assertEqual(len(diagnostics), 1)
        self.assertIn("inside an agent", diagnostics[0].message)


if __name__ == "__main__":
    unittest.main()
