# SlopeScript Language Specification 🎿

Version 2.0 — the complete reference for the SlopeScript programming language.

SlopeScript is a dynamically-typed, imperative language with first-class
functions, structured error handling, and a skiing-shaped syntax. Programs
"flow downhill": execution starts at the `summit` and ends at the `lodge`.

- [1. Program structure](#1-program-structure)
- [2. Lexical rules](#2-lexical-rules)
- [3. Types and values](#3-types-and-values)
- [4. Variables](#4-variables)
- [5. Expressions and operators](#5-expressions-and-operators)
- [6. Output and input](#6-output-and-input)
- [7. Conditionals](#7-conditionals-trail-ratings)
- [8. Loops](#8-loops)
- [9. Tricks (functions)](#9-tricks-functions)
- [10. Racks (arrays)](#10-racks-arrays)
- [11. Lockers (dictionaries)](#11-lockers-dictionaries)
- [12. Ski patrol (error handling)](#12-ski-patrol-error-handling)
- [13. The Base Lodge (standard library)](#13-the-base-lodge-standard-library)
- [14. The REPL](#14-the-repl)
- [15. Grammar](#15-grammar)
- [16. Style guide](#16-style-guide)

---

## 1. Program structure

Every program file starts with `summit` and ends with `lodge`:

```slopescript
summit
  // your run goes here
lodge
```

Anything after `lodge` is a syntax error — the run is over.

**Blocks.** Every block construct (`greenCircle` chains, `gondola`,
`liftline`, `trick`, `patrol`) is closed by the keyword `runout` — the flat
section at the bottom of a slope. Tricks may traditionally be closed with
`nail` instead; the two are interchangeable.

Whitespace and indentation are not significant. Indent for humans; the
`runout` keywords are what the interpreter reads. Statements simply follow
one another — no semicolons.

## 2. Lexical rules

- **Identifiers**: letters, digits, and `_`, not starting with a digit.
  Convention is `camelCase`.
- **Keywords** (reserved): `summit lodge pack carve greenCircle blueSquare
  blackDiamond gondola liftline in trick nail runout stomp bail sendIt
  powder ice whiteout patrol patroller avalanche`
- **Numbers**: `42`, `3.14`, `-7` (unary minus). Integers and decimals.
- **Text**: double- or single-quoted: `"powder day"`, `'corduroy'`.
  Escapes: `\n` `\t` `\r` `\\` `\"` `\'` `\0`. Strings cannot span lines.
- **Comments**: `// to end of line` and `/* block comments */`.

## 3. Types and values

| Type name | Values | Literal |
|---|---|---|
| `number` | integers & decimals | `42`, `3.14` |
| `text` | strings | `"gnar"` |
| `condition` | booleans | `powder` (true), `ice` (false) |
| `whiteout` | null / nothing | `whiteout` |
| `rack` | ordered list | `[1, 2, 3]` |
| `locker` | key → value map | `{ name: "Big Red", capacity: 6 }` |
| `trick` | function | defined with `trick ... nail` |

`type(x)` returns the type name as text.

**Truthiness.** `ice`, `whiteout`, `0`, empty text `""`, empty rack `[]`,
and empty locker `{}` are falsy. Everything else is truthy.

**Printing.** When carved, `powder`/`ice`/`whiteout` print as those words;
whole-valued decimals print without the trailing `.0` (so `10 / 2` carves
as `5`); racks and lockers print in literal form with text quoted.

## 4. Variables

Declare (or re-declare) with `pack`; reassign with `=`:

```slopescript
pack speed = 0        // declare
speed = 10            // reassign (must already be packed)
speed += 5            // compound: += -= *= /=
```

Reassigning a name that was never packed is an error — the message tells
you to pack it first. `pack` inside a trick creates a *local* variable;
plain `=` walks outward and updates the nearest packed variable with that
name (so tricks can update globals).

Rack slots and locker entries are assignable too:

```slopescript
trails[0] = "Corbet's"
lift.name = "Big Red"
lift["capacity"] = 6
```

## 5. Expressions and operators

Precedence from loosest to tightest:

| Level | Operators |
|---|---|
| logical or | `\|\|` |
| logical and | `&&` |
| equality | `==` `!=` |
| comparison | `<` `>` `<=` `>=` `in` |
| additive | `+` `-` |
| multiplicative | `*` `/` `%` |
| unary | `!` `-` |
| power | `**` (right-associative) |
| postfix | `x[i]`, `x.key`, `f(args)` |

Notes:

- `+` adds numbers, concatenates racks, and joins text: if either side is
  text, the other side is converted, so `"Run " + 3` is `"Run 3"`.
- `/` on two whole numbers gives a whole number when it divides evenly,
  a decimal otherwise. Dividing by zero is a *yard sale* (error).
- `&&` and `||` short-circuit and return the deciding operand.
- `in` tests membership: item in rack, text in text, key in locker.
- Comparisons (`<` etc.) work between two numbers or two texts; comparing
  across types is an error rather than a silent surprise.
- `==` never coerces: `1 == "1"` is `ice`.

## 6. Output and input

**`carve`** prints its arguments separated by spaces, then a newline.
With no arguments it prints a blank line. Arguments must start on the same
line as the `carve` keyword.

```slopescript
carve "Run #" + n, "-", vertical, "feet"
carve                      // blank line
```

**`chairlift(prompt)`** reads one line of input as text. Convert with
`number(...)` when you need one. When input runs out (end of file), the
lifts close: the program stops with a `LiftsClosed` report that `patroller`
deliberately does not catch, so retry loops can't spin forever.

## 7. Conditionals (trail ratings)

`greenCircle` (if) → any number of `blueSquare` (else if) → optional
`blackDiamond` (else), closed by `runout`:

```slopescript
greenCircle (snowfall > 6)
  carve "Powder day!"
blueSquare (snowfall > 2)
  carve "Fresh enough"
blackDiamond
  carve "Groomer day"
runout
```

The first branch whose condition is truthy runs; the rest are skipped.
A `blueSquare` or `blackDiamond` without a `greenCircle` is a syntax error.
Chains nest freely — each chain has its own `runout`.

## 8. Loops

**`gondola`** — while loop:

```slopescript
gondola (laps < 5)
  laps += 1
runout
```

**`liftline`** — for-each loop over a rack (items), text (characters), or
locker (keys). Use `laps(n)` from the standard library to count:

```slopescript
liftline skier in ["Ann", "Bo"]
  carve skier
runout

liftline i in laps(10)      // 0 through 9
  carve i
runout
```

**`bail`** exits the innermost loop. **`sendIt`** skips to its next
iteration. Using either outside a loop is an error.

## 9. Tricks (functions)

```slopescript
trick average(rackOfNumbers)
  greenCircle (length(rackOfNumbers) == 0)
    stomp 0
  runout
  stomp sum(rackOfNumbers) / length(rackOfNumbers)
nail
```

- Define with `trick name(param1, param2, ...)`; close with `nail` (or
  `runout`).
- `stomp expr` returns a value ("stomp the landing"). Bare `stomp` — and
  falling off the end of the trick — returns `whiteout`.
- Calling with the wrong number of arguments is an error that names the
  expected parameters.
- Tricks may call themselves (recursion) and each other. Recursion deeper
  than 200 calls triggers an avalanche-risk error.
- Parameters and `pack`ed names are local to the call. Plain `=` reaches
  outward, so tricks can update variables from enclosing scopes.
- A trick defined with the same name as a builtin shadows the builtin.

## 10. Racks (arrays)

```slopescript
pack trails = ["Corbet's", "KT-22"]
carve trails[0]              // first item
carve trails[-1]             // last item (negative indexing works)
trails[1] = "Chute 75"
push(trails, "Rambo")        // grow
carve length(trails)
carve [1, 2] + [3]           // concatenation → [1, 2, 3]
pack grid = [[1, 2], [3, 4]]
carve grid[1][0]             // nesting → 3
```

Indexing off the edge of a rack is a caught-by-patrol-able error, not a
silent `whiteout`.

## 11. Lockers (dictionaries)

```slopescript
pack lift = { name: "Big Red", capacity: 6, "top speed": 5 }
carve lift.name              // dot access for simple keys
carve lift["top speed"]      // bracket access for anything
lift.express = powder        // add / update either way
drop(lift, "capacity")       // remove a key
liftline key in lift         // iterate keys in insertion order
  carve key, "=", lift[key]
runout
```

Literal keys may be bare names, text, or numbers. Reading a key that isn't
there is an error that lists the keys the locker *does* hold.

## 12. Ski patrol (error handling)

```slopescript
patrol
  pack n = number(chairlift("How many runs?"))
  greenCircle (n < 0)
    avalanche { code: 400, reason: "negative runs" }
  runout
  carve 100 / n
patroller (whoops)
  carve "⛑️ caught:", whoops
runout
```

- `patrol ... patroller (name) ... runout` is try/catch. The handler binds
  the caught value to `name`.
- `avalanche value` throws any value — text, a number, or a locker full of
  detail. A patroller catches exactly the value thrown.
- Runtime wipeouts (division by zero, missing keys, bad indexing, type
  errors, tuning failures) are caught too; `name` gets the message text.
- Patrols nest; an avalanche in a handler rides up to the next patrol out.
- Uncaught errors stop the program with a report giving file and line.
- Syntax errors and the end of input (`LiftsClosed`) are not catchable.

## 13. The Base Lodge (standard library)

All functions are global — no imports. Themed names are canonical; the
plain aliases in parentheses work identically.

### Input & output
| Function | Returns |
|---|---|
| `chairlift(prompt?)` | one line of input, as text |

### Conversion & inspection
| Function | Returns |
|---|---|
| `number(x)` *(tune)* | `x` as a number; error if it won't tune |
| `text(x)` | `x` as text |
| `type(x)` *(trailMap)* | type name as text |

### Racks
| Function | Returns |
|---|---|
| `length(x)` | items in a rack/locker, characters in text |
| `push(rack, item)` *(stash)* | appends in place, returns the rack |
| `pop(rack)` | removes and returns the last item |
| `laps(n)` / `laps(start, stop)` / `laps(start, stop, step)` *(range)* | rack of counting numbers |
| `groom(rack)` *(sort)* | sorted copy |
| `flip(x)` *(reverse)* | reversed copy of a rack or text |
| `contains(x, item)` | membership test (also see the `in` operator) |
| `find(x, item)` | first position, or `-1` |
| `slice(x, start, end?)` | sub-rack or sub-text |
| `join(rack, sep)` | rack joined into text |
| `sum(rack)` / `min(...)` / `max(...)` | totals and extremes |

### Text
| Function | Returns |
|---|---|
| `upper(t)` *(shout)* / `lower(t)` *(whisper)* | case-changed copy |
| `trim(t)` | copy without surrounding whitespace |
| `split(t, sep)` | rack of pieces (`""` splits into characters) |
| `replace(t, old, new)` | copy with replacements |
| `startsWith(t, prefix)` / `endsWith(t, suffix)` | condition |

### Lockers
| Function | Returns |
|---|---|
| `keys(l)` / `values(l)` | rack of keys / values |
| `has(l, key)` | condition |
| `drop(l, key)` | removes the key (if present), returns the locker |

### Math
| Function | Returns |
|---|---|
| `abs(n)` | absolute value |
| `round(n, digits?)` | rounded value |
| `basin(n)` *(floor)* | round down (into the basin) |
| `cornice(n)` *(ceil)* | round up (onto the cornice) |
| `sqrt(n)` | square root |
| `snowflake()` *(random)* | random decimal in [0, 1) |
| `snowflake(low, high)` | random whole number from low to high, inclusive |

### Misc
| Function | Returns |
|---|---|
| `clock()` | seconds since the epoch (time programs with it) |

## 14. The REPL

Run `slope` with no arguments for an interactive session:

- Statements execute immediately; bare expressions echo their value.
- A line that opens a block keeps the prompt open (`···`) until every block
  is closed with `runout`/`nail`.
- `summit`/`lodge` are optional in the REPL.
- State (packs and tricks) persists for the whole session.
- Leave with `apres`, `exit`, or Ctrl-D. Ctrl-C hockey-stops the current
  input.

Piping a file into `slope` runs it as a program (`summit`/`lodge` required).

## 15. Grammar

EBNF, ignoring whitespace and comments:

```ebnf
program     = "summit" { statement } "lodge" ;

statement   = pack | assign | carve | conditional | gondola | liftline
            | trickdef | "stomp" [ expression ] | "bail" | "sendIt"
            | patrol | "avalanche" expression | expression ;

pack        = "pack" IDENT "=" expression ;
assign      = target ( "=" | "+=" | "-=" | "*=" | "/=" ) expression ;
target      = IDENT { "[" expression "]" | "." IDENT } ;
carve       = "carve" [ expression { "," expression } ] ;

conditional = "greenCircle" "(" expression ")" { statement }
              { "blueSquare" "(" expression ")" { statement } }
              [ "blackDiamond" { statement } ]
              "runout" ;

gondola     = "gondola" "(" expression ")" { statement } "runout" ;
liftline    = "liftline" IDENT "in" expression { statement } "runout" ;
trickdef    = "trick" IDENT "(" [ IDENT { "," IDENT } ] ")"
              { statement } ( "nail" | "runout" ) ;
patrol      = "patrol" { statement }
              "patroller" "(" IDENT ")" { statement } "runout" ;

expression  = orexpr ;
orexpr      = andexpr { "||" andexpr } ;
andexpr     = equality { "&&" equality } ;
equality    = comparison { ( "==" | "!=" ) comparison } ;
comparison  = additive { ( "<" | ">" | "<=" | ">=" | "in" ) additive } ;
additive    = multiplicative { ( "+" | "-" ) multiplicative } ;
multiplicative = unary { ( "*" | "/" | "%" ) unary } ;
unary       = ( "!" | "-" ) unary | power ;
power       = postfix [ "**" unary ] ;
postfix     = primary { "[" expression "]" | "." IDENT
                      | "(" [ expression { "," expression } ] ")" } ;
primary     = NUMBER | STRING | "powder" | "ice" | "whiteout" | IDENT
            | "(" expression ")" | rack | locker ;
rack        = "[" [ expression { "," expression } ] "]" ;
locker      = "{" [ lockerpair { "," lockerpair } ] "}" ;
lockerpair  = ( IDENT | STRING | NUMBER ) ":" expression ;
```

Calls apply only to plain names (`f(x)`, not `rack[0](x)`).
`carve` and `stomp` only take arguments that start on their own line, so
statements never bleed into each other.

## 16. Style guide

- Indent two spaces per block. The interpreter doesn't care; humans do.
- `camelCase` names: `verticalFeet`, `openTrails`.
- One statement per line.
- Close tricks with `nail`, everything else with `runout`.
- Comment like you'd chat on a chairlift: brief, friendly, and only when
  there's something worth saying.

---

*Code flows downhill. Ski safe.* ⛷️
