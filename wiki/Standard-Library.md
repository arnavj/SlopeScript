# The Base Lodge (Standard Library) 🛖

Around **50 built-in functions**, all global — no imports needed. Themed names
are canonical; the plain aliases in parentheses work identically, so if you
forget that "sort" is `groom`, `sort` still works.

- [Input & output](#input--output)
- [Conversion & inspection](#conversion--inspection)
- [Racks](#racks)
- [Higher-order](#higher-order)
- [Text](#text)
- [Lockers](#lockers)
- [Math](#math)
- [Files](#files)
- [The radio (HTTP + JSON)](#the-radio-http--json)
- [Misc](#misc)
- [Alias quick-reference](#alias-quick-reference)

---

## Input & output

| Function | Returns |
|---|---|
| `chairlift(prompt?)` | one line of input, as text |

`carve` is a statement (keyword), not a function — see
[Control Flow](Control-Flow) and [The Language Tour](The-Language-Tour).

```slopescript
pack name = chairlift("Your name? ")
```

When input runs out (EOF), the **lifts close**: the program stops with a
`LiftsClosed` report that `patroller` deliberately doesn't catch. See
[Error Handling](Error-Handling).

## Conversion & inspection

| Function | Alias | Returns |
|---|---|---|
| `number(x)` | `tune` | `x` as a number; errors if it won't tune |
| `text(x)` | — | `x` as text |
| `type(x)` | `trailMap` | the type name as text |

```slopescript
carve number("42")      // 42
carve text(42)          // "42"
carve type([1, 2])      // "rack"
```

## Racks

| Function | Alias | Returns |
|---|---|---|
| `length(x)` | — | items in a rack/locker, characters in text |
| `push(rack, item)` | `stash` | appends in place, returns the rack |
| `pop(rack)` | — | removes and returns the last item |
| `laps(n)` / `laps(start, stop)` / `laps(start, stop, step)` | `range` | rack of counting numbers |
| `groom(rack)` | `sort` | sorted copy |
| `flip(x)` | `reverse` | reversed copy of a rack or text |
| `contains(x, item)` | — | membership test (see also the `in` operator) |
| `find(x, item)` | — | first position, or `-1` |
| `slice(x, start, end?)` | — | sub-rack or sub-text |
| `join(rack, sep)` | — | rack joined into text |
| `sum(rack)` | — | total of a rack of numbers |
| `min(...)` / `max(...)` | — | smallest / largest |

```slopescript
carve length([1, 2, 3])          // 3
carve laps(3)                    // [0, 1, 2]
carve laps(1, 5)                 // [1, 2, 3, 4]
carve laps(0, 10, 2)             // [0, 2, 4, 6, 8]
carve groom([3, 1, 2])           // [1, 2, 3]
carve flip([1, 2, 3])            // [3, 2, 1]
carve find(["a", "b"], "b")      // 1
carve slice([1, 2, 3, 4], 1, 3)  // [2, 3]
carve join(["a", "b", "c"], "-") // "a-b-c"
carve sum([1, 2, 3])             // 6
carve min(4, 2, 8)               // 2
carve max(4, 2, 8)               // 8
```

## Higher-order

Tricks that take tricks. See [Tricks (Functions)](Tricks-Functions).

| Function | Returns |
|---|---|
| `map(rack, fn)` | new rack of `fn(item)` results |
| `filter(rack, fn)` | items where `fn(item)` is truthy |
| `reduce(rack, fn, start?)` | rack folded to one value with `fn(acc, item)` |
| `each(rack, fn)` | calls `fn(item)` for each item, returns `whiteout` |

```slopescript
pack runs = [2500, 3100, 1800, 2900]
carve map(runs, trick(f) stomp f / 3.28 runout)     // to meters
carve filter(runs, trick(f) stomp f > 2400 runout)  // [2500, 3100, 2900]
carve reduce(runs, trick(a, b) stomp a + b runout)  // 10300
each(runs, trick(f) carve "run:", f runout)
```

## Text

| Function | Alias | Returns |
|---|---|---|
| `upper(t)` | `shout` | UPPERCASE copy |
| `lower(t)` | `whisper` | lowercase copy |
| `trim(t)` | — | copy without surrounding whitespace |
| `split(t, sep)` | — | rack of pieces (`""` splits into characters) |
| `replace(t, old, new)` | — | copy with replacements |
| `startsWith(t, prefix)` | — | `powder` / `ice` |
| `endsWith(t, suffix)` | — | `powder` / `ice` |

```slopescript
carve upper("gnar")               // "GNAR"
carve trim("  powder  ")          // "powder"
carve split("a,b,c", ",")         // ["a", "b", "c"]
carve replace("groomer", "oo", "u")  // "grumer"
carve startsWith("powder", "pow")    // powder
```

## Lockers

| Function | Returns |
|---|---|
| `keys(l)` | rack of keys |
| `values(l)` | rack of values |
| `has(l, key)` | `powder` / `ice` |
| `drop(l, key)` | removes the key (if present), returns the locker |

```slopescript
pack lift = { name: "Big Red", capacity: 6 }
carve keys(lift)         // ["name", "capacity"]
carve values(lift)       // ["Big Red", 6]
carve has(lift, "name")  // powder
drop(lift, "capacity")
```

## Math

| Function | Alias | Returns |
|---|---|---|
| `abs(n)` | — | absolute value |
| `round(n, digits?)` | — | rounded value |
| `basin(n)` | `floor` | round down (into the basin) |
| `cornice(n)` | `ceil` | round up (onto the cornice) |
| `sqrt(n)` | — | square root |
| `snowflake()` | `random` | random decimal in `[0, 1)` |
| `snowflake(low, high)` | `random` | random whole number `low`..`high`, inclusive |

```slopescript
carve abs(-7)              // 7
carve round(3.14159, 2)    // 3.14
carve basin(3.9)           // 3
carve cornice(3.1)         // 4
carve sqrt(144)            // 12
carve snowflake(1, 100)    // e.g. 57
```

## Files

See [Files & the Radio](Files-and-the-Radio) for details and error behaviour.

| Function | Returns |
|---|---|
| `readFile(path)` | whole file as text |
| `readLines(path)` | rack of lines (no trailing newlines) |
| `writeFile(path, value)` | writes (replacing the file), returns `whiteout` |
| `appendFile(path, value)` | appends, returns `whiteout` |
| `fileExists(path)` | `powder` / `ice` |
| `deleteFile(path)` | `powder` if deleted, `ice` if it wasn't there |

## The radio (HTTP + JSON)

See [Files & the Radio](Files-and-the-Radio) for details, headers, timeouts, and
CORS notes.

| Function | Alias | Returns |
|---|---|---|
| `radioBase(url, headers?)` | `fetch` | GET; body as text |
| `radioJson(url, headers?)` | `fetchJson` | GET; body parsed from JSON |
| `radioPost(url, value, headers?)` | `post` | POST; returns body |
| `parseJson(text)` | — | JSON text → SlopeScript values |
| `toJson(value, pretty?)` | — | SlopeScript value → JSON text |

## Misc

| Function | Returns |
|---|---|
| `clock()` | seconds since the epoch (time programs with it) |

```slopescript
pack start = clock()
// ... work ...
carve "took", round(clock() - start, 3), "seconds"
```

## Alias quick-reference

Every themed name and its plain alias:

| Themed | Plain alias |
|---|---|
| `number` | `tune` |
| `type` | `trailMap` |
| `push` | `stash` |
| `laps` | `range` |
| `groom` | `sort` |
| `flip` | `reverse` |
| `upper` | `shout` |
| `lower` | `whisper` |
| `basin` | `floor` |
| `cornice` | `ceil` |
| `snowflake` | `random` |
| `radioBase` | `fetch` |
| `radioJson` | `fetchJson` |
| `radioPost` | `post` |

> A trick you define can share a builtin's name and will **shadow** it for the
> rest of the program.

---

For the authoritative table, see
[LANGUAGE_SPEC.md](https://github.com/arnavj/SlopeScript/blob/main/LANGUAGE_SPEC.md#14-the-base-lodge-standard-library).
