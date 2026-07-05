# Glossary 🏔️

SlopeScript's syntax is skiing all the way down. Every keyword is a real skiing
term chosen so its meaning maps onto the programming concept. This page is the
decoder ring — skiing term → what it does → the familiar equivalent.

## Keywords

| SlopeScript | Skiing meaning | Programming concept | Familiar name |
|---|---|---|---|
| `summit` | the top of the mountain | program start | — |
| `lodge` | the base lodge | program end | — |
| `pack` | pack your gear | declare a variable | `let` / `var` |
| `carve` | carve a turn into the snow | print output | `print` |
| `chairlift` | ride up, ask a question | read input | `input()` |
| `greenCircle` | easiest trail rating | `if` | `if` |
| `blueSquare` | intermediate rating | `else if` | `elif` / `else if` |
| `blackDiamond` | expert rating | `else` | `else` |
| `gondola` | enclosed lift, goes round | `while` loop | `while` |
| `liftline` | the line for the lift | `for-each` loop | `for … in` |
| `in` | — | membership / iteration | `in` |
| `trick` | a freestyle trick | function | `def` / `function` |
| `nail` | nail the landing | end a function | `}` / `end` |
| `runout` | the flat at the slope's bottom | end of a block | `}` / `end` |
| `stomp` | stomp the landing | return a value | `return` |
| `bail` | bail out of a run | break a loop | `break` |
| `sendIt` | send it — keep going | continue a loop | `continue` |
| `powder` | fresh powder (the good stuff) | boolean true | `true` |
| `ice` | icy (the bad stuff) | boolean false | `false` |
| `whiteout` | can't see anything | null / nothing | `null` / `None` |
| `patrol` | ski patrol watches the run | `try` | `try` |
| `patroller` | the patroller who helps | `catch` | `catch` / `except` |
| `avalanche` | something went very wrong | `throw` | `throw` / `raise` |
| `traverse` | traverse to another trail | import a file | `import` / `require` |

## Data types

| SlopeScript | Concept | Familiar name |
|---|---|---|
| `number` | integers & decimals | number |
| `text` | strings | string |
| `condition` | booleans | boolean |
| `whiteout` | nothing | null |
| `rack` | a ski rack holds your gear | ordered list | array / list |
| `locker` | a locker with labelled cubbies | key→value map | dict / object / map |
| `trick` | a function value | function |

## Themed builtins

The standard library keeps the theme too. Full list on the
[Standard Library](Standard-Library) page.

| SlopeScript | Does | Plain alias |
|---|---|---|
| `laps(n)` | counting numbers (do laps) | `range` |
| `groom` | groom the run smooth | `sort` |
| `flip` | flip it around | `reverse` |
| `push` | stash gear on the rack | `stash` / push |
| `basin` | down into the basin | `floor` |
| `cornice` | up onto the cornice | `ceil` |
| `snowflake` | every one is random | `random` |
| `number` | tune your skis | `tune` |
| `type` | read the trail map | `trailMap` |
| `upper` / `lower` | shout / whisper | `shout` / `whisper` |
| `radioBase` | call on the radio (GET) | `fetch` |
| `radioJson` | radio, parsed | `fetchJson` |
| `radioPost` | radio out (POST) | `post` |

## Error & REPL flavour

| Phrase | Where you'll see it | Meaning |
|---|---|---|
| *Yard sale!* | error message | you crashed and gear went everywhere (e.g. divide by zero) |
| *Ski Patrol Report* | uncaught error | the crash report, with file and line |
| *Avalanche risk!* | error message | recursion too deep (>200 calls) |
| *Lifts closed* / `LiftsClosed` | end of input | input ran out; the program stops |
| *fresh corduroy, no waiting* | REPL banner | freshly groomed snow — a clean session |
| `apres` | REPL command | après-ski — leave the REPL |
| *hockey stop* | REPL (Ctrl-C) | stop hard, clear the current input |
| *first chair* | REPL goodbye | the first lift of the morning |

---

*Now you speak fluent chairlift.* → back to [Home](Home).
