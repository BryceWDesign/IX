# IX Language Design Principles

IX is a declarative scripting language for defining conversational agents and autonomous behaviors.

Its primary design goals are:

## 🧠 Readable by Non-Programmers

IX is meant to be understood by creators, designers, and thinkers — not just developers. Syntax should be minimal, expressive, and avoid unnecessary complexity.

```ix
agent MyBot
  start: Hello there!
  ask "How are you?":
    - "Good": That's great to hear!
    - "Bad": I'm sorry to hear that.
