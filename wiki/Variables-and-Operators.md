# Variables & Operators 🎒

## Packing gear (variables)

Declare a variable with **`pack`**, reassign it with **`=`**:

```slopescript
pack speed = 0        // declare
speed = 10            // reassign (must already be packed)
speed += 5            // compound assignment
```

**Reassigning a name that was never packed is an error** — and the message tells
you exactly how to fix it:

```
⛑️  'speed' is not packed — pack it first, like: pack speed = ...
```

This is deliberate: it catches typos (`spede = 10`) instead of silently creating
a second variable.

### Compound assignment

`+=`, `-=`, `*=`, `/=` all work and mean what you'd expect:

```slopescript
pack total = 100
total += 25    // 125
total -= 5     // 120
total *= 2     // 240
total /= 4     // 60
```

### Assigning into racks and lockers

Rack slots and locker entries are assignable targets too:

```slopescript
trails[0] = "Corbet's"
lift.name = "Big Red"
lift["capacity"] = 6
```

### Scope: `pack` vs `=` inside a trick

- **`pack` inside a trick creates a *local* variable** — it exists only for that
  call.
- **Plain `=` walks outward** and updates the nearest already-packed variable
  with that name.

So a trick can update a variable from an enclosing scope with `=`, but `pack`
always makes a fresh local. This is how closures capture and mutate state — see
[Tricks (Functions)](Tricks-Functions).

```slopescript
summit
  pack score = 0

  trick addPoint()
    score = score + 1     // plain = reaches the outer `score`
  nail

  addPoint()
  addPoint()
  carve score              // 2
lodge
```

## Operators

Precedence, from **loosest** (binds last) to **tightest** (binds first):

| Level | Operators | Notes |
|---|---|---|
| logical or | `\|\|` | short-circuits, returns deciding operand |
| logical and | `&&` | short-circuits, returns deciding operand |
| equality | `==` `!=` | never coerces types |
| comparison | `<` `>` `<=` `>=` `in` | two numbers or two texts only |
| additive | `+` `-` | `+` also joins text and concatenates racks |
| multiplicative | `*` `/` `%` | `/` by zero is a *yard sale* |
| unary | `!` `-` | logical not, negation |
| power | `**` | right-associative |
| postfix | `x[i]` `x.key` `f(args)` | indexing, member, call |

### The `+` operator is overloaded

```slopescript
carve 2 + 3            // 5      (numbers add)
carve [1, 2] + [3]     // [1, 2, 3]   (racks concatenate)
carve "Run " + 3       // "Run 3"     (if either side is text, both join as text)
```

If **either** side of `+` is text, the other side is converted to text and the
two are joined. This makes building strings painless (though interpolation is
usually cleaner).

### Division

`/` on two whole numbers gives a whole number **when it divides evenly**, and a
decimal otherwise:

```slopescript
carve 10 / 2     // 5      (not 5.0)
carve 10 / 3     // 3.3333333333333335
```

Dividing by zero is a **yard sale** — a catchable runtime error:

```
⛑️  Yard sale! Division by zero
```

### Logical operators short-circuit

`&&` and `||` don't just return `powder`/`ice` — they return the **deciding
operand**, like in Python or JavaScript:

```slopescript
carve powder && "yes"     // "yes"
carve ice || "fallback"   // "fallback"
carve "" || "default"     // "default"  (empty text is falsy)
```

### The `in` operator

`in` tests membership across all three collection kinds:

```slopescript
carve 2 in [1, 2, 3]                // powder
carve "ow" in "powder"              // powder  (substring)
carve "name" in { name: "Big Red" } // powder  (key present)
```

### Comparisons are strict

- `<` `>` `<=` `>=` compare **two numbers or two texts**. Comparing across types
  (`3 < "5"`) is an **error**, not a silent surprise.
- `==` and `!=` **never coerce**: `1 == "1"` is `ice`.

This strictness is a feature — it turns "why is my sort weird?" bugs into clear
errors at the point of comparison.

---

Next: [Control Flow](Control-Flow) — trail ratings and loops.
