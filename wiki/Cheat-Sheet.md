# Cheat Sheet 🗺️

The whole language on one page. Themed keyword → what it means.

## Structure & flow

| SlopeScript | Means | SlopeScript | Means |
|---|---|---|---|
| `summit` / `lodge` | program start / end | `trick` / `nail` | define function |
| `pack x = 1` | declare variable | `stomp v` | return |
| `carve a, b` | print | `patrol` / `patroller` | try / catch |
| `chairlift(p)` | input | `avalanche v` | throw |
| `greenCircle` | if | `bail` | break |
| `blueSquare` | else if | `sendIt` | continue |
| `blackDiamond` | else | `powder` / `ice` | true / false |
| `gondola` | while | `whiteout` | null |
| `liftline x in r` | for-each | `runout` | end of block |
| `traverse "f"` | import a file | `"x is {expr}"` | interpolation |

## Skeleton of every construct

```slopescript
summit

  pack x = 10                       // variable
  x += 5                            // compound assign (+= -= *= /=)

  greenCircle (x > 20)              // if / else-if / else
    carve "big"
  blueSquare (x > 5)
    carve "medium"
  blackDiamond
    carve "small"
  runout

  gondola (x > 0)                   // while
    x -= 1
  runout

  liftline i in laps(3)             // for-each (0, 1, 2)
    carve i
  runout

  trick double(n)                   // function
    stomp n * 2
  nail

  patrol                            // try / catch
    avalanche "oops"                // throw
  patroller (e)
    carve "caught:", e
  runout

lodge
```

## Values

```slopescript
pack n = 42                  // number
pack t = "gnar"              // text (also 'single quotes')
pack b = powder              // condition: powder / ice
pack z = whiteout            // null
pack r = [1, 2, 3]           // rack (array)
pack l = { a: 1, b: 2 }      // locker (dict)
pack f = trick(x) stomp x*x runout   // trick (function)
```

**Falsy:** `ice`, `whiteout`, `0`, `""`, `[]`, `{}`. Everything else is truthy.

## Operators (loosest → tightest)

```
||   &&   == !=   < > <= >= in   + -   * / %   ! -(unary)   **   x[i] x.k f()
```

- `+` adds numbers, joins text, concatenates racks.
- `==` never coerces; comparisons need same types.
- `&&` / `||` short-circuit and return the deciding operand.
- `in`: item in rack, substring in text, key in locker.

## Racks & lockers

```slopescript
pack a = [10, 20, 30]
a[0]          // 10        a[-1]  // 30 (negative index)
a[1] = 99     // assign     push(a, 40)   pop(a)   length(a)
[1,2] + [3]   // [1, 2, 3]

pack m = { name: "Big Red", capacity: 6 }
m.name        // dot        m["capacity"] // bracket
m.express = powder          // add/update   drop(m, "name")
keys(m)  values(m)  has(m, "name")
```

## Interpolation & printing

```slopescript
carve "Run {n}: {feet} ft ({round(feet/3.28)} m)"
carve "literal brace: \{ not interpolated }"
```

## Most-used builtins

```
length push pop laps(range) groom(sort) flip(reverse) contains find slice join sum min max
map filter reduce each
upper(shout) lower(whisper) trim split replace startsWith endsWith
keys values has drop
number(tune) text type(trailMap)
abs round basin(floor) cornice(ceil) sqrt snowflake(random)
readFile readLines writeFile appendFile fileExists deleteFile
radioBase(fetch) radioJson(fetchJson) radioPost(post) parseJson toJson
clock
```

---

Want the full detail? → [Standard Library](Standard-Library) ·
[Grammar](Grammar) · [Glossary](Glossary)
