# Control Flow 🚦

SlopeScript has two kinds of control flow: **conditionals** (rated like ski
trails) and **loops** (gondolas and liftlines). Both are block constructs, so
both close with **`runout`** — the flat section at the bottom of a slope.

## Conditionals — trail ratings

Trails are rated green (easy), blue (intermediate), black (expert). SlopeScript
borrows the rating system for if / else-if / else:

- **`greenCircle (cond)`** — the `if`
- **`blueSquare (cond)`** — an `else if` (zero or more)
- **`blackDiamond`** — the `else` (optional, takes no condition)
- **`runout`** — closes the whole chain

```slopescript
greenCircle (snowfall > 6)
  carve "Powder day!"
blueSquare (snowfall > 2)
  carve "Fresh enough"
blackDiamond
  carve "Groomer day"
runout
```

The first branch whose condition is **truthy** runs; the rest are skipped. (See
[Types & Values](Types-and-Values#truthiness) for what counts as truthy.)

Rules:

- A `blueSquare` or `blackDiamond` without a leading `greenCircle` is a **syntax
  error**.
- You can have any number of `blueSquare` branches.
- `blackDiamond` is optional and comes last.
- Chains **nest freely** — each inner chain has its own `runout`.

```slopescript
greenCircle (open)
  greenCircle (crowded)
    carve "Open but busy"
  blackDiamond
    carve "Open and empty — go!"
  runout
runout
```

## Loops

### `gondola` — while loop

Runs the body as long as the condition stays truthy:

```slopescript
pack laps = 0
gondola (laps < 5)
  laps += 1
  carve "Lap", laps
runout
```

### `liftline` — for-each loop

Iterates over a collection. What it yields depends on what you give it:

| You loop over… | Each iteration binds… |
|---|---|
| a **rack** | the next item |
| **text** | the next character |
| a **locker** | the next key (in insertion order) |

```slopescript
liftline skier in ["Ann", "Bo", "Cy"]
  carve skier
runout

liftline ch in "gnar"
  carve ch                 // g, n, a, r
runout

liftline key in { name: "Big Red", capacity: 6 }
  carve key, "=", lift[key]
runout
```

#### Counting with `laps(n)`

There's no C-style `for (i = 0; ...)`. To count, iterate over `laps(n)` from the
standard library, which produces a rack of numbers:

```slopescript
liftline i in laps(10)      // 0, 1, 2, ... 9
  carve i
runout

liftline i in laps(1, 5)    // 1, 2, 3, 4
  carve i
runout

liftline i in laps(0, 10, 2) // 0, 2, 4, 6, 8
  carve i
runout
```

`laps` has the alias `range`. See [Standard Library](Standard-Library#racks).

### `bail` and `sendIt`

- **`bail`** exits the innermost loop immediately (`break`).
- **`sendIt`** skips to the next iteration (`continue`).

```slopescript
liftline n in laps(100)
  greenCircle (n == 5)
    bail                 // stop the whole loop
  runout
  greenCircle (n % 2 == 0)
    sendIt               // skip even numbers
  runout
  carve n                // 1, 3
runout
```

Using `bail` or `sendIt` **outside a loop** is an error.

## A note on blocks and `runout`

Whitespace and indentation are **not significant** in SlopeScript — indent for
humans; the interpreter reads the `runout` keywords to find block boundaries.
This is why every conditional and loop needs its `runout`: it's what tells the
interpreter where the block ends.

> **Why explicit `runout`?** In SlopeScript 1.0, conditionals closed implicitly,
> which meant code after a conditional could silently land inside its last
> branch. Explicit `runout` (added in 2.0) made every block boundary
> unambiguous. See the [Changelog](https://github.com/arnavj/SlopeScript/blob/main/CHANGELOG.md).

---

Next: [Tricks (Functions)](Tricks-Functions).
