# 📘 IX Language Specification (WIP)

> This document describes the syntax, keywords, and rules for writing valid IX programs.

## 🧠 Philosophy
IX is a language for designing intelligent agents using readable, natural-style syntax.
It prioritizes clarity, structure, and extensibility.

---

## 📜 Basic Syntax

### 💬 Statements
IX code is made of plain-text statements. Each line represents one action, definition, or message.

```
when user says "hi":
    reply "Hello there!"
```

### 🧱 Indentation
Like Python, blocks are defined by indentation. Use **4 spaces** per level.

### 🔤 Strings
Strings are enclosed in double quotes `"like this"`. Escape characters are not required in MVP.

---

## 🔑 Keywords

| Keyword     | Purpose                                 |
|-------------|-----------------------------------------|
| `define`    | Declare an entity or variable           |
| `when`      | Begin a trigger block                   |
| `reply`     | Send a response to the user             |
| `ask`       | Ask a question and wait for a reply     |
| `set`       | Assign a value to a variable            |
| `if`        | Conditional logic                       |
| `else`      | Alternative logic path                  |
| `loop`      | Repeat a block                          |

Example:
```
define name

when user says "hello":
    reply "Hi! What's your name?"
    ask "Name"
    set name to last_answer
    reply "Nice to meet you, {name}!"
```

---

## 🧩 Variables

- Declared using `define <name>`
- Used with `{name}` inside strings
- Updated using `set` and context input

---

## 🧠 Triggers
Triggers are entry points for the agent.

```
when user says "help":
    reply "Here’s what I can do…"
```

Triggers can match simple patterns (exact strings for now).

---

## 🧪 Evaluation & Execution Rules
- Execution starts from the top trigger that matches.
- Replies are sent immediately.
- `ask` halts and waits for user input.
- `set` stores values in memory (context).

---

## 🚧 Planned Features
- Conditionals (`if user.age > 18`)
- Loops for repeated behavior
- State machines or scenes
- Modules and includes
- Webhooks / plugins

---

## 📦 Example
```
define mood

define name

when user says "start":
    reply "Welcome!"
    ask "What’s your name?"
    set name to last_answer
    reply "Nice to meet you, {name}."

when user says "how are you":
    if mood is "happy":
        reply "I’m feeling great!"
    else:
        reply "Could be better."
```

---

## ✨ Goals Recap
- No brackets or symbols — natural language feel
- Human-readable scripts that can be edited by non-devs
- Lightweight runtime and portable logic
