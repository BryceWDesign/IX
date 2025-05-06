# ix_parser.py
# IX Language — Minimal Interpreter Prototype
# Author: @BryceWDesign
# License: MIT

import re

class IXAgent:
    def __init__(self, name):
        self.name = name
        self.memory = {}
        print(f"[INIT] Agent '{self.name}' created.")

    def say(self, message):
        print(f"{self.name}: {message}")

    def remember(self, key, value):
        self.memory[key] = value
        print(f"[MEMORY] {self.name} remembers {key} = {value}")

    def recall(self, key):
        value = self.memory.get(key, "(unknown)")
        print(f"[RECALL] {self.name} recalls {key} = {value}")
        return value

class IXInterpreter:
    def __init__(self, code):
        self.code = code.strip().splitlines()
        self.agent = None

    def run(self):
        for line in self.code:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            self._execute(line)

    def _execute(self, line):
        if line.startswith("agent "):
            name = line.split(" ")[1]
            self.agent = IXAgent(name)
        elif line.startswith("say "):
            if self.agent:
                message = line[4:].strip('"')
                self.agent.say(message)
        elif line.startswith("remember "):
            match = re.match(r'remember (\w+) = "(.+)"', line)
            if match and self.agent:
                key, value = match.groups()
                self.agent.remember(key, value)
        elif line.startswith("recall "):
            key = line.split(" ")[1]
            if self.agent:
                self.agent.recall(key)
        else:
            print(f"[WARN] Unknown command: {line}")
