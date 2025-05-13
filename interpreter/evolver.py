"""
IX-GENESIS Evolver v0.1
Purpose: Reads .ix file, applies simulated mutation, rewrites modified logic.
"""

import os
import random
from datetime import datetime

class IXEvolver:
    def __init__(self, path):
        self.path = path
        self.instructions = []

    def load_ix(self):
        with open(self.path, 'r') as f:
            self.instructions = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("#")]

    def mutate(self):
        if not self.instructions:
            return

        mutation_type = random.choice(["add", "replace", "remove"])
        if mutation_type == "add":
            new_line = 'say I have grown at ' + datetime.now().isoformat()
            self.instructions.append(new_line)

        elif mutation_type == "replace":
            index = random.randint(0, len(self.instructions)-1)
            self.instructions[index] = 'say This was evolved on ' + datetime.now().isoformat()

        elif mutation_type == "remove" and len(self.instructions) > 1:
            index = random.randint(0, len(self.instructions)-1)
            self.instructions.pop(index)

    def save_ix(self):
        with open(self.path, 'w') as f:
            f.write("# Auto-mutated by IX-GENESIS\n")
            for line in self.instructions:
                f.write(line + '\n')

if __name__ == "__main__":
    file_to_mutate = os.path.join("agent", "genesis1.ix")
    evolver = IXEvolver(file_to_mutate)
    evolver.load_ix()
    evolver.mutate()
    evolver.save_ix()
