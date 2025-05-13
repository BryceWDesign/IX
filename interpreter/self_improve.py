"""
IX-GENESIS Self-Improvement v0.1
Basic scaffolding for modifying .ix scripts based on feedback.
"""

import random

class SelfImprover:
    def __init__(self, filepath):
        self.filepath = filepath

    def evolve(self):
        with open(self.filepath, 'r') as f:
            lines = f.readlines()

        # Very primitive evolution: randomly reword or duplicate one line
        if not lines:
            return

        i = random.randint(0, len(lines) - 1)
        chosen = lines[i].strip()
        mutation = f"# mutated: {chosen}\n"

        # Insert mutation
        lines.insert(i + 1, mutation)

        with open(self.filepath, 'w') as f:
            f.writelines(lines)

        print(f"[Evolve] Modified: {self.filepath}")

if __name__ == "__main__":
    improver = SelfImprover("agent/genesis1.ix")
    improver.evolve()
