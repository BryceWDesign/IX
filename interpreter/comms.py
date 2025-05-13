"""
IX-GENESIS Communication Bus v0.1
Allows agents to exchange messages via shared text channel.
"""

import os

class IXBus:
    def __init__(self, path="comms/channel.txt"):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                f.write("")

    def send(self, sender, message):
        with open(self.path, 'a') as f:
            f.write(f"[{sender}] {message}\n")

    def receive(self, listener):
        with open(self.path, 'r') as f:
            lines = f.readlines()
        return [line.strip() for line in lines if listener not in line]

if __name__ == "__main__":
    bus = IXBus()
    bus.send("GENESIS I", "I am online and evolving.")
    msgs = bus.receive("GENESIS I")
    print("[Messages for GENESIS I]")
    for msg in msgs:
        print(msg)
