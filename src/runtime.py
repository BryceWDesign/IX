import re

class IXAgent:
def init(self, code):
self.triggers = {}
self.load(code)

python
Copy
Edit
def load(self, code):
    agent_blocks = re.findall(r"agent\s+(\w+)\s*\{(.*?)\}", code, re.DOTALL)
    for agent_name, body in agent_blocks:
        events = re.findall(r"on\s+(.+?)\s*\{(.*?)\}", body, re.DOTALL)
        for trigger, action in events:
            self.triggers[trigger.strip()] = action.strip()

def run(self, event):
    action = self.triggers.get(event)
    if action:
        lines = action.splitlines()
        for line in lines:
            line = line.strip()
            if line.startswith("say "):
                message = line[5:].strip().strip('"')
                print(f"[Agent]: {message}")
    else:
        print("[Agent]: I don't understand.")
if name == "main":
with open("examples/hello_bot.ix") as f:
code = f.read()

python
Copy
Edit
agent = IXAgent(code)
print("Type 'start', 'ask name', or 'ask weather'. Type 'exit' to quit.")

while True:
    user_input = input("You: ").strip()
    if user_input == "exit":
        break
    elif user_input.startswith("ask "):
        event = user_input
    else:
        event = user_input
    agent.run(event)
