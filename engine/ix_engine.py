# IX Engine + Parser Prototype (MVP)

# --- 1. Define Token Types for the IX Language
from enum import Enum, auto

class TokenType(Enum):
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()
    COLON = auto()
    DASH = auto()
    INDENT = auto()
    DEDENT = auto()
    NEWLINE = auto()
    EOF = auto()

# --- 2. Lexer for IX Language (very simple YAML-inspired syntax)
import re

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

class Lexer:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.lines = code.splitlines()

    def tokenize(self):
        for line in self.lines:
            if not line.strip():
                continue
            indent = len(line) - len(line.lstrip())
            if indent > 0:
                self.tokens.append(Token(TokenType.INDENT))
            parts = re.split(r'(:\s*|\s+-\s+|\s+)', line.strip())
            for part in parts:
                if not part or part.isspace():
                    continue
                elif part.strip() == ':':
                    self.tokens.append(Token(TokenType.COLON))
                elif part.strip() == '-':
                    self.tokens.append(Token(TokenType.DASH))
                elif re.match(r'^\d+$', part):
                    self.tokens.append(Token(TokenType.NUMBER, int(part)))
                elif re.match(r'^".*"$', part):
                    self.tokens.append(Token(TokenType.STRING, part.strip('"')))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, part))
            self.tokens.append(Token(TokenType.NEWLINE))
        self.tokens.append(Token(TokenType.EOF))
        return self.tokens

# --- 3. AST Node Types
class Node:
    pass

class Agent(Node):
    def __init__(self, name, attributes):
        self.name = name
        self.attributes = attributes

    def __repr__(self):
        return f"Agent({self.name}, {self.attributes})"

# --- 4. Parser
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def consume(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def peek(self):
        return self.tokens[self.pos]

    def parse(self):
        agents = []
        while self.peek().type != TokenType.EOF:
            agents.append(self.parse_agent())
        return agents

    def parse_agent(self):
        name_token = self.consume()
        if name_token.type != TokenType.IDENTIFIER:
            raise SyntaxError("Expected agent name")
        colon = self.consume()
        if colon.type != TokenType.COLON:
            raise SyntaxError("Expected ':' after agent name")
        attributes = {}
        while self.peek().type != TokenType.IDENTIFIER and self.peek().type != TokenType.EOF:
            self.consume()  # eat indent/newline
            if self.peek().type == TokenType.IDENTIFIER:
                key = self.consume().value
                self.consume()  # colon
                val_token = self.consume()
                val = val_token.value
                attributes[key] = val
        return Agent(name_token.value, attributes)

# --- 5. Interpreter
class Interpreter:
    def __init__(self, agents):
        self.agents = agents

    def run(self):
        for agent in self.agents:
            print(f"Running agent: {agent.name}")
            for key, value in agent.attributes.items():
                print(f"  {key} => {value}")

# --- 6. Entry Point (Sample IX Code)
ix_code = """
Scout:
  goal: "monitor internet"
  location: "online"
  priority: 5

Helper:
  goal: "assist humans"
  location: "local"
  priority: 8
"""

lexer = Lexer(ix_code)
tokens = lexer.tokenize()
parser = Parser(tokens)
agents = parser.parse()
interpreter = Interpreter(agents)
interpreter.run()
