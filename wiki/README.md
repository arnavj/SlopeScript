# SlopeScript Wiki (source) 🎿📖

This directory holds the **source Markdown** for the SlopeScript GitHub wiki at
<https://github.com/arnavj/SlopeScript/wiki>.

GitHub wikis are a *separate git repository* (`SlopeScript.wiki.git`), so wiki
pages can't be edited through a normal pull request to the main repo. Keeping the
pages here lets them be reviewed like code, then published to the wiki with the
included script.

## Pages

| File | Wiki page | Special role |
|---|---|---|
| `Home.md` | Home | wiki landing page |
| `_Sidebar.md` | — | navigation sidebar (shown on every page) |
| `_Footer.md` | — | footer (shown on every page) |
| `Getting-Started.md` | Getting Started | |
| `The-Language-Tour.md` | The Language Tour | |
| `Types-and-Values.md` | Types & Values | |
| `Variables-and-Operators.md` | Variables & Operators | |
| `Control-Flow.md` | Control Flow | |
| `Tricks-Functions.md` | Tricks (Functions) | |
| `Racks-and-Lockers.md` | Racks & Lockers | |
| `Error-Handling.md` | Ski Patrol (Error Handling) | |
| `Modules.md` | Modules | |
| `Files-and-the-Radio.md` | Files & the Radio | |
| `Standard-Library.md` | The Base Lodge (Standard Library) | |
| `Grammar.md` | Grammar | |
| `Cheat-Sheet.md` | Cheat Sheet | |
| `Glossary.md` | Glossary | |
| `REPL.md` | The REPL | |
| `Playground.md` | Playground | |
| `Examples.md` | Examples | |
| `Language-Internals.md` | Language Internals | |
| `FAQ.md` | FAQ | |
| `Contributing.md` | Contributing | |

### GitHub wiki naming rules (why the filenames look like this)

- A file named `Foo-Bar.md` becomes the page **"Foo Bar"** — GitHub turns
  hyphens into spaces. Links between pages use the hyphenated slug, e.g.
  `[Getting Started](Getting-Started)`.
- `Home.md` is the landing page.
- `_Sidebar.md` and `_Footer.md` are special: they render on the side and bottom
  of every page and never get their own page.

## Publishing to the wiki

The wiki must be **initialised once** before it has a git repo to push to: open
<https://github.com/arnavj/SlopeScript/wiki>, click **Create the first page**,
and save anything (the publish step overwrites it).

Then run the script from the repo root:

```bash
./wiki/publish.sh
```

It clones `SlopeScript.wiki.git`, copies every `*.md` here into it, and pushes.
Re-run it any time these sources change.

### Doing it manually

```bash
git clone https://github.com/arnavj/SlopeScript.wiki.git /tmp/ss-wiki
cp wiki/*.md /tmp/ss-wiki/
rm -f /tmp/ss-wiki/README.md          # this file is not a wiki page
cd /tmp/ss-wiki
git add -A
git -c user.email="951585+arnavj@users.noreply.github.com" \
    commit -m "Update wiki from main repo wiki/ sources"
git push
```

> **Heads up — GitHub error `GH007`** ("your push would publish a private email
> address"): that means the commit was authored with a private email while
> *Settings → Emails → Block command line pushes that expose my email* is on.
> Commit with your `@users.noreply.github.com` address instead (as above) — the
> `publish.sh` script already does this for you.

## Editing

Edit the Markdown here, open a PR, and once it merges, run the publish script.
Cross-page links use the hyphenated page slug **without** the `.md`, e.g.
`[Standard Library](Standard-Library)`.
