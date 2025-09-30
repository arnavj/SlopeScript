# SlopeScript Programming Language 🎿

## Overview
SlopeScript is a programming language where code flows downhill like a skier on a mountain. Programs are structured as ski runs, with control flow mimicking the experience of navigating slopes.

## Core Concepts

### 1. Program Structure
Every program starts at the **summit** and ends at the **lodge**:

```
summit
  // Your code here
lodge
```

### 2. Variables (Gear)
Variables are called "gear" - you pack them before your run:

```
pack speed = 0
pack style = "parallel"
pack elevation = 3500
```

### 3. Output (Carve)
Print output by "carving" it into the snow:

```
carve "Hello from the slopes!"
carve speed
```

### 4. Input (Chairlift)
Get user input via the chairlift:

```
pack name = chairlift("What's your name, skier?")
```

### 5. Conditionals (Trails)
Choose your path like selecting a trail:

```
greenCircle (speed < 20)
  carve "Taking it easy on the bunny slope"
blueSquare (speed < 40)
  carve "Cruising on an intermediate run"
blackDiamond
  carve "Shredding expert terrain!"
```

### 6. Loops

**Gondola** (while loop - keeps going up and down):
```
gondola (laps < 5)
  carve "Lap number:"
  carve laps
  pack laps = laps + 1
```

**LiftLine** (for loop - wait your turn):
```
liftline skier in ["Alice", "Bob", "Charlie"]
  carve skier
  carve "is ready to drop!"
```

### 7. Functions (Tricks)
Define reusable code as tricks:

```
trick greet(name)
  carve "Shred on,"
  carve name
  carve "! 🎿"
nail  // end of trick
```

Call a trick:
```
greet("Tony")
```

### 8. Comments
```
// Single line - like a ski pole mark in the snow
/* Multi-line comment
   Like tracks across
   fresh powder */
```

### 9. Operators

**Arithmetic:**
- `+` (climb)
- `-` (descend)
- `*` (multiply speed)
- `/` (divide slope)

**Comparison:**
- `>` (steeper than)
- `<` (gentler than)
- `==` (same run)
- `!=` (different run)

**Logical:**
- `&&` (parallel - both conditions)
- `||` (moguls - either condition)
- `!` (wipeout - not)

### 10. Special Keywords
- `bail` - break out of loop (fall and stop)
- `sendIt` - continue to next iteration
- `powder` - true value
- `ice` - false value
- `avalanche` - throw error
- `patroller` - catch error

## Sample Program

```
summit

pack verticalFeet = 0
pack runs = 0
pack maxRuns = 10

carve "🎿 Welcome to SlopeScript Mountain! 🏔️"

gondola (runs < maxRuns)
  pack runs = runs + 1
  pack thisRun = 2500
  pack verticalFeet = verticalFeet + thisRun
  
  carve "Run #"
  carve runs
  carve "- Dropped"
  carve thisRun
  carve "feet!"
  
  greenCircle (runs < 3)
    carve "Warming up..."
  blueSquare (runs < 7)
    carve "Getting into the groove!"
  blackDiamond
    carve "Sending it! 💨"
  
gondola

carve "Session complete!"
carve "Total vertical:"
carve verticalFeet
carve "feet! Time for hot chocolate! ☕"

lodge
```

## Advanced Features

### Error Handling (Ski Patrol)
```
patrol
  // risky code here
avalanche "Something went wrong on the slopes!"
patroller (whoops)
  carve "Ski patrol to the rescue:"
  carve whoops
```

### Arrays (Ski Racks)
```
pack skiRack = ["moguls", "powder", "groomers"]
carve skiRack[0]  // moguls
```

### Data Types
- `number` - distances, speeds, angles
- `text` - trail names, messages
- `powder/ice` - booleans
- `rack` - arrays
- `locker` - objects/dictionaries

## Philosophy
SlopeScript embraces the flow and rhythm of skiing. Code should read like planning and executing ski runs - starting at the top, making decisions on the fly, and finishing with style at the bottom!

---

*"There are no friends on a powder day... but there are variables!"* 🎿❄️