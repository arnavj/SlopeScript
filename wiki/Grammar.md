# Grammar 📐

The formal grammar of SlopeScript, in EBNF, ignoring whitespace and comments.
This mirrors §16 of the
[Language Specification](https://github.com/arnavj/SlopeScript/blob/main/LANGUAGE_SPEC.md#16-grammar).

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

## Lexical notes

- **Identifiers** (`IDENT`): letters, digits, and `_`, not starting with a
  digit. Convention is `camelCase`.
- **Numbers** (`NUMBER`): `42`, `3.14`, `-7` (unary minus). Integers and
  decimals share one type.
- **Text** (`STRING`): double- or single-quoted. Escapes: `\n \t \r \\ \" \' \0
  \{`. Strings cannot span lines. `STRING` literals may contain `{expression}`
  interpolations.
- **Comments**: `// to end of line` and `/* block comments */`.
- **Whitespace and indentation are not significant** — the `runout`/`nail`
  keywords delimit blocks, not layout.

## Two placement rules

The grammar is almost free-form, but two rules keep statements from bleeding
into each other:

1. A **call's opening `(`** must sit on the **same line** as the callee.
2. **`carve` and `stomp`** only take arguments that start on their **own line**
   (the same line as the keyword).

Both are enforced by the parser so that consecutive statements are never
accidentally joined.

## Reserved keywords

```
summit lodge pack carve greenCircle blueSquare blackDiamond
gondola liftline in trick nail runout stomp bail sendIt
powder ice whiteout patrol patroller avalanche traverse
```

Builtin **function names** (`length`, `map`, `round`, …) are *not* reserved —
they're ordinary global values you can shadow with your own tricks.

---

See also: [Cheat Sheet](Cheat-Sheet) · [Language Internals](Language-Internals).
