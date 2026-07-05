<p align="center">
  <img src="https://raw.githubusercontent.com/arnavj/SlopeScript/main/logo.svg" alt="SlopeScript Logo" width="280">
</p>

# 🎿 SlopeScript Wiki

**A programming language where code flows downhill.** Real functions, real data
structures, real error handling — with fresh powder on top.

SlopeScript is a dynamically-typed, imperative language with a skiing-shaped
syntax. Every program starts at the **summit** and ends at the **lodge**. In
between you pack gear (variables), carve output into the snow, ride gondolas
(while loops) and liftlines (for loops), land tricks (functions), and when
things go wrong, ski patrol (error handling) has your back.

It's a *real* working language — first-class functions with recursion, arrays
and dictionaries, a ~50-function standard library (including HTTP and file
I/O), precise error messages with line numbers, an interactive REPL, a browser
playground, and a zero-dependency single-file interpreter.

```slopescript
summit
  trick fibonacci(n)
    greenCircle (n < 2)
      stomp n
    runout
    stomp fibonacci(n - 1) + fibonacci(n - 2)
  nail

  liftline i in laps(10)
    carve "fib({i}) = {fibonacci(i)}"
  runout
lodge
```

## 🧭 New here? Start with the trail map

| If you want to… | Go to |
|---|---|
| Install it and run your first program | **[Getting Started](Getting-Started)** |
| See the whole language in 60 seconds | **[The Language Tour](The-Language-Tour)** |
| Try it right now, no install | **[Playground](Playground)** |
| Look up a keyword or a builtin fast | **[Cheat Sheet](Cheat-Sheet)** · **[Standard Library](Standard-Library)** |
| Decode the skiing metaphor | **[Glossary](Glossary)** |

## 📚 The full trail system

**Language guide** — read these top to bottom for a complete tour:

1. [Types & Values](Types-and-Values) — numbers, text, conditions, whiteout, racks, lockers, tricks
2. [Variables & Operators](Variables-and-Operators) — `pack`, reassignment, precedence
3. [Control Flow](Control-Flow) — trail ratings (if/else) and loops
4. [Tricks (Functions)](Tricks-Functions) — definitions, recursion, closures, first-class values
5. [Racks & Lockers](Racks-and-Lockers) — arrays and dictionaries
6. [Ski Patrol (Error Handling)](Error-Handling) — `patrol` / `patroller` / `avalanche`
7. [Modules](Modules) — splitting a program across files with `traverse`
8. [Files & the Radio](Files-and-the-Radio) — file I/O and HTTP + JSON

**Reference:**

- [Standard Library](Standard-Library) — every builtin in the Base Lodge
- [Grammar](Grammar) — the formal EBNF
- [Cheat Sheet](Cheat-Sheet) — the whole language on one page
- [Glossary](Glossary) — skiing term → programming concept

**Project:**

- [The REPL](REPL) — the interactive session
- [Examples](Examples) — a guided tour of the sample programs
- [Language Internals](Language-Internals) — how the interpreter works
- [FAQ](FAQ) — common questions
- [Contributing](Contributing) — help build SlopeScript

## 🧭 Why SlopeScript?

Learning-to-code tools tend to be either toys (fun, but you outgrow them in a
week and none of it transfers) or real languages (transferable, but the first
error message sends you to Stack Overflow). SlopeScript sits deliberately in the
gap:

- **It's a real language** — first-class functions, closures, data structures,
  modules, error handling. Every concept transfers 1:1 to Python or JavaScript.
- **It's genuinely friendly** — errors name the line and tell you how to fix it,
  the whole language fits on one cheat sheet, and the metaphor does real
  pedagogical work (`patrol` catches wipeouts; blocks end at the `runout`).
- **Zero setup at every stage** — playground in the browser, then one single-file
  interpreter, then `pip install`. No toolchain cliff.

---

*Code flows downhill. Ski safe.* ⛷️❄️
