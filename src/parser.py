# src/parser.py

import re

class IXParser:
    def __init__(self):
        # Define a minimal grammar pattern for IX agents
        self.agent_pattern = re.compile(
            r'agent\s+(\w+)\s*\{([^}]*)\}', re.MULTILINE | re.DOTALL)

    def parse(self, code: str):
        agents = []
        for match in self.agent_pattern.finditer(code):
            name = match.group(1).strip()
            body = match.group(2).strip()
            agents.append({
                'name': name,
                'body': body
            })
        return agents
