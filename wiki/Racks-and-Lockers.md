# Racks & Lockers 🎿🔐

SlopeScript's two collection types: **racks** (ordered lists / arrays) and
**lockers** (key → value maps / dictionaries).

## Racks (arrays)

A rack is an ordered, mutable list written with square brackets:

```slopescript
pack trails = ["Corbet's", "KT-22", "Delirium Dive"]
```

### Indexing

Zero-based, with **negative indexing** for counting from the end:

```slopescript
carve trails[0]      // "Corbet's"  (first)
carve trails[-1]     // "Delirium Dive"  (last)
carve trails[1]      // "KT-22"
```

Indexing **off the edge** of a rack is a catchable runtime error (not a silent
`whiteout`), so out-of-bounds bugs surface immediately:

```
⛑️  Rack index 9 out of range (rack has 3 items)
```

### Assigning into a slot

```slopescript
trails[1] = "Chute 75"
```

### Growing and shrinking

```slopescript
push(trails, "Rambo")     // append (alias: stash), returns the rack
pack last = pop(trails)   // remove & return the last item
carve length(trails)      // how many items
```

### Concatenation

`+` joins two racks into a new one:

```slopescript
carve [1, 2] + [3]        // [1, 2, 3]
```

### Nesting

Racks hold anything, including other racks and lockers:

```slopescript
pack grid = [[1, 2], [3, 4]]
carve grid[1][0]          // 3

pack runs = [
  { name: "Corbet's Couloir", vertical: 2500 },
  { name: "KT-22",            vertical: 3000 }
]
carve runs[0].name        // "Corbet's Couloir"
```

### Iterating

```slopescript
liftline trail in trails
  carve trail
runout
```

### Rack builtins

`length`, `push`, `pop`, `laps` (range), `groom` (sort), `flip` (reverse),
`contains`, `find`, `slice`, `join`, `sum`, `min`, `max`, plus the higher-order
`map`, `filter`, `reduce`, `each`. Full signatures on the
[Standard Library](Standard-Library) page.

```slopescript
pack nums = [3, 1, 4, 1, 5]
carve groom(nums)              // [1, 1, 3, 4, 5]
carve flip(nums)               // [5, 1, 4, 1, 3]
carve sum(nums)                // 14
carve join(["a", "b"], "-")    // "a-b"
carve find(nums, 4)            // 2
carve slice(nums, 1, 3)        // [1, 4]
```

## Lockers (dictionaries)

A locker maps keys to values and **keeps insertion order**. Write one with curly
braces:

```slopescript
pack lift = { name: "Big Red", capacity: 6, "top speed": 5 }
```

Keys in a literal may be **bare names**, **text**, or **numbers**:

```slopescript
pack menu = { "hot chocolate": 5, coffee: 4, 42: "answer" }
```

### Access

Two ways in:

```slopescript
carve lift.name              // dot access — for simple identifier keys
carve lift["capacity"]       // bracket access — for any key
carve lift["top speed"]      // brackets needed (key has a space)
```

Reading a key that **isn't there** is an error that lists the keys the locker
*does* hold — so typos are obvious:

```
⛑️  Locker has no key 'naem' (keys: name, capacity, top speed)
```

### Adding, updating, removing

```slopescript
lift.express = powder        // add or update (dot)
lift["capacity"] = 8         // add or update (bracket)
drop(lift, "capacity")       // remove a key (alias for the operation)
```

### Iterating

`liftline` over a locker yields its **keys**, in insertion order:

```slopescript
liftline key in lift
  carve key, "=", lift[key]
runout
```

### Locker builtins

| Builtin | Returns |
|---|---|
| `keys(l)` | rack of keys |
| `values(l)` | rack of values |
| `has(l, key)` | `powder` / `ice` |
| `drop(l, key)` | removes the key (if present), returns the locker |

```slopescript
carve keys(lift)             // ["name", "top speed", "express"]
carve values(lift)
carve has(lift, "name")      // powder
```

## Lockers as lookup tables

A common pattern — use a locker to map inputs to outputs:

```slopescript
pack trailsByLevel = {
  beginner:     ["Bunny Hill", "Easy Street"],
  intermediate: ["Blue Bird", "Cruiser"],
  expert:       ["Corbet's Couloir", "Death Chute"]
}

pack level = lower(trim(chairlift("Your level?")))
greenCircle (has(trailsByLevel, level))
  liftline trail in trailsByLevel[level]
    carve "  ✓", trail
  runout
blackDiamond
  carve "Invalid skill level!"
runout
```

## How they print

Racks and lockers print in literal form with **text quoted**, so nesting and
types stay readable:

```slopescript
carve ["a", "b"]                     // ["a", "b"]
carve { name: "Big Red", capacity: 6 }  // { name: "Big Red", capacity: 6 }
```

---

Next: [Ski Patrol (Error Handling)](Error-Handling).
