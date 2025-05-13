"""
IX Runtime v0.1
Interprets .ix agent files with support for memory, speech, and communication.
"""

import os
from interpreter.comms import IXBus

class IXAgent:
    def __init__(self, name, ix_file):
        self.name = name
        self.ix_file = ix_file
        self.memory = {}
        self.bus = IXBus()
        self.instructions = []

    def load(self):
        with open(self.ix_file, 'r') as f:
            self.instructions = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    def interpret(self):
        print(f"== Running agent: {self.name} ==")
        for line in self.instructions:
            if line.startswith("say "):
                msg = line[4:]
                print(f"[{self.name}] says: {msg}")
                self.bus.send(self.name, msg)

            elif line.startswith("remember "):
                key, val = line[9:].split(" = ")
                self.memory[key.strip()] = val.strip()

            elif line.startswith("recall "):
                key = line[7:].strip()
                val = self.memory.get(key, "(nothing)")
                print(f"[{self.name}] recalls: {key} = {val}")
                self.bus.send(self.name, f"memory: {key} = {val}")

            elif line.startswith("listen"):
                print(f"[{self.name}] Listening...")
                messages = self.bus.receive(self.name)
                for m in messages:
                    print(f"[{self.name}] hears: {m}")

if __name__ == "__main__":
    agent1 = IXAgent("GENESIS I", "agent/genesis1.ix")
    agent1.load()
    agent1.interpret()

    agent2 = IXAgent("GENESIS II", "agent/genesis2.ix")
    agent2.load()
    agent2.interpret()
