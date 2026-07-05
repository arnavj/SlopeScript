# Tricks (Functions) 🤸

A **trick** is a function. You define one with `trick`, return from it with
`stomp` (stomp the landing!), and finish the definition with `nail` (or
`runout` — they're interchangeable).

```slopescript
trick average(rackOfNumbers)
  greenCircle (length(rackOfNumbers) == 0)
    stomp 0
  runout
  stomp sum(rackOfNumbers) / length(rackOfNumbers)
nail
```

## Defining and returning

- **`trick name(param1, param2, ...)`** starts a definition.
- **`nail`** (or `runout`) finishes it.
- **`stomp expr`** returns a value.
- A **bare `stomp`** — and **falling off the end** of a trick — returns
  `whiteout`.

```slopescript
trick greet(name)
  carve "Shred on, " + name + "! 🎿"
nail                          // no stomp → returns whiteout

trick verticalPerRun(total, runs)
  greenCircle (runs == 0)
    stomp 0                   // early return
  runout
  stomp round(total / runs)
nail
```

## Calling

Call with parentheses. The opening `(` of a call must be on the **same line** as
the thing being called (so statements never bleed together).

```slopescript
carve verticalPerRun(24000, 9)     // 2667
```

Calling with the **wrong number of arguments** is an error that names the
parameters it expected:

```
⛑️  Trick 'verticalPerRun' expects 2 arguments (total, runs), got 1
```

## Recursion

Tricks can call themselves and each other:

```slopescript
trick fibonacci(n)
  greenCircle (n < 2)
    stomp n
  runout
  stomp fibonacci(n - 1) + fibonacci(n - 2)
nail

carve fibonacci(10)     // 55
```

Recursion deeper than **200 calls** triggers a friendly avalanche-risk error
(instead of a raw Python stack overflow):

```
⛑️  Avalanche risk! Recursion too deep (over 200 calls)
```

## Scope

- Parameters and `pack`ed names are **local** to the call.
- Plain `=` reaches **outward** to update variables in enclosing scopes.

See [Variables & Operators](Variables-and-Operators#scope-pack-vs--inside-a-trick)
for the full rules.

A trick defined with the **same name as a builtin shadows the builtin** for the
rest of the program.

## Tricks are first-class values

A trick name (or a Base Lodge builtin name) evaluates to the trick **itself**,
so tricks can be stored, passed, and returned like any other value.

```slopescript
pack tidy = groom            // a builtin is a value
carve tidy([3, 1, 2])        // [1, 2, 3]
```

### Anonymous tricks

Write a trick inline as an expression — no name:

```slopescript
pack square = trick(n) stomp n * n runout
carve square(9)              // 81
```

Anonymous tricks shine with higher-order builtins:

```slopescript
pack runs = [2500, 3100, 1800, 2900]
carve filter(runs, trick(feet) stomp feet > 2400 runout)   // [2500, 3100, 2900]
carve map(runs,    trick(feet) stomp feet / 3.28 runout)   // feet → meters
carve reduce(runs, trick(a, b) stomp a + b runout)         // day total
```

### Storing tricks in lockers and racks

```slopescript
pack convert = {
  toMeters: trick(feet) stomp round(feet / 3.28) runout,
  toMiles:  trick(feet) stomp round(feet / 5280, 2) runout
}
carve convert.toMeters(3280)     // 1000
```

### Anything that evaluates to a trick is callable

```slopescript
rack[0](x)          // call a trick stored in a rack
locker.fn(x)        // call a trick stored in a locker
makeCounter()()     // call the trick returned by a call
```

Calling something that **isn't** a trick is a runtime error.

## Closures

A trick captures the scope where it was **created**, so it can remember and
mutate that state after the enclosing trick has returned:

```slopescript
trick makeCounter()
  pack count = 0
  stomp trick()
    count += 1      // reaches the captured `count`
    stomp count
  runout
nail

pack lap = makeCounter()
carve lap(), lap(), lap()    // 1 2 3
```

Each call to `makeCounter()` produces a fresh, independent counter.

## Quick reference

| Keyword | Meaning |
|---|---|
| `trick name(params)` | begin a function definition |
| `trick(params)` | an anonymous (inline) function |
| `nail` / `runout` | end a trick definition |
| `stomp expr` | return a value |
| `stomp` | return `whiteout` |

---

Next: [Racks & Lockers](Racks-and-Lockers) — the data structures.
