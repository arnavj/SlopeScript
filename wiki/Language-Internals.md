# Language Internals ⚙️

How the SlopeScript interpreter actually works. This is a friendly map of
[`slopescript.py`](https://github.com/arnavj/SlopeScript/blob/main/slopescript.py)
— the entire language (lexer, parser, interpreter, standard library, REPL, and
CLI) in a single ~2,000-line, zero-dependency Python file. It's built to be read
top to bottom in one sitting: a small, complete tour of how languages work.

## The pipeline

SlopeScript is a classic **tree-walking interpreter**. Source text flows through
three stages:

```
source text
   │
   ▼   Lexer.tokenize()
tokens  ──►  a flat list of Token(type, value, line)
   │
   ▼   Parser.parse_program()
AST     ──►  nested tuples like ("carve", [args], line)
   │
   ▼   Interpreter.run()
effects ──►  values printed, files written, etc.
```

There's no bytecode and no separate compile step — the interpreter walks the
tree directly.

## 1. The Lexer

`class Lexer` turns characters into a list of `Token`s. It scans one character
at a time (`current`, `peek`, `advance`), skipping whitespace and both comment
styles (`// line` and `/* block */`), and recognises:

- **identifiers / keywords** (`read_identifier`),
- **numbers** (`read_number`),
- **text** (`read_string`), including escape sequences and, importantly,
  **string interpolation** (`read_interpolation`) — `{…}` inside a literal is
  lexed so the parser can evaluate the embedded expression,
- **operators** (`read_operator`).

Every token carries its **line number**, which is what makes error messages able
to point at the exact line.

## 2. The Parser

`class Parser` is a hand-written **recursive-descent** parser. It consumes the
token list and produces an AST made of plain Python **tuples** (e.g. a
conditional becomes `("if", branches, else_body, line)`).

- `parse_program` expects `summit … lodge`.
- `parse_statement` dispatches on the current keyword to the right handler
  (`parse_pack`, `parse_carve`, `parse_conditional`, `parse_gondola`,
  `parse_liftline`, `parse_trick`, `parse_patrol`, …).
- `parse_block` reads statements until it hits a block terminator (`runout`,
  `nail`, `blueSquare`, …), which is how the `runout`-delimited block structure
  is recognised without significant whitespace.
- Expression parsing is a **precedence ladder** — one method per level, loosest
  to tightest: `parse_or → parse_and → parse_equality → parse_comparison →
  parse_additive → parse_multiplicative → parse_unary → parse_power →
  parse_postfix → parse_primary`. This ladder *is* the operator-precedence table
  from the [Grammar](Grammar).

The parser also enforces the two placement rules (a call's `(` on the same line
as the callee; `carve`/`stomp` args starting on their own line) so statements
can't silently merge.

Helper functions `describe_type` / `describe_token` produce the human-readable
names that show up in syntax-error messages.

## 3. The Interpreter

The interpreter walks the AST. Its core support cast:

### Environments (scope)

`class Environment` is a scope: a dict of names plus a link to its `parent`.

- `declare` creates a **local** binding (this is what `pack` does).
- `assign` **walks outward** through parents to find an existing binding (this is
  what plain `=` does), which is exactly the scope rule described in
  [Variables & Operators](Variables-and-Operators#scope-pack-vs--inside-a-trick).
- `get` looks a name up through the parent chain.

Function calls create a child environment whose parent is the trick's
**closure** — the environment where the trick was defined — which is what makes
[closures](Tricks-Functions#closures) work.

### Values

SlopeScript values reuse Python types where possible: numbers are Python
`int`/`float`, text is `str`, `powder`/`ice` are `True`/`False`, `whiteout` is
`None`, racks are `list`, lockers are `dict`. Functions are represented by two
small classes:

- `class Trick` — a user-defined function: its `name`, `params`, `body` (AST),
  and captured `closure`.
- `class BuiltinRef` — a first-class handle to a standard-library function, so
  builtins are values you can pass around too.

Helpers `format_value` / `format_inner` implement the printing rules (quoting
text inside collections, dropping trailing `.0`), `is_truthy` implements the
[truthiness table](Types-and-Values#truthiness), and `type_name` backs the
`type()` builtin.

### Control flow via signals

Non-local control flow is implemented with Python exceptions used as **signals**
— a clean, common technique for tree-walkers:

| Signal class | Raised by | Caught by |
|---|---|---|
| `StompSignal` | `stomp` | the trick-call machinery (carries the return value) |
| `BailSignal` | `bail` | the enclosing loop |
| `SendItSignal` | `sendIt` | the enclosing loop (skips to next iteration) |

### Errors that teach

The error hierarchy is deliberate, because *errors are a feature*:

- `SlopeError` (base) — carries a message and a line number.
  - `SlopeSyntaxError` — raised during lexing/parsing.
  - `SlopeRuntimeError` — the catchable wipeouts (yard sales, bad indexes,
    missing keys, type errors).
  - `AvalancheError` — a user `avalanche`; carries the **thrown value** (any
    type), which is what `patroller` binds.
  - `LiftsClosedError` — end of input during `chairlift`. Notably, **`patroller`
    does not catch this** (and neither do syntax errors), so retry loops can't
    spin forever.

`patrol` catches `SlopeRuntimeError` and `AvalancheError` and binds the value or
message; everything else propagates to the top and is printed as a *Ski Patrol
Report* with file and line.

## 4. The standard library

`build_builtins()` constructs the Base Lodge as a dict of `BuiltinRef`s. Each
builtin is a small Python closure `def _name(args, line, interp)` registered with
its name, arg-count bounds, and any aliases. Argument-count and type checking
(`_require_number`, `_require_rack`, `_require_text`, `_require_locker`) raise the
same teaching-quality errors as the rest of the language. See the
[Standard Library](Standard-Library) page for the surface.

## 5. REPL & CLI

The bottom of the file is the front door:

- The **REPL** reads lines, keeps a block open across lines until it balances,
  echoes expression values, and persists one `Environment` for the session. See
  [The REPL](REPL).
- The **CLI** (`main`) handles `--version` / `--help`, running a file, `slope
  run`, and reading a program from stdin. `pyproject.toml` wires the `slope` and
  `slopescript` console entry points to `slopescript:main`.

## Performance

It's a tree-walker, so it's built for clarity, not number-crunching. Version 2.1
added fast paths for number math, truthiness, and trick calls — roughly **1.4×**
on tight loops and **1.2×** on call-heavy recursion (see
[`benchmarks/`](https://github.com/arnavj/SlopeScript/tree/main/benchmarks)).
For heavy computation, reach for a compiled language; for learning how languages
work, read this one.

## Reading order

If you want to read the source, this order tracks the pipeline:

1. The exception/signal classes at the top — the vocabulary of control flow.
2. `Lexer` — text → tokens.
3. `Parser` — tokens → AST.
4. `Environment`, `Trick`, `BuiltinRef`, and the `format_*` / `is_truthy`
   helpers.
5. `build_builtins` — the standard library.
6. The interpreter's statement/expression evaluation.
7. The REPL and `main`.

---

Want to change it? See [Contributing](Contributing).
