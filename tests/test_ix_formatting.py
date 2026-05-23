import unittest

from ix.formatting import format_ix
from ix.parser import parse_ix


class TestIXFormatting(unittest.TestCase):
    def test_formats_basic_program(self):
        program = parse_ix('let name="Bryce"\nreply "Hello {name}"')

        formatted = format_ix(program)

        self.assertEqual(formatted, 'let name = "Bryce"\nreply "Hello {name}"\n')

    def test_formats_agent_blocks(self):
        program = parse_ix(
            '''
            agent Router {
                on start { reply "Ready" }
                on user_message {
                    trace "seen"
                    reply "OK"
                }
            }
            '''
        )

        formatted = format_ix(program)

        self.assertEqual(
            formatted,
            'agent Router {\n'
            '    on start {\n'
            '        reply "Ready"\n'
            '    }\n'
            '\n'
            '    on user_message {\n'
            '        trace "seen"\n'
            '        reply "OK"\n'
            '    }\n'
            '}\n',
        )


if __name__ == "__main__":
    unittest.main()
