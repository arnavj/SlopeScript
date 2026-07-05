# The REPL 🎮

Run `slope` with **no arguments** for an interactive session — a place to try
things line by line without writing a file.

```
$ slope
🏔️  SlopeScript 2.2.0 — fresh corduroy, no waiting.

⛷️  pack x = 21
⛷️  x * 2
42
⛷️  trick double(n)
···   stomp n * 2
··· nail
⛷️  double(1200)
2400
⛷️  apres
🌙 Last run of the day. See you at first chair!
```

## How it behaves

- **Statements execute immediately.**
- **Bare expressions echo their value** — type `2 + 2` and see `4`. (In a
  program file you'd have to `carve` it.)
- **Multi-line blocks stay open.** A line that opens a block switches the prompt
  to `···` and keeps reading until **every** block is closed with `runout` /
  `nail`.
- **State persists** for the whole session — packed variables and defined tricks
  stick around.
- **`summit` / `lodge` are optional** in the REPL. You're already on the
  mountain.

## Leaving

- Type **`apres`** (après-ski), `exit`, or `quit`.
- Press **Ctrl-D** (end of input).

## Interrupting

Press **Ctrl-C** to **hockey stop** — it clears the current (possibly
half-typed, multi-line) input and gives you a fresh prompt without quitting the
session.

## Running a file through stdin

Piping a program into `slope` runs it as a program rather than starting the
REPL — in that mode `summit` / `lodge` **are** required:

```bash
cat examples/hello.slope | slope
echo 'summit
  carve "hi from stdin"
lodge' | slope
```

## Tips

- Define a trick once and call it repeatedly to explore its behaviour.
- Because expressions echo, the REPL doubles as a calculator: `sqrt(144)`,
  `groom([3,1,2])`, `snowflake(1, 6)`.
- Forgot the exact name of a builtin? The plain aliases work too (`sort` for
  `groom`, `range` for `laps`) — see the [Cheat Sheet](Cheat-Sheet).

---

Prefer zero install? The **[Playground](Playground)** is a REPL-ish editor in
your browser.
