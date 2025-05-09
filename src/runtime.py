# src/runtime.py

class Agent:
    def __init__(self, name, events):
        self.name = name
        self.events = events
        self.state = {}

    def trigger(self, event, input_text=None):
        if event not in self.events:
            print(f"[{self.name}] Event '{event}' not defined.")
            return

        actions = self.events[event]
        for action in actions:
            verb = action['verb']
            arg = action.get('arg')

            if verb == 'say':
                print(f"[{self.name}] {arg}")
            elif verb == 'ask':
                user_input = input("> ") if input_text is None else input_text
                self.state['last_input'] = user_input
            else:
                print(f"[{self.name}] Unknown action: {verb}")
