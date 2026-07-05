# The Language Tour ⛷️

The whole language in one page. Every snippet below is real, runnable
SlopeScript. For the deep dives, follow the links into the language guide.

Every program is wrapped in `summit … lodge`:

```slopescript
summit
  // your run goes here
lodge
```

## Variables — pack your gear

```slopescript
pack speed = 45
pack name = "Tony"
pack isReady = powder      // powder = true, ice = false
pack nothing = whiteout    // whiteout = null

speed += 5                 // +=, -=, *=, /= all work
carve "Hi", name, "- speed is", speed
```

`pack` declares; plain `=` reassigns something already packed. → [Variables & Operators](Variables-and-Operators)

## Output & input — carve and ride the chairlift

```slopescript
carve "Hello, skier!"                 // print (multiple values, comma-separated)
carve "You did {runs} runs — {runs * 2500} feet!"   // {…} interpolates any expression
pack answer = chairlift("Your name?") // prompt for input
pack age = number(chairlift("Age?"))  // convert text to a number
```

Any text literal can embed `{expression}`; escape a literal brace with `\{`.

## Conditionals — pick your trail

Rated like real trails: `greenCircle` (if), `blueSquare` (else if),
`blackDiamond` (else). Every chain ends at the `runout`.

```slopescript
greenCircle (speed < 20)
  carve "Cruising the bunny slope"
blueSquare (speed < 40)
  carve "Solid blue-square pace"
blackDiamond
  carve "Absolutely sending it 💨"
runout
```

→ [Control Flow](Control-Flow)

## Loops — gondolas and liftlines

```slopescript
// gondola = while loop
pack laps = 0
gondola (laps < 5)
  laps += 1
  carve "Lap", laps
runout

// liftline = for-each loop (racks, text, lockers, or laps(n) for counting)
liftline skier in ["Alice", "Bob", "Charlie"]
  carve skier, "drops in!"
runout

liftline i in laps(3)      // 0, 1, 2
  carve i
runout
```

`bail` breaks out of a loop; `sendIt` continues to the next iteration.

## Tricks — functions

```slopescript
trick verticalPerRun(total, runs)
  greenCircle (runs == 0)
    stomp 0                 // stomp = return (stomp the landing!)
  runout
  stomp round(total / runs)
nail                        // nail finishes the trick

carve verticalPerRun(24000, 9), "feet per run"
```

Tricks are proper, **first-class** functions — recursion, closures, and all.
Pass them around, stash them in lockers, or write them inline:

```slopescript
pack runs = [2500, 3100, 1800, 2900]
carve filter(runs, trick(feet) stomp feet > 2400 runout)   // [2500, 3100, 2900]
carve map(runs, trick(feet) stomp feet / 3.28 runout)      // feet → meters
carve reduce(runs, trick(a, b) stomp a + b runout)         // day total
```

→ [Tricks (Functions)](Tricks-Functions)

## Racks & lockers — arrays and dictionaries

```slopescript
pack trails = ["Corbet's", "KT-22", "Delirium Dive"]
carve trails[0], "of", length(trails)
push(trails, "Rambo")
trails[1] = "Chute 75"

pack lift = { name: "Big Red", capacity: 6, express: powder }
carve lift.name             // dot access
carve lift["capacity"]      // or bracket access
lift.express = ice          // assign either way
carve keys(lift), values(lift)
```

→ [Racks & Lockers](Racks-and-Lockers)

## Ski patrol — error handling

```slopescript
patrol                                  // try
  pack n = number(chairlift("Number?"))
  greenCircle (n < 0)
    avalanche "no negative numbers!"    // throw (any value, even a locker)
  runout
  carve 100 / n
patroller (whoops)                      // catch
  carve "⛑️ Patrol caught it:", whoops
runout
```

Uncaught problems produce friendly reports with the file and line:

```
⛑️  Ski Patrol Report (run.slope, line 7): Yard sale! Division by zero
```

→ [Ski Patrol (Error Handling)](Error-Handling)

## Modules — traverse to another trail

```slopescript
traverse "lib/slopemath.slope"   // load another file's tricks and gear
carve gradient(900, 2800)
```

Each file loads once (repeat traverses are no-ops) and cycles are caught. → [Modules](Modules)

## Files — the trail journal

```slopescript
writeFile("journal.txt", "TRAIL JOURNAL\n")
appendFile("journal.txt", "KT-22: 3000 feet\n")
liftline line in readLines("journal.txt")
  carve line
runout
```

## The radio — call real APIs over HTTP

```slopescript
patrol                                    // mountains have dead zones
  pack repo = radioJson("https://api.github.com/repos/python/cpython")
  carve "{repo.full_name} has {repo.stargazers_count} stars"
patroller (e)
  carve "No signal:", e
runout
```

→ [Files & the Radio](Files-and-the-Radio)

## The Base Lodge — standard library

Around 50 built-in functions, no imports needed: `length`, `push`, `pop`,
`map`, `filter`, `reduce`, `groom` (sort), `upper`, `split`, `keys`, `round`,
`sqrt`, `snowflake` (random), `readFile`, `radioJson`, and many more. → [Standard Library](Standard-Library)

---

Next: install it in **[Getting Started](Getting-Started)**, or keep the whole
language handy on the **[Cheat Sheet](Cheat-Sheet)**.
