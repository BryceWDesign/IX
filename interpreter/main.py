"""
IX-GENESIS Interpreter v0.1
Purpose: Reads, executes, and allows evolution of .ix logic files.
"""
import json
import os

class IXInterpreter:
    def __init__(self, ix_path):
        self.ix_path = ix_path
        self.state = {}
        self.instructions = []
    
    def load_ix(self):
        with open(self.ix_path, 'r') as f:
            lines = f.readlines()
        self.instructions = [line.strip() for line in lines if line.strip() and not line.startswith("#")]
    
    def execute(self):
        print("[IX] Executing instructions...")
        for inst in self.instructions:
            if inst.startswith("say "):
                message = inst[4:].strip()
                print("[Agent]:", message)
            elif inst.startswith("remember "):
                key_val = inst[9:].split("=", 1)
                if len(key_val) == 2:
                    key, value = key_val
                    self.state[key.strip()] = value.strip()
            elif inst.startswith("recall "):
                key = inst[7:].strip()
                print("[Memory]:", self.state.get(key, "not found"))

    def save_state(self):
        with open("state.json", "w") as f:
            json.dump(self.state, f, indent=2)

if __name__ == "__main__":
    agent_file = os.path.join("agent", "genesis1.ix")
    ix = IXInterpreter(agent_file)
    ix.load_ix()
    ix.execute()
    ix.save_state()
