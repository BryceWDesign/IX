# core/ix_parser.py

import re

class IXParser:
    def __init__(self):
        self.variables = {}

    def parse(self, line):
        line = line.strip()
        if line.startswith("let "):
            return self.handle_let(line)
        elif line.startswith("print "):
            return self.handle_print(line)
        else:
            raise SyntaxError(f"Unrecognized command: {line}")

    def handle_let(self, line):
        try:
            _, rest = line.split("let ", 1)
            name, value = rest.split("=", 1)
            name, value = name.strip(), value.strip()
            self.variables[name] = eval(value, {}, self.variables)
            return f"{name} = {self.variables[name]}"
        except Exception as e:
            return f"Error in 'let': {e}"

    def handle_print(self, line):
        try:
            _, expr = line.split("print ", 1)
            result = eval(expr.strip(), {}, self.variables)
            return str(result)
        except Exception as e:
            return f"Error in 'print': {e}"

    def run(self, script):
        output = []
        for line in script.splitlines():
            if line.strip():
                result = self.parse(line)
                output.append(result)
        return "\n".join(output)
