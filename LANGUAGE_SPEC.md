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
- [13. Modules (traverse)](#13-modules-traverse)
- [14. The Base Lodge (standard library)](#14-the-base-lodge-standard-library)
- [15. The REPL](#15-the-repl)
- [16. Grammar](#16-grammar)
- [17. Style guide](#17-style-guide)

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
  powder ice whiteout patrol patroller avalanche traverse`
- **Numbers**: `42`, `3.14`, `-7` (unary minus). Integers and decimals.
- **Text**: double- or single-quoted: `"powder day"`, `'corduroy'`.
  Escapes: `\n` `\t` `\r` `\\` `\"` `\'` `\0` `\{`. Strings cannot span lines.
  Text interpolates `{expression}` — see [§6](#6-output-and-input).
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

**Interpolation.** Any text literal may embed `{expression}`; the expression
is evaluated and formatted in place. Escape a literal brace as `\{`; empty
braces `{}` stay literal.

```slopescript
carve "Run #{n}: {vertical} feet ({round(vertical / 3.28)} m)"
pack label = "avg {total / runs} feet per run"
```

An unclosed `{` in text, or a brace containing an invalid expression, is a
syntax error that points at the interpolation.

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

**Tricks are first-class values.** A trick name (or a Base Lodge builtin
name) evaluates to the trick itself, so tricks can be stored, passed, and
returned. Closures capture the scope where the trick was made. An unnamed
trick is written inline as an expression:

```slopescript
pack square = trick(n) stomp n * n runout
carve map([1, 2, 3], square)                     // [1, 4, 9]
carve filter(runs, trick(f) stomp f > 2400 runout)
pack ops = { toMeters: trick(f) stomp f / 3.28 runout }
carve ops.toMeters(3280)

trick makeCounter()
  pack count = 0
  stomp trick()
    count += 1
    stomp count
  runout
nail
```

Any expression that evaluates to a trick can be called: `rack[0](x)`,
`locker.fn(x)`, `makeCounter()()`. Calling anything that isn't a trick is a
runtime error. The opening `(` of a call must be on the same line as the
expression being called.

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

## 13. Modules (traverse)

Split a program across files with `traverse`:

```slopescript
summit
  traverse "lib/slopemath.slope"   // path relative to this file
  carve gradient(900, 2800)
lodge
```

- The traversed file is a normal SlopeScript program; it runs once, in the
  global scope, so its tricks and packed gear become available to the
  traverser. The `.slope` extension may be omitted.
- Repeat traverses of the same file are no-ops; mutual traverses (a cycle)
  are a runtime error.
- The path may be any expression that evaluates to text. Relative paths
  resolve against the directory of the file doing the traversing.
- Errors inside a traversed file are reported with `(while traversing ...)`
  appended.

## 14. The Base Lodge (standard library)

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

### Higher-order (tricks that take tricks)
| Function | Returns |
|---|---|
| `map(rack, fn)` | new rack of `fn(item)` results |
| `filter(rack, fn)` | items where `fn(item)` is truthy |
| `reduce(rack, fn, start?)` | rack folded to one value with `fn(acc, item)` |
| `each(rack, fn)` | calls `fn(item)` for every item, returns whiteout |

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

### Files (the trail journal)
| Function | Returns |
|---|---|
| `readFile(path)` | whole file as text |
| `readLines(path)` | rack of lines (no trailing newlines) |
| `writeFile(path, value)` | writes (replacing the file), returns whiteout |
| `appendFile(path, value)` | appends, returns whiteout |
| `fileExists(path)` | condition |
| `deleteFile(path)` | powder if deleted, ice if it wasn't there |

Paths resolve against the working directory. Every file failure (missing
file, permissions, ...) is a runtime error a `patroller` can catch.

### The radio (HTTP + JSON)
| Function | Returns |
|---|---|
| `radioBase(url, headers?)` *(fetch)* | GET; response body as text |
| `radioJson(url, headers?)` *(fetchJson)* | GET; body parsed from JSON into racks/lockers |
| `radioPost(url, value, headers?)` *(post)* | POST; lockers/racks are sent as JSON, text as-is; returns body |
| `parseJson(text)` | JSON text → SlopeScript values |
| `toJson(value, pretty?)` | SlopeScript value → JSON text |

Headers are an optional locker (`{ "Authorization": "Bearer ..." }`).
Requests time out after 30 seconds. HTTP error statuses, unreachable
hosts, and bad JSON are runtime errors a `patroller` can catch — always
patrol around the radio. In the browser playground, GET works through the
browser (subject to the target site's CORS policy) and `radioPost` is
unavailable.

### Misc
| Function | Returns |
|---|---|
| `clock()` | seconds since the epoch (time programs with it) |

## 15. The REPL

Run `slope` with no arguments for an interactive session:

- Statements execute immediately; bare expressions echo their value.
- A line that opens a block keeps the prompt open (`···`) until every block
  is closed with `runout`/`nail`.
- `summit`/`lodge` are optional in the REPL.
- State (packs and tricks) persists for the whole session.
- Leave with `apres`, `exit`, or Ctrl-D. Ctrl-C hockey-stops the current
  input.

Piping a file into `slope` runs it as a program (`summit`/`lodge` required).

## 16. Grammar

EBNF, ignoring whitespace and comments:

```ebnf
program     = "summit" { statement } "lodge" ;

statement   = pack | assign | carve | conditional | gondola | liftline
            | trickdef | "stomp" [ expression ] | "bail" | "sendIt"
            | patrol | "avalanche" expression
            | "traverse" expression | expression ;

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
            | "(" expression ")" | rack | locker | anontrick ;
anontrick   = "trick" "(" [ IDENT { "," IDENT } ] ")"
              { statement } ( "nail" | "runout" ) ;
rack        = "[" [ expression { "," expression } ] "]" ;
locker      = "{" [ lockerpair { "," lockerpair } ] "}" ;
lockerpair  = ( IDENT | STRING | NUMBER ) ":" expression ;
```

STRING literals may contain `{expression}` interpolations (§6). A call's
opening `(` must sit on the same line as the callee, and `carve`/`stomp`
only take arguments that start on their own line — so statements never
bleed into each other.

## 17. Style guide

- Indent two spaces per block. The interpreter doesn't care; humans do.
- `camelCase` names: `verticalFeet`, `openTrails`.
- One statement per line.
- Close tricks with `nail`, everything else with `runout`.
- Comment like you'd chat on a chairlift: brief, friendly, and only when
  there's something worth saying.

---

*Code flows downhill. Ski safe.* ⛷️
