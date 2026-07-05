# Ski Patrol (Error Handling) ⛑️

When something wipes out on the mountain, **ski patrol** catches it.
SlopeScript's error handling is `try` / `catch` / `throw`, spelled `patrol` /
`patroller` / `avalanche`.

## The shape

```slopescript
patrol                                  // try
  pack n = number(chairlift("How many runs?"))
  greenCircle (n < 0)
    avalanche { code: 400, reason: "negative runs" }   // throw
  runout
  carve 100 / n
patroller (whoops)                      // catch — binds the caught value
  carve "⛑️ caught:", whoops
runout
```

- **`patrol`** starts the protected block (the `try`).
- **`patroller (name)`** is the handler (the `catch`); it binds the caught value
  to `name`.
- **`runout`** closes the whole construct.
- **`avalanche value`** throws (the `throw`).

## Throwing with `avalanche`

`avalanche` throws **any value** — text, a number, a condition, or a whole
locker full of detail. The `patroller` catches **exactly** the value thrown:

```slopescript
trick openTrail(name, snowDepth)
  greenCircle (snowDepth < 6)
    avalanche { trail: name, reason: "not enough snow" }
  runout
  carve "✅", name, "is open!"
nail

patrol
  openTrail("Bunny Hill", 2)
patroller (report)
  carve "🚧", report.trail, "is closed:", report.reason
runout
```

Because you can throw a locker, you can attach structured context (codes,
reasons, offending values) to an error and inspect it in the handler.

## Runtime wipeouts are caught too

You don't have to `avalanche` explicitly — the built-in runtime errors are
catchable as well. When a runtime wipeout is caught, `name` is bound to the
**message text**:

```slopescript
patrol
  carve 10 / 0
patroller (whoops)
  carve "⛑️ Patrol caught a wipeout:", whoops
runout
```

Catchable runtime wipeouts include:

- **Division by zero** (a *yard sale*)
- **Rack index out of range**
- **Missing locker key**
- **Type errors** (e.g. comparing a number with text)
- **Tuning failures** (`number("not a number")`)
- **File and radio failures** (missing files, unreachable hosts, bad JSON)

## Nesting and re-throwing

Patrols nest. An `avalanche` inside a handler rides **up** to the next `patrol`
further out:

```slopescript
patrol
  patrol
    avalanche "inner problem"
  patroller (e)
    carve "inner caught:", e
    avalanche "escalated"       // re-throw to the outer patrol
  runout
patroller (outer)
  carve "outer caught:", outer   // "escalated"
runout
```

## A real pattern: retry loop

Wrap risky input in `patrol` and use `sendIt` to retry:

```slopescript
gondola (guess != secret)
  patrol
    guess = number(chairlift("Enter your guess:"))
  patroller (whoops)
    carve "That's not a number — try again!"
    sendIt                       // back to the top of the loop
  runout
  // ... use guess ...
runout
```

## What ski patrol will *not* catch

Two things ride right past `patroller` on purpose:

1. **Syntax errors** — the program never starts, so there's nothing to catch.
2. **End of input (`LiftsClosed`)** — when `chairlift` runs out of input (EOF),
   the "lifts close" and the program stops. A `patroller` deliberately does
   **not** catch this, so retry loops can't spin forever on empty input.

## Uncaught errors

An uncaught wipeout stops the program with a friendly report naming the file and
line:

```
⛑️  Ski Patrol Report (run.slope, line 7): Yard sale! Division by zero
```

Every SlopeScript error is designed to **teach**: what went wrong, where, and
often how to fix it.

---

Next: [Modules](Modules) — splitting a program across files.
