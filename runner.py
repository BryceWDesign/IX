# runner.py

import sys
from core.ix_parser import IXParser

def main():
    if len(sys.argv) != 2:
        print("Usage: python runner.py <ix_script.ix>")
        sys.exit(1)

    filepath = sys.argv[1]
    try:
        with open(filepath, 'r') as file:
            code = file.read()
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        sys.exit(1)

    parser = IXParser()
    output = parser.run(code)
    print("Output:\n" + output)

if __name__ == "__main__":
    main()
