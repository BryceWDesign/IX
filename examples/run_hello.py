# examples/run_hello.py

from src.parser import parse_ix
from src.runtime import Agent

if __name__ == "__main__":
    with open("examples/hello_bot.ix") as f:
        code = f.read()

    agent_def = parse_ix(code)
    agent = Agent(agent_def['name'], agent_def['events'])

    agent.trigger("start")
    agent.trigger("ask")
