# Files & the Radio 📻📓

SlopeScript can read and write files (the **trail journal**) and talk to the
internet over HTTP (the **radio**). Both live in the Base Lodge and both report
failures as catchable ski-patrol errors — always `patrol` around I/O.

## Files — the trail journal

| Function | Returns |
|---|---|
| `readFile(path)` | the whole file as text |
| `readLines(path)` | a rack of lines (no trailing newlines) |
| `writeFile(path, value)` | writes (replacing the file), returns `whiteout` |
| `appendFile(path, value)` | appends, returns `whiteout` |
| `fileExists(path)` | `powder` / `ice` |
| `deleteFile(path)` | `powder` if deleted, `ice` if it wasn't there |

Paths resolve against the **working directory**.

```slopescript
summit
  writeFile("journal.txt", "TRAIL JOURNAL\n")
  appendFile("journal.txt", "KT-22: 3000 feet\n")
  appendFile("journal.txt", "Corbet's: 2500 feet\n")

  carve "--- the journal ---"
  liftline line in readLines("journal.txt")
    carve line
  runout

  greenCircle (fileExists("journal.txt"))
    deleteFile("journal.txt")
    carve "cleaned up"
  runout
lodge
```

Every file failure — missing file, permission denied, and so on — is a runtime
error a `patroller` can catch:

```slopescript
patrol
  pack text = readFile("does-not-exist.txt")
patroller (e)
  carve "Couldn't read it:", e
runout
```

## The radio — HTTP + JSON

The **radio** makes HTTP requests. Mountains have dead zones, so always wrap the
radio in `patrol`.

| Function | Alias | Returns |
|---|---|---|
| `radioBase(url, headers?)` | `fetch` | GET; response body as **text** |
| `radioJson(url, headers?)` | `fetchJson` | GET; body parsed from JSON into racks/lockers |
| `radioPost(url, value, headers?)` | `post` | POST; lockers/racks sent as JSON, text as-is; returns body |
| `parseJson(text)` | — | JSON text → SlopeScript values |
| `toJson(value, pretty?)` | — | SlopeScript value → JSON text |

### GET and parse JSON

```slopescript
summit
  patrol
    pack repo = radioJson("https://api.github.com/repos/python/cpython")
    carve "{repo.full_name} has {repo.stargazers_count} stars"
  patroller (e)
    carve "No signal:", e
  runout
lodge
```

`radioJson` returns ordinary racks and lockers, so you navigate the response
with `.key` and `[i]` exactly like any other data.

### POST

`radioPost` sends lockers and racks as JSON automatically; text is sent as-is:

```slopescript
patrol
  radioPost("https://example.com/report", { trail: "KT-22", open: powder })
patroller (e)
  carve "Post failed:", e
runout
```

### Headers

The optional last argument is a locker of headers:

```slopescript
pack data = radioJson("https://api.example.com/me", {
  "Authorization": "Bearer TOKEN"
})
```

### JSON on its own

`parseJson` and `toJson` convert without any network — handy for config and
files. JSON maps 1:1 onto SlopeScript: objects ↔ lockers, arrays ↔ racks,
`true`/`false`/`null` ↔ `powder`/`ice`/`whiteout`.

```slopescript
pack data = parseJson('{ "trail": "KT-22", "open": true, "runs": [1, 2, 3] }')
carve data.trail, data.open, data.runs[0]

carve toJson({ trail: "KT-22", open: powder })          // compact
carve toJson({ trail: "KT-22", open: powder }, powder)  // pretty-printed
```

### The fine print

- Requests **time out after 30 seconds**.
- **HTTP error statuses, unreachable hosts, and non-JSON replies** are all
  runtime errors a `patroller` can catch.
- In the **[browser playground](Playground)**, `radioBase` / `radioJson` (GET)
  work through the browser's network stack — subject to the target site's
  **CORS** policy — while `radioPost` reports that it needs the CLI.

---

Next: browse the whole toolbox on the [Standard Library](Standard-Library) page.
