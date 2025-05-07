import unittest
from engine.parser import parse_ix_code
from engine.runtime import IXRuntime

class TestIXEngine(unittest.TestCase):

    def test_parse_basic(self):
        code = 'say "Hello World"'
        ast = parse_ix_code(code)
        self.assertIsInstance(ast, list)
        self.assertGreater(len(ast), 0)

    def test_runtime_say(self):
        code = 'say "Hello from IX"'
        runtime = IXRuntime()
        runtime.run(code)
        # This won't assert console output — you can improve this with mocking if desired

if __name__ == '__main__':
    unittest.main()
