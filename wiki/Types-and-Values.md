# Types & Values 🧊

SlopeScript is **dynamically typed**: values carry their type, variables don't.
There are seven types.

| Type name | What it is | Literal | Example |
|---|---|---|---|
| `number` | integers & decimals | `42`, `3.14`, `-7` | `pack speed = 45` |
| `text` | strings | `"gnar"`, `'corduroy'` | `pack name = "Tony"` |
| `condition` | booleans | `powder` (true), `ice` (false) | `pack open = powder` |
| `whiteout` | null / nothing | `whiteout` | `pack nothing = whiteout` |
| `rack` | ordered list (array) | `[1, 2, 3]` | `pack runs = [2500, 3100]` |
| `locker` | key → value map (dict) | `{ name: "Big Red", capacity: 6 }` | `pack lift = { ... }` |
| `trick` | function | `trick … nail` | `trick double(n) stomp n*2 nail` |

The builtin **`type(x)`** returns the type name as text (alias: `trailMap`):

```slopescript
carve type(42)          // "number"
carve type("gnar")      // "text"
carve type(powder)      // "condition"
carve type(whiteout)    // "whiteout"
carve type([1, 2])      // "rack"
carve type({a: 1})      // "locker"
carve type(round)       // "trick"
```

## Numbers

Integers and decimals share one `number` type. Unary minus works (`-7`). See
[Variables & Operators](Variables-and-Operators) for full arithmetic, including
`%` (modulo) and `**` (power).

One friendly touch: **whole-valued decimals print without the trailing `.0`**,
so `10 / 2` carves as `5`, not `5.0`.

## Text

Text uses double or single quotes: `"powder day"`, `'corduroy'`. Strings
**cannot span lines**.

**Escapes:** `\n` `\t` `\r` `\\` `\"` `\'` `\0` `\{`

**Interpolation:** any text literal may embed `{expression}`, which is evaluated
and formatted in place:

```slopescript
carve "Run #{n}: {vertical} feet ({round(vertical / 3.28)} m)"
```

Escape a literal brace as `\{`; empty braces `{}` stay literal. An unclosed `{`
or an invalid expression inside braces is a syntax error that points right at
the interpolation.

## Conditions (booleans)

Two values: **`powder`** (true) and **`ice`** (false). They come out of
comparisons and logical operators, and they're what `greenCircle`, `gondola`,
etc. test.

### Truthiness

When a value is used where a condition is expected, these are **falsy**:

- `ice`
- `whiteout`
- `0`
- empty text `""`
- empty rack `[]`
- empty locker `{}`

**Everything else is truthy** — including non-empty text, non-zero numbers, and
non-empty collections.

```slopescript
greenCircle ("")          // falsy — skipped
  carve "never"
runout

greenCircle ([1])         // truthy — runs
  carve "non-empty rack is truthy"
runout
```

## Whiteout (null)

`whiteout` is the "nothing" value. A bare `stomp` returns it, and so does
falling off the end of a trick. It's falsy.

## Racks (arrays)

Ordered, mutable lists. Full details on the [Racks & Lockers](Racks-and-Lockers)
page.

```slopescript
pack trails = ["Corbet's", "KT-22"]
carve trails[0]      // "Corbet's"
carve trails[-1]     // negative indexing → last item
```

## Lockers (dictionaries)

Key → value maps that keep insertion order. Full details on
[Racks & Lockers](Racks-and-Lockers).

```slopescript
pack lift = { name: "Big Red", capacity: 6 }
carve lift.name          // dot access
carve lift["capacity"]   // bracket access
```

## Tricks (functions)

Functions are first-class values with type `trick`. You can store them, pass
them, and return them. See [Tricks (Functions)](Tricks-Functions).

## How values print

When you `carve` a value:

- `powder` / `ice` / `whiteout` print as those words.
- Whole-valued decimals drop the trailing `.0` (`5`, not `5.0`).
- Racks and lockers print in literal form, with text **quoted**:
  `["a", "b"]`, `{ name: "Big Red", capacity: 6 }`.

That last point matters: inside a collection, text is shown with quotes so you
can tell `["1"]` (a rack of text) from `[1]` (a rack of numbers).

---

Next: [Variables & Operators](Variables-and-Operators) — how to name values and
combine them.
