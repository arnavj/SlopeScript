# Modules (traverse) 🗺️

A **traverse** connects two trails: it loads another SlopeScript file so its
tricks and packed gear become available in yours.

## Basic use

```slopescript
summit
  traverse "lib/slopemath.slope"   // path relative to THIS file
  carve gradient(900, 2800)        // gradient() came from the traversed file
lodge
```

The `.slope` extension may be omitted:

```slopescript
traverse "lib/slopemath"
```

## How it works

- The traversed file is a **normal SlopeScript program** — it has its own
  `summit … lodge`.
- It **runs once, in the global scope**, so everything it packs and every trick
  it defines becomes available to the file that traversed it.
- **Repeat traverses of the same file are no-ops** — traverse it from ten places
  and it still only loads once.
- **Cycles are caught**: if trail A traverses trail B and B traverses A, that's a
  runtime error (two trails can't lead into each other).

## Paths

- The path may be **any expression that evaluates to text**, not just a literal.
- **Relative paths resolve against the directory of the file doing the
  traversing** — not the current working directory. So a library can traverse
  its own neighbours reliably no matter where you run the program from.

```slopescript
pack lib = "lib/slopemath.slope"
traverse lib
```

## A library file

Here's `lib/slopemath.slope` — an ordinary program that just defines reusable
tricks and a version constant:

```slopescript
// lib/slopemath.slope — a reusable library of tricks
summit
  pack SLOPEMATH_VERSION = "1.0"

  trick feetToMeters(feet)
    stomp round(feet / 3.28)
  nail

  trick gradient(rise, distance)
    stomp round(rise / distance * 100, 1)
  nail

  trick steepness(percent)
    greenCircle (percent < 25)
      stomp "green circle"
    blueSquare (percent < 40)
      stomp "blue square"
    blackDiamond
      stomp "black diamond"
    runout
  nail
lodge
```

And a program that uses it:

```slopescript
// mountain_tour.slope
summit
  traverse "lib/slopemath.slope"

  carve "slopemath v" + SLOPEMATH_VERSION
  carve "3280 feet is", feetToMeters(3280), "meters"

  pack g = gradient(900, 2800)
  carve "Gradient:", g, "% — that's a", steepness(g)
lodge
```

## Errors inside a traversed file

If a traversed file wipes out, the report tells you it happened while
traversing, so you know which trail the problem is on:

```
⛑️  Ski Patrol Report (lib/slopemath.slope, line 8): ... (while traversing lib/slopemath.slope)
```

## Summary

| Rule | Behaviour |
|---|---|
| When it runs | Once, at the point of the `traverse` statement |
| Scope | Global — its tricks & gear join yours |
| Repeat traverse | No-op |
| Cyclic traverse | Runtime error |
| Path resolution | Relative to the traversing file's directory |
| Extension | `.slope` optional |

---

Next: [Files & the Radio](Files-and-the-Radio) — reading files and talking to
the internet.
