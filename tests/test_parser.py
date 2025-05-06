import unittest
from src.parser import IXParser  # Adjust import as needed

class TestIXParser(unittest.TestCase):
    def test_basic_parse(self):
        parser = IXParser()
        result = parser.parse("agent Test {}")
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
