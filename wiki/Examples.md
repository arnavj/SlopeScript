# Examples 🎯

Every program in the repo's [`examples/`](https://github.com/arnavj/SlopeScript/tree/main/examples)
directory runs out of the box:

```bash
slope examples/hello.slope
# or, without installing:
python3 slopescript.py examples/hello.slope
```

They're ordered here roughly from simplest to richest — a natural reading path.

| Program | Shows off |
|---|---|
| [`hello.slope`](https://github.com/arnavj/SlopeScript/blob/main/examples/hello.slope) | the classic first run |
| [`counter.slope`](https://github.com/arnavj/SlopeScript/blob/main/examples/counter.slope) | `gondola` (while) loops |
| [`ski_day.slope`](https://github.com/arnavj/SlopeScript/blob/main/examples/ski_day.slope) | loops + trail ratings together |
| [`tricks.slope`](https://github.com/arnavj/SlopeScript/blob/main/examples/tricks.slope) | functions, returns, recursion |
| [`higher_order.slope`](https://github.com/arnavj/SlopeScript/blob/main/examples/higher_order.slope) | map/filter/reduce, closures, anonymous tricks |
| [`mountain_tour.slope`](https://github.com/arnavj/SlopeScript/blob/main/examples/mountain_tour.slope) | modules with `traverse` |
| [`trail_journal.slope`](https://github.com/arnavj/SlopeScript/blob/main/examples/trail_journal.slope) | file I/O |
| [`radio_check.slope`](https://github.com/arnavj/SlopeScript/blob/main/examples/radio_check.slope) | HTTP + JSON against a real API |
| [`lodge_menu.slope`](https://github.com/arnavj/SlopeScript/blob/main/examples/lodge_menu.slope) | lockers (dictionaries) |
| [`ski_patrol.slope`](https://github.com/arnavj/SlopeScript/blob/main/examples/ski_patrol.slope) | error handling |
| [`vertical_tracker.slope`](https://github.com/arnavj/SlopeScript/blob/main/examples/vertical_tracker.slope) | racks of lockers |
| [`guess_number.slope`](https://github.com/arnavj/SlopeScript/blob/main/examples/guess_number.slope) | input, random numbers, patrol |
| [`trail_selector.slope`](https://github.com/arnavj/SlopeScript/blob/main/examples/trail_selector.slope) | lockers as lookup tables |
| [`speed_calculator.slope`](https://github.com/arnavj/SlopeScript/blob/main/examples/speed_calculator.slope) | math builtins |
| [`conditions_check.slope`](https://github.com/arnavj/SlopeScript/blob/main/examples/conditions_check.slope) | logical operators |

## Hello, slopes

Your first run. `summit … lodge` and `carve`.

```slopescript
// hello.slope — your first run
summit
  carve "🎿 Hello from the slopes!"
  carve "Welcome to SlopeScript!"
lodge
```

## Counting with a gondola

A `gondola` (while) loop with compound assignment.

```slopescript
summit
  pack count = 1
  gondola (count <= 5)
    carve "Count:", count
    count += 1
  runout
  carve "Done counting!"
lodge
```

→ concepts: [Control Flow](Control-Flow)

## Tricks & recursion

Defining functions, early `stomp`, and recursion (Fibonacci).

```slopescript
summit
  trick verticalPerRun(total, runs)
    greenCircle (runs == 0)
      stomp 0
    runout
    stomp round(total / runs)
  nail

  trick fibonacci(n)
    greenCircle (n < 2)
      stomp n
    runout
    stomp fibonacci(n - 1) + fibonacci(n - 2)
  nail

  carve "Average vertical per run:", verticalPerRun(24000, 9), "feet"
  liftline i in laps(10)
    carve "  fib({i}) = {fibonacci(i)}"
  runout
lodge
```

→ concepts: [Tricks (Functions)](Tricks-Functions)

## Tricks are values (higher-order)

`filter` / `map` / `reduce`, tricks stored in lockers, and a closure-based
counter.

```slopescript
summit
  pack runs = [2500, 3100, 1800, 2900, 2200]

  pack bigRuns = filter(runs, trick(feet) stomp feet > 2400 runout)
  pack inMeters = map(bigRuns, trick(feet) stomp round(feet / 3.28) runout)
  pack total = reduce(runs, trick(a, b) stomp a + b runout)

  carve "big runs: {bigRuns} feet"
  carve "in meters: {inMeters}"
  carve "day total: {total} feet"

  trick makeCounter()
    pack count = 0
    stomp trick()
      count += 1
      stomp count
    runout
  nail

  pack lap = makeCounter()
  carve "laps: {lap()}, {lap()}, {lap()}"
lodge
```

→ concepts: [Tricks (Functions)](Tricks-Functions#closures)

## Ski patrol

Catching a runtime wipeout, throwing a locker with `avalanche`, and looping over
attempts.

```slopescript
summit
  patrol
    carve 10 / 0
  patroller (whoops)
    carve "⛑️ Patrol caught a wipeout:", whoops
  runout

  trick openTrail(name, snowDepth)
    greenCircle (snowDepth < 6)
      avalanche { trail: name, reason: "not enough snow" }
    runout
    carve "✅", name, "is open!"
  nail

  liftline attempt in [["Corbet's", 24], ["Bunny Hill", 2]]
    patrol
      openTrail(attempt[0], attempt[1])
    patroller (report)
      carve "🚧", report.trail, "is closed:", report.reason
    runout
  runout
lodge
```

→ concepts: [Error Handling](Error-Handling)

## Racks of lockers

Modelling structured data — a list of runs, each a locker — and totalling a
field.

```slopescript
summit
  pack runs = [
    { name: "Corbet's Couloir", vertical: 2500 },
    { name: "KT-22",            vertical: 3000 },
    { name: "Delirium Dive",    vertical: 2800 }
  ]
  pack totalVertical = 0

  liftline run in runs
    carve "Dropping into:", run.name, "-", run.vertical, "feet"
    totalVertical += run.vertical
  runout

  carve "TOTAL VERTICAL:", totalVertical, "FEET! 🎿"
lodge
```

→ concepts: [Racks & Lockers](Racks-and-Lockers)

## An interactive game

Random numbers, input, conversion, patrol-guarded parsing, and a retry with
`sendIt`.

```slopescript
summit
  pack secret = snowflake(1, 100)
  pack guess = 0
  pack attempts = 0

  gondola (guess != secret)
    patrol
      guess = number(chairlift("Enter your guess:"))
    patroller (whoops)
      carve "That's not a number — try again!"
      sendIt
    runout

    attempts += 1
    greenCircle (guess < secret)
      carve "Too low! Go steeper! ⛷️"
    blueSquare (guess > secret)
      carve "Too high! Ease up! 🎿"
    blackDiamond
      carve "🎉 You got it in", attempts, "attempts!"
    runout
  runout
lodge
```

→ concepts: [Error Handling](Error-Handling), [Standard Library](Standard-Library)

## Modules

`mountain_tour.slope` pulls in `lib/slopemath.slope`. See the full walkthrough on
the [Modules](Modules) page.

## Talking to an API

`radio_check.slope` makes a live JSON request wrapped in `patrol`. See
[Files & the Radio](Files-and-the-Radio).

---

Open any of these in the **[Playground](Playground)** to run and tweak them
without installing anything.
