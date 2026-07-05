#!/usr/bin/env python3
"""
SlopeScript — a skiing-themed programming language.

Code flows downhill: every program starts at the `summit` and ends at the
`lodge`. In between you pack gear (variables), carve output into the snow,
ride gondolas (while loops) and liftlines (for loops), pull off tricks
(functions), and when things go wrong, ski patrol (error handling) has your
back.

Usage:
    slope program.slope        run a program
    slope                      start the interactive REPL
    slope --version            print version
    slope --help               show help

This file is the entire implementation: lexer, parser, interpreter,
standard library ("the base lodge"), REPL, and CLI. Zero dependencies.
"""

import json
import math
import os
import random
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

VERSION = "2.2.0"

# ---------------------------------------------------------------------------
# Errors and control-flow signals
# ---------------------------------------------------------------------------

class SlopeError(Exception):
    """Base class for all SlopeScript errors."""

    def __init__(self, message: str, line: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.line = line


class SlopeSyntaxError(SlopeError):
    """The trail is closed: the source code could not be parsed."""


class SlopeRuntimeError(SlopeError):
    """A wipeout at runtime."""


class AvalancheError(SlopeError):
    """A user-triggered error (`avalanche <value>`), catchable by `patroller`."""

    def __init__(self, value: Any, line: Optional[int] = None):
        super().__init__(format_value(value), line)
        self.value = value


class LiftsClosedError(SlopeError):
    """Input ran out (end of file). Deliberately NOT catchable by patroller,
    so programs that retry on bad input can't spin forever once stdin closes."""


class BailSignal(Exception):
    """`bail` — break out of the current loop."""

    def __init__(self, line: Optional[int] = None):
        self.line = line


class SendItSignal(Exception):
    """`sendIt` — continue to the next loop iteration."""

    def __init__(self, line: Optional[int] = None):
        self.line = line


class StompSignal(Exception):
    """`stomp` — return from the current trick."""

    def __init__(self, value: Any, line: Optional[int] = None):
        self.value = value
        self.line = line


class SlopeTimeout(Exception):
    """A run exceeded its wall-clock budget (used by the web playground).

    Deliberately NOT a SlopeError, so patroller can't catch it — a runaway
    program can't hide inside a patrol block and outrun the timeout."""

    def __init__(self, message: str = "the run took too long"):
        super().__init__(message)
        self.message = message


# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------

KEYWORDS = {
    'summit': 'SUMMIT',
    'lodge': 'LODGE',
    'pack': 'PACK',
    'carve': 'CARVE',
    'greenCircle': 'GREEN',
    'blueSquare': 'BLUE',
    'blackDiamond': 'BLACK',
    'gondola': 'GONDOLA',
    'liftline': 'LIFTLINE',
    'in': 'IN',
    'trick': 'TRICK',
    'nail': 'RUNOUT',      # traditional way to finish a trick
    'runout': 'RUNOUT',    # universal end-of-block
    'stomp': 'STOMP',      # return from a trick
    'bail': 'BAIL',        # break
    'sendIt': 'SENDIT',    # continue
    'powder': 'TRUE',
    'ice': 'FALSE',
    'whiteout': 'NULL',    # null / nothing
    'patrol': 'PATROL',    # try
    'patroller': 'PATROLLER',  # catch
    'avalanche': 'AVALANCHE',  # throw
    'traverse': 'TRAVERSE',    # import another .slope file
}

TWO_CHAR_OPS = {
    '==': 'EQ', '!=': 'NEQ', '<=': 'LTE', '>=': 'GTE',
    '&&': 'AND', '||': 'OR',
    '+=': 'PLUSEQ', '-=': 'MINUSEQ', '*=': 'MULTEQ', '/=': 'DIVEQ',
    '**': 'POW',
}

ONE_CHAR_OPS = {
    '+': 'PLUS', '-': 'MINUS', '*': 'MULT', '/': 'DIV', '%': 'MOD',
    '=': 'ASSIGN', '<': 'LT', '>': 'GT',
    '(': 'LPAREN', ')': 'RPAREN',
    '[': 'LBRACKET', ']': 'RBRACKET',
    '{': 'LBRACE', '}': 'RBRACE',
    ',': 'COMMA', '!': 'NOT', '.': 'DOT', ':': 'COLON',
}

ESCAPES = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"', "'": "'", '0': '\0'}


class Token:
    __slots__ = ('type', 'value', 'line')

    def __init__(self, type: str, value: Any, line: int):
        self.type = type
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line {self.line})"


class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.tokens: List[Token] = []

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.code):
            self.skip_whitespace()
            if self.pos >= len(self.code):
                break
            if self.peek(2) == '//':
                self.skip_line_comment()
            elif self.peek(2) == '/*':
                self.skip_block_comment()
            elif self.current().isalpha() or self.current() == '_':
                self.read_identifier()
            elif self.current().isdigit():
                self.read_number()
            elif self.current() in '"\'':
                self.read_string()
            else:
                self.read_operator()
        return self.tokens

    def current(self) -> str:
        return self.code[self.pos] if self.pos < len(self.code) else '\0'

    def peek(self, n: int = 1) -> str:
        return self.code[self.pos:self.pos + n]

    def advance(self, n: int = 1):
        for _ in range(n):
            if self.pos < len(self.code):
                if self.code[self.pos] == '\n':
                    self.line += 1
                self.pos += 1

    def skip_whitespace(self):
        while self.current() in ' \t\r\n' and self.pos < len(self.code):
            self.advance()

    def skip_line_comment(self):
        while self.current() != '\n' and self.pos < len(self.code):
            self.advance()

    def skip_block_comment(self):
        start_line = self.line
        self.advance(2)
        while self.peek(2) != '*/':
            if self.pos >= len(self.code):
                raise SlopeSyntaxError("Unclosed block comment (missing '*/')", start_line)
            self.advance()
        self.advance(2)

    def read_identifier(self):
        start = self.pos
        while self.current().isalnum() or self.current() == '_':
            self.advance()
        value = self.code[start:self.pos]
        token_type = KEYWORDS.get(value, 'IDENTIFIER')
        if token_type == 'TRUE':
            self.tokens.append(Token('TRUE', True, self.line))
        elif token_type == 'FALSE':
            self.tokens.append(Token('FALSE', False, self.line))
        elif token_type == 'NULL':
            self.tokens.append(Token('NULL', None, self.line))
        else:
            self.tokens.append(Token(token_type, value, self.line))

    def read_number(self):
        start = self.pos
        while self.current().isdigit():
            self.advance()
        if self.current() == '.' and self.pos + 1 < len(self.code) and self.code[self.pos + 1].isdigit():
            self.advance()
            while self.current().isdigit():
                self.advance()
            value: Any = float(self.code[start:self.pos])
        else:
            value = int(self.code[start:self.pos])
        self.tokens.append(Token('NUMBER', value, self.line))

    def read_string(self):
        # Text supports {expression} interpolation. A plain string becomes a
        # STRING token; interpolated text becomes an ISTRING token whose value
        # is a list of ('t', text) and ('e', expr_source, line) parts.
        quote = self.current()
        start_line = self.line
        self.advance()
        parts: List[Tuple] = []
        buf: List[str] = []
        while True:
            ch = self.current()
            if self.pos >= len(self.code) or ch == '\n':
                raise SlopeSyntaxError("Unterminated string — did you forget a closing quote?", start_line)
            if ch == quote:
                self.advance()
                break
            if ch == '\\':
                self.advance()
                esc = self.current()
                if esc in ('{', '}'):
                    buf.append(esc)
                else:
                    buf.append(ESCAPES.get(esc, esc))
                self.advance()
                continue
            if ch == '{':
                expr_line = self.line
                self.advance()
                if self.current() == '}':
                    buf.append('{}')  # empty braces stay literal
                    self.advance()
                    continue
                source = self.read_interpolation(start_line)
                if buf:
                    parts.append(('t', ''.join(buf)))
                    buf = []
                parts.append(('e', source, expr_line))
                continue
            buf.append(ch)
            self.advance()
        if not parts:
            self.tokens.append(Token('STRING', ''.join(buf), start_line))
        else:
            if buf:
                parts.append(('t', ''.join(buf)))
            self.tokens.append(Token('ISTRING', parts, start_line))

    def read_interpolation(self, start_line: int) -> str:
        """Collect the source between { and its matching }, respecting
        nested braces and string literals inside the interpolation."""
        depth = 1
        chars: List[str] = []
        while True:
            if self.pos >= len(self.code) or self.current() == '\n':
                raise SlopeSyntaxError("Unclosed {...} interpolation in text — "
                                       "escape a literal brace as \\{", start_line)
            ch = self.current()
            if ch in '"\'':
                inner_quote = ch
                chars.append(ch)
                self.advance()
                while True:
                    if self.pos >= len(self.code) or self.current() == '\n':
                        raise SlopeSyntaxError("Unterminated string inside a {...} interpolation",
                                               start_line)
                    c2 = self.current()
                    chars.append(c2)
                    self.advance()
                    if c2 == '\\':
                        if self.pos < len(self.code) and self.current() != '\n':
                            chars.append(self.current())
                            self.advance()
                        continue
                    if c2 == inner_quote:
                        break
                continue
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    self.advance()
                    return ''.join(chars)
            chars.append(ch)
            self.advance()

    def read_operator(self):
        two = self.peek(2)
        if two in TWO_CHAR_OPS:
            self.tokens.append(Token(TWO_CHAR_OPS[two], two, self.line))
            self.advance(2)
            return
        ch = self.current()
        if ch in ONE_CHAR_OPS:
            self.tokens.append(Token(ONE_CHAR_OPS[ch], ch, self.line))
            self.advance()
            return
        raise SlopeSyntaxError(f"Unexpected character {ch!r} on the trail", self.line)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------
#
# Statements are tuples whose last element is the source line:
#   ('pack', name, expr, line)          declare / set a variable
#   ('assign', target, op, expr, line)  reassign; target is a var/index/member expr
#   ('carve', [exprs], line)            print
#   ('cond', [(cond|None, body)], line) greenCircle / blueSquare / blackDiamond
#   ('gondola', cond, body, line)       while loop
#   ('liftline', var, iterable, body, line)  for-each loop
#   ('trick', name, params, body, line) function definition
#   ('stomp', expr|None, line)          return
#   ('bail', line) / ('sendit', line)   break / continue
#   ('patrol', body, err_name, handler, line)  try / catch
#   ('avalanche', expr, line)           throw
#   ('expr', expr, line)                expression statement
#
# Expressions:
#   ('lit', value)                      numbers, strings, powder/ice, whiteout
#   ('var', name, line)
#   ('rack', [exprs], line)             array literal
#   ('locker', [(key, expr)], line)     dictionary literal
#   ('index', base, idx, line)
#   ('member', base, name, line)
#   ('call', name, [args], line)
#   ('bin', op, left, right, line)
#   ('un', op, expr, line)

EXPR_START = {
    'NUMBER', 'STRING', 'ISTRING', 'TRUE', 'FALSE', 'NULL', 'IDENTIFIER',
    'LPAREN', 'LBRACKET', 'LBRACE', 'NOT', 'MINUS', 'TRICK',
}

BLOCK_OPENERS = {'GREEN', 'GONDOLA', 'LIFTLINE', 'TRICK', 'PATROL'}


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    # -- token helpers ------------------------------------------------------

    def current(self) -> Optional[Token]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def check(self, *types: str) -> bool:
        tok = self.current()
        return tok is not None and tok.type in types

    def advance(self) -> Token:
        tok = self.current()
        if tok is None:
            raise SlopeSyntaxError("Unexpected end of program — did you reach the lodge too soon?",
                                   self.tokens[-1].line if self.tokens else 1)
        self.pos += 1
        return tok

    def expect(self, token_type: str, hint: str = '') -> Token:
        tok = self.current()
        if tok is None or tok.type != token_type:
            got = describe_token(tok)
            msg = f"Expected {describe_type(token_type)} but found {got}"
            if hint:
                msg += f" — {hint}"
            raise SlopeSyntaxError(msg, tok.line if tok else self.last_line())
        return self.advance()

    def last_line(self) -> int:
        return self.tokens[-1].line if self.tokens else 1

    def at_end(self) -> bool:
        return self.pos >= len(self.tokens)

    # -- entry points -------------------------------------------------------

    def parse_program(self) -> List[Tuple]:
        self.expect('SUMMIT', "every SlopeScript program starts at the summit")
        body = self.parse_block({'LODGE'}, opened_at=1, what="program")
        self.expect('LODGE', "every run ends at the lodge")
        if not self.at_end():
            tok = self.current()
            raise SlopeSyntaxError(f"Found {describe_token(tok)} after the lodge — the run is already over", tok.line)
        return body

    def parse_snippet(self) -> List[Tuple]:
        """Parse statements without requiring summit/lodge (REPL mode)."""
        if self.check('SUMMIT'):
            return self.parse_program()
        body = []
        while not self.at_end():
            body.append(self.parse_statement())
        return body

    def parse_expression_only(self) -> Tuple:
        expr = self.parse_expression()
        if not self.at_end():
            tok = self.current()
            raise SlopeSyntaxError(f"Unexpected {describe_token(tok)} after expression", tok.line)
        return expr

    # -- statements ---------------------------------------------------------

    def parse_block(self, stop_types: set, opened_at: int, what: str) -> List[Tuple]:
        body = []
        while not self.check(*stop_types):
            if self.at_end() or (self.check('LODGE') and 'LODGE' not in stop_types):
                raise SlopeSyntaxError(
                    f"The {what} starting on line {opened_at} was never closed — expected "
                    + " or ".join(sorted(describe_type(t) for t in stop_types)),
                    self.current().line if self.current() else self.last_line())
            body.append(self.parse_statement())
        return body

    def parse_statement(self) -> Tuple:
        tok = self.current()
        t = tok.type
        if t == 'PACK':
            return self.parse_pack()
        if t == 'CARVE':
            return self.parse_carve()
        if t == 'GREEN':
            return self.parse_conditional()
        if t in ('BLUE', 'BLACK'):
            raise SlopeSyntaxError(f"{tok.value} without a matching greenCircle — "
                                   "every trail rating chain starts with greenCircle", tok.line)
        if t == 'GONDOLA':
            return self.parse_gondola()
        if t == 'LIFTLINE':
            return self.parse_liftline()
        if t == 'TRICK':
            nxt = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if nxt is not None and nxt.type == 'IDENTIFIER':
                return self.parse_trick()
            # `trick (x) ... nail` with no name is an anonymous trick expression.
            return self.parse_assign_or_expr()
        if t == 'TRAVERSE':
            self.advance()
            expr = self.parse_expression()
            return ('traverse', expr, tok.line)
        if t == 'PATROL':
            return self.parse_patrol()
        if t == 'PATROLLER':
            raise SlopeSyntaxError("patroller without a matching patrol block", tok.line)
        if t == 'RUNOUT':
            raise SlopeSyntaxError("runout with no open block — there is nothing to close here", tok.line)
        if t == 'STOMP':
            self.advance()
            expr = None
            nxt = self.current()
            if nxt is not None and nxt.line == tok.line and nxt.type in EXPR_START:
                expr = self.parse_expression()
            return ('stomp', expr, tok.line)
        if t == 'BAIL':
            self.advance()
            return ('bail', tok.line)
        if t == 'SENDIT':
            self.advance()
            return ('sendit', tok.line)
        if t == 'AVALANCHE':
            self.advance()
            expr = self.parse_expression()
            return ('avalanche', expr, tok.line)
        # Assignment or bare expression statement.
        return self.parse_assign_or_expr()

    def parse_pack(self) -> Tuple:
        tok = self.expect('PACK')
        name = self.expect('IDENTIFIER', "pack needs a name, like: pack speed = 0").value
        self.expect('ASSIGN', f"pack {name} needs a value, like: pack {name} = 0")
        value = self.parse_expression()
        return ('pack', name, value, tok.line)

    def parse_carve(self) -> Tuple:
        tok = self.expect('CARVE')
        exprs: List[Tuple] = []
        nxt = self.current()
        if nxt is not None and nxt.line == tok.line and nxt.type in EXPR_START:
            exprs.append(self.parse_expression())
            while self.check('COMMA'):
                self.advance()
                exprs.append(self.parse_expression())
        return ('carve', exprs, tok.line)

    def parse_conditional(self) -> Tuple:
        first = self.expect('GREEN')
        branches: List[Tuple[Optional[Tuple], List[Tuple]]] = []
        self.expect('LPAREN', "greenCircle needs a condition in parentheses")
        condition = self.parse_expression()
        self.expect('RPAREN')
        body = self.parse_block({'BLUE', 'BLACK', 'RUNOUT'}, first.line, "greenCircle")
        branches.append((condition, body))
        while self.check('BLUE'):
            blue = self.advance()
            self.expect('LPAREN', "blueSquare needs a condition in parentheses")
            condition = self.parse_expression()
            self.expect('RPAREN')
            body = self.parse_block({'BLUE', 'BLACK', 'RUNOUT'}, blue.line, "blueSquare")
            branches.append((condition, body))
        if self.check('BLACK'):
            black = self.advance()
            body = self.parse_block({'RUNOUT'}, black.line, "blackDiamond")
            branches.append((None, body))
        self.expect('RUNOUT', "close the trail rating chain with runout")
        return ('cond', branches, first.line)

    def parse_gondola(self) -> Tuple:
        tok = self.expect('GONDOLA')
        self.expect('LPAREN', "gondola needs a condition, like: gondola (laps < 5)")
        condition = self.parse_expression()
        self.expect('RPAREN')
        body = self.parse_block({'RUNOUT'}, tok.line, "gondola loop")
        self.expect('RUNOUT', "close the gondola loop with runout")
        return ('gondola', condition, body, tok.line)

    def parse_liftline(self) -> Tuple:
        tok = self.expect('LIFTLINE')
        var = self.expect('IDENTIFIER', "liftline needs a rider, like: liftline skier in skiers").value
        self.expect('IN', f"liftline needs 'in', like: liftline {var} in skiers")
        iterable = self.parse_expression()
        body = self.parse_block({'RUNOUT'}, tok.line, "liftline loop")
        self.expect('RUNOUT', "close the liftline loop with runout")
        return ('liftline', var, iterable, body, tok.line)

    def parse_trick(self) -> Tuple:
        tok = self.expect('TRICK')
        name = self.expect('IDENTIFIER', "trick needs a name, like: trick greet(name)").value
        self.expect('LPAREN', f"trick {name} needs a parameter list, even if empty: trick {name}()")
        params = self.parse_params()
        body = self.parse_block({'RUNOUT'}, tok.line, f"trick {name}")
        self.expect('RUNOUT', "finish the trick with nail (or runout)")
        return ('trick', name, params, body, tok.line)

    def parse_params(self) -> List[str]:
        params: List[str] = []
        while not self.check('RPAREN'):
            params.append(self.expect('IDENTIFIER', "trick parameters must be names").value)
            if self.check('COMMA'):
                self.advance()
            elif not self.check('RPAREN'):
                raise SlopeSyntaxError("Expected ',' or ')' in trick parameter list",
                                       self.current().line if self.current() else self.last_line())
        self.expect('RPAREN')
        return params

    def parse_patrol(self) -> Tuple:
        tok = self.expect('PATROL')
        body = self.parse_block({'PATROLLER'}, tok.line, "patrol block")
        self.expect('PATROLLER', "patrol needs a patroller to handle trouble")
        self.expect('LPAREN', "patroller needs a name for the report, like: patroller (whoops)")
        err_name = self.expect('IDENTIFIER').value
        self.expect('RPAREN')
        handler = self.parse_block({'RUNOUT'}, tok.line, "patroller block")
        self.expect('RUNOUT', "close the patrol with runout")
        return ('patrol', body, err_name, handler, tok.line)

    def parse_assign_or_expr(self) -> Tuple:
        tok = self.current()
        if tok.type == 'IDENTIFIER':
            saved = self.pos
            target = self.parse_postfix(('var', self.advance().value, tok.line))
            if self.check('ASSIGN', 'PLUSEQ', 'MINUSEQ', 'MULTEQ', 'DIVEQ'):
                op = self.advance().value
                value = self.parse_expression()
                if target[0] not in ('var', 'index', 'member'):
                    raise SlopeSyntaxError("Can't assign to that — assign to a variable, "
                                           "rack slot, or locker entry", tok.line)
                return ('assign', target, op, value, tok.line)
            self.pos = saved
        if tok.type not in EXPR_START:
            raise SlopeSyntaxError(f"Unexpected {describe_token(tok)} — expected a statement", tok.line)
        expr = self.parse_expression()
        return ('expr', expr, tok.line)

    # -- expressions --------------------------------------------------------

    def parse_expression(self) -> Tuple:
        return self.parse_or()

    def parse_or(self) -> Tuple:
        left = self.parse_and()
        while self.check('OR'):
            line = self.advance().line
            left = ('bin', '||', left, self.parse_and(), line)
        return left

    def parse_and(self) -> Tuple:
        left = self.parse_equality()
        while self.check('AND'):
            line = self.advance().line
            left = ('bin', '&&', left, self.parse_equality(), line)
        return left

    def parse_equality(self) -> Tuple:
        left = self.parse_comparison()
        while self.check('EQ', 'NEQ'):
            tok = self.advance()
            left = ('bin', tok.value, left, self.parse_comparison(), tok.line)
        return left

    def parse_comparison(self) -> Tuple:
        left = self.parse_additive()
        while self.check('LT', 'GT', 'LTE', 'GTE', 'IN'):
            tok = self.advance()
            op = 'in' if tok.type == 'IN' else tok.value
            left = ('bin', op, left, self.parse_additive(), tok.line)
        return left

    def parse_additive(self) -> Tuple:
        left = self.parse_multiplicative()
        while self.check('PLUS', 'MINUS'):
            tok = self.advance()
            left = ('bin', tok.value, left, self.parse_multiplicative(), tok.line)
        return left

    def parse_multiplicative(self) -> Tuple:
        left = self.parse_unary()
        while self.check('MULT', 'DIV', 'MOD'):
            tok = self.advance()
            left = ('bin', tok.value, left, self.parse_unary(), tok.line)
        return left

    def parse_unary(self) -> Tuple:
        if self.check('NOT', 'MINUS'):
            tok = self.advance()
            return ('un', tok.value, self.parse_unary(), tok.line)
        return self.parse_power()

    def parse_power(self) -> Tuple:
        base = self.parse_postfix(self.parse_primary())
        if self.check('POW'):
            tok = self.advance()
            return ('bin', '**', base, self.parse_unary(), tok.line)
        return base

    def parse_postfix(self, expr: Tuple) -> Tuple:
        while True:
            if self.check('LBRACKET'):
                line = self.advance().line
                index = self.parse_expression()
                self.expect('RBRACKET')
                expr = ('index', expr, index, line)
            elif self.check('DOT'):
                line = self.advance().line
                name = self.expect('IDENTIFIER', "expected a locker key after '.'").value
                expr = ('member', expr, name, line)
            elif self.check('LPAREN') and self.tokens[self.pos - 1].line == self.current().line:
                # Tricks are first-class: any expression can be called. The
                # same-line rule stops a parenthesised statement on the next
                # line from being read as arguments.
                line = self.advance().line
                args: List[Tuple] = []
                while not self.check('RPAREN'):
                    args.append(self.parse_expression())
                    if self.check('COMMA'):
                        self.advance()
                    elif not self.check('RPAREN'):
                        raise SlopeSyntaxError("Expected ',' or ')' in trick call",
                                               self.current().line if self.current() else self.last_line())
                self.expect('RPAREN')
                if expr[0] == 'var':
                    expr = ('call', expr[1], args, line)
                else:
                    expr = ('callexpr', expr, args, line)
            else:
                return expr

    def parse_primary(self) -> Tuple:
        tok = self.current()
        if tok is None:
            raise SlopeSyntaxError("Ran out of trail while reading an expression", self.last_line())
        if tok.type == 'NUMBER' or tok.type == 'STRING':
            self.advance()
            return ('lit', tok.value)
        if tok.type == 'ISTRING':
            self.advance()
            parts: List[Tuple] = []
            for part in tok.value:
                if part[0] == 't':
                    parts.append(('t', part[1]))
                else:
                    source, expr_line = part[1], part[2]
                    try:
                        sub = Parser(Lexer(source).tokenize()).parse_expression_only()
                    except SlopeSyntaxError as e:
                        raise SlopeSyntaxError(f"Inside the {{{source}}} interpolation: {e.message}",
                                               expr_line)
                    parts.append(('e', sub))
            return ('interp', parts, tok.line)
        if tok.type in ('TRUE', 'FALSE', 'NULL'):
            self.advance()
            return ('lit', tok.value)
        if tok.type == 'TRICK':
            self.advance()
            self.expect('LPAREN', "an anonymous trick needs parameters, like: trick(x)")
            params = self.parse_params()
            body = self.parse_block({'RUNOUT'}, tok.line, "anonymous trick")
            self.expect('RUNOUT', "finish the trick with nail (or runout)")
            return ('trickexpr', params, body, tok.line)
        if tok.type == 'IDENTIFIER':
            self.advance()
            return ('var', tok.value, tok.line)
        if tok.type == 'LPAREN':
            self.advance()
            expr = self.parse_expression()
            self.expect('RPAREN')
            return expr
        if tok.type == 'LBRACKET':
            return self.parse_rack()
        if tok.type == 'LBRACE':
            return self.parse_locker()
        raise SlopeSyntaxError(f"Unexpected {describe_token(tok)} in expression", tok.line)

    def parse_rack(self) -> Tuple:
        tok = self.expect('LBRACKET')
        elements: List[Tuple] = []
        while not self.check('RBRACKET'):
            elements.append(self.parse_expression())
            if self.check('COMMA'):
                self.advance()
            elif not self.check('RBRACKET'):
                raise SlopeSyntaxError("Expected ',' or ']' in rack",
                                       self.current().line if self.current() else self.last_line())
        self.expect('RBRACKET')
        return ('rack', elements, tok.line)

    def parse_locker(self) -> Tuple:
        tok = self.expect('LBRACE')
        pairs: List[Tuple[Any, Tuple]] = []
        while not self.check('RBRACE'):
            key_tok = self.current()
            if key_tok is None:
                raise SlopeSyntaxError("Unclosed locker (missing '}')", tok.line)
            if key_tok.type in ('STRING', 'NUMBER'):
                key = key_tok.value
                self.advance()
            elif key_tok.type == 'IDENTIFIER':
                key = key_tok.value
                self.advance()
            else:
                raise SlopeSyntaxError("Locker keys must be names, text, or numbers", key_tok.line)
            self.expect('COLON', "locker entries look like: name: value")
            pairs.append((key, self.parse_expression()))
            if self.check('COMMA'):
                self.advance()
            elif not self.check('RBRACE'):
                raise SlopeSyntaxError("Expected ',' or '}' in locker",
                                       self.current().line if self.current() else self.last_line())
        self.expect('RBRACE')
        return ('locker', pairs, tok.line)


TOKEN_DESCRIPTIONS = {
    'SUMMIT': "'summit'", 'LODGE': "'lodge'", 'RUNOUT': "'runout'",
    'LPAREN': "'('", 'RPAREN': "')'", 'LBRACKET': "'['", 'RBRACKET': "']'",
    'LBRACE': "'{'", 'RBRACE': "'}'", 'ASSIGN': "'='", 'COLON': "':'",
    'COMMA': "','", 'IDENTIFIER': 'a name', 'IN': "'in'",
    'PATROLLER': "'patroller'",
}


def describe_type(token_type: str) -> str:
    return TOKEN_DESCRIPTIONS.get(token_type, f"'{token_type.lower()}'")


def describe_token(tok: Optional[Token]) -> str:
    if tok is None:
        return "the end of the program"
    if tok.type == 'STRING':
        return f'text "{tok.value}"'
    if tok.type == 'NUMBER':
        return f"number {tok.value}"
    return f"'{tok.value}'"


# ---------------------------------------------------------------------------
# Values and formatting
# ---------------------------------------------------------------------------

def format_value(value: Any) -> str:
    """How a value is carved into the snow."""
    if value is True:
        return 'powder'
    if value is False:
        return 'ice'
    if value is None:
        return 'whiteout'
    if isinstance(value, float):
        if math.isfinite(value) and value == int(value) and abs(value) < 1e16:
            return str(int(value))
        return repr(value)
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return '[' + ', '.join(format_inner(v) for v in value) + ']'
    if isinstance(value, dict):
        return '{' + ', '.join(f"{format_inner(k)}: {format_inner(v)}" for k, v in value.items()) + '}'
    if isinstance(value, Trick):
        return f"<trick {value.name}>"
    if isinstance(value, BuiltinRef):
        return f"<trick {value.name} (base lodge)>"
    return str(value)


def format_inner(value: Any) -> str:
    if isinstance(value, str):
        return f'"{value}"'
    return format_value(value)


def is_truthy(value: Any) -> bool:
    if value is True:
        return True
    if value is False or value is None:
        return False
    t = type(value)
    if t is int or t is float:
        return value != 0
    if t is str or t is list or t is dict:
        return len(value) > 0
    return True


def type_name(value: Any) -> str:
    if isinstance(value, bool):
        return 'condition'   # powder / ice
    if value is None:
        return 'whiteout'
    if isinstance(value, (int, float)):
        return 'number'
    if isinstance(value, str):
        return 'text'
    if isinstance(value, list):
        return 'rack'
    if isinstance(value, dict):
        return 'locker'
    if isinstance(value, (Trick, BuiltinRef)):
        return 'trick'
    return type(value).__name__


class Trick:
    """A user-defined function. First-class: store it, pass it, stomp it."""

    __slots__ = ('name', 'params', 'body', 'closure')

    def __init__(self, name: str, params: List[str], body: List[Tuple], closure: 'Environment'):
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure


class BuiltinRef:
    """A Base Lodge function as a first-class value (e.g. `pack f = groom`)."""

    __slots__ = ('name', 'fn', 'min_args', 'max_args')

    def __init__(self, name: str, fn, min_args: int, max_args: Optional[int]):
        self.name = name
        self.fn = fn
        self.min_args = min_args
        self.max_args = max_args


class Environment:
    __slots__ = ('vars', 'parent')

    def __init__(self, parent: Optional['Environment'] = None):
        self.vars: Dict[str, Any] = {}
        self.parent = parent

    def declare(self, name: str, value: Any):
        self.vars[name] = value

    def get(self, name: str, line: Optional[int] = None) -> Any:
        env: Optional[Environment] = self
        while env is not None:
            if name in env.vars:
                return env.vars[name]
            env = env.parent
        raise SlopeRuntimeError(f"'{name}' is not packed — pack it first, like: pack {name} = ...", line)

    def assign(self, name: str, value: Any, line: Optional[int] = None):
        env: Optional[Environment] = self
        while env is not None:
            if name in env.vars:
                env.vars[name] = value
                return
            env = env.parent
        raise SlopeRuntimeError(f"'{name}' is not packed — pack it first, like: pack {name} = ...", line)


# ---------------------------------------------------------------------------
# The Base Lodge (standard library)
# ---------------------------------------------------------------------------

def _require_number(value: Any, fn: str, line: Optional[int]) -> Any:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SlopeRuntimeError(f"{fn}() needs a number, not {type_name(value)}", line)
    return value


def _require_rack(value: Any, fn: str, line: Optional[int]) -> list:
    if not isinstance(value, list):
        raise SlopeRuntimeError(f"{fn}() needs a rack, not {type_name(value)}", line)
    return value


def _require_text(value: Any, fn: str, line: Optional[int]) -> str:
    if not isinstance(value, str):
        raise SlopeRuntimeError(f"{fn}() needs text, not {type_name(value)}", line)
    return value


def _require_locker(value: Any, fn: str, line: Optional[int]) -> dict:
    if not isinstance(value, dict):
        raise SlopeRuntimeError(f"{fn}() needs a locker, not {type_name(value)}", line)
    return value


def _normalize_number(value: float) -> Any:
    if isinstance(value, float) and math.isfinite(value) and value == int(value):
        return int(value)
    return value


def build_builtins() -> Dict[str, Any]:
    B: Dict[str, Any] = {}

    def builtin(name, min_args, max_args, aliases=()):
        def register(fn):
            entry = BuiltinRef(name, fn, min_args, max_args)
            B[name] = entry
            for alias in aliases:
                B[alias] = entry
            return fn
        return register

    # ---- input / output ----
    @builtin('chairlift', 0, 1)
    def _chairlift(args, line, interp):
        prompt = ''
        if args:
            prompt = format_value(args[0]) + ' '
        try:
            return input(prompt)
        except EOFError:
            raise LiftsClosedError("The lifts are closed — there is no more input to read", line)

    # ---- conversions ----
    @builtin('number', 1, 1, aliases=('tune',))
    def _number(args, line, interp):
        v = args[0]
        if isinstance(v, bool):
            return 1 if v else 0
        if isinstance(v, (int, float)):
            return v
        if isinstance(v, str):
            try:
                text = v.strip()
                return float(text) if ('.' in text or 'e' in text or 'E' in text) else int(text)
            except ValueError:
                raise SlopeRuntimeError(f'Could not tune "{v}" into a number', line)
        raise SlopeRuntimeError(f"Could not tune {type_name(v)} into a number", line)

    @builtin('text', 1, 1)
    def _text(args, line, interp):
        return format_value(args[0])

    @builtin('type', 1, 1, aliases=('trailMap',))
    def _type(args, line, interp):
        return type_name(args[0])

    # ---- racks & text ----
    @builtin('length', 1, 1)
    def _length(args, line, interp):
        v = args[0]
        if isinstance(v, (str, list, dict)):
            return len(v)
        raise SlopeRuntimeError(f"length() needs text, a rack, or a locker, not {type_name(v)}", line)

    @builtin('push', 2, 2, aliases=('stash',))
    def _push(args, line, interp):
        rack = _require_rack(args[0], 'push', line)
        rack.append(args[1])
        return rack

    @builtin('pop', 1, 1)
    def _pop(args, line, interp):
        rack = _require_rack(args[0], 'pop', line)
        if not rack:
            raise SlopeRuntimeError("pop() on an empty rack — there is nothing left to grab", line)
        return rack.pop()

    @builtin('laps', 1, 3, aliases=('range',))
    def _laps(args, line, interp):
        nums = [_require_number(a, 'laps', line) for a in args]
        if any(isinstance(n, float) for n in nums):
            raise SlopeRuntimeError("laps() needs whole numbers", line)
        return list(range(*nums))

    @builtin('groom', 1, 1, aliases=('sort',))
    def _groom(args, line, interp):
        rack = _require_rack(args[0], 'groom', line)
        try:
            return sorted(rack)
        except TypeError:
            raise SlopeRuntimeError("groom() can only sort a rack of all numbers or all text", line)

    @builtin('flip', 1, 1, aliases=('reverse',))
    def _flip(args, line, interp):
        v = args[0]
        if isinstance(v, list):
            return list(reversed(v))
        if isinstance(v, str):
            return v[::-1]
        raise SlopeRuntimeError(f"flip() needs a rack or text, not {type_name(v)}", line)

    @builtin('contains', 2, 2)
    def _contains(args, line, interp):
        container, item = args
        if isinstance(container, (list, str, dict)):
            return item in container
        raise SlopeRuntimeError(f"contains() needs a rack, text, or locker, not {type_name(container)}", line)

    @builtin('find', 2, 2)
    def _find(args, line, interp):
        container, item = args
        if isinstance(container, list):
            return container.index(item) if item in container else -1
        if isinstance(container, str):
            return container.find(item if isinstance(item, str) else format_value(item))
        raise SlopeRuntimeError(f"find() needs a rack or text, not {type_name(container)}", line)

    @builtin('slice', 2, 3)
    def _slice(args, line, interp):
        v = args[0]
        if not isinstance(v, (list, str)):
            raise SlopeRuntimeError(f"slice() needs a rack or text, not {type_name(v)}", line)
        start = int(_require_number(args[1], 'slice', line))
        end = int(_require_number(args[2], 'slice', line)) if len(args) > 2 else len(v)
        return v[start:end]

    @builtin('join', 2, 2)
    def _join(args, line, interp):
        rack = _require_rack(args[0], 'join', line)
        sep = _require_text(args[1], 'join', line)
        return sep.join(format_value(v) for v in rack)

    @builtin('split', 2, 2)
    def _split(args, line, interp):
        text = _require_text(args[0], 'split', line)
        sep = _require_text(args[1], 'split', line)
        if sep == '':
            return list(text)
        return text.split(sep)

    @builtin('upper', 1, 1, aliases=('shout',))
    def _upper(args, line, interp):
        return _require_text(args[0], 'upper', line).upper()

    @builtin('lower', 1, 1, aliases=('whisper',))
    def _lower(args, line, interp):
        return _require_text(args[0], 'lower', line).lower()

    @builtin('trim', 1, 1)
    def _trim(args, line, interp):
        return _require_text(args[0], 'trim', line).strip()

    @builtin('replace', 3, 3)
    def _replace(args, line, interp):
        return _require_text(args[0], 'replace', line).replace(
            _require_text(args[1], 'replace', line),
            _require_text(args[2], 'replace', line))

    @builtin('startsWith', 2, 2)
    def _starts(args, line, interp):
        return _require_text(args[0], 'startsWith', line).startswith(
            _require_text(args[1], 'startsWith', line))

    @builtin('endsWith', 2, 2)
    def _ends(args, line, interp):
        return _require_text(args[0], 'endsWith', line).endswith(
            _require_text(args[1], 'endsWith', line))

    # ---- lockers ----
    @builtin('keys', 1, 1)
    def _keys(args, line, interp):
        return list(_require_locker(args[0], 'keys', line).keys())

    @builtin('values', 1, 1)
    def _values(args, line, interp):
        return list(_require_locker(args[0], 'values', line).values())

    @builtin('has', 2, 2)
    def _has(args, line, interp):
        return args[1] in _require_locker(args[0], 'has', line)

    @builtin('drop', 2, 2)
    def _drop(args, line, interp):
        locker = _require_locker(args[0], 'drop', line)
        locker.pop(args[1], None)
        return locker

    # ---- math ----
    @builtin('abs', 1, 1)
    def _abs(args, line, interp):
        return abs(_require_number(args[0], 'abs', line))

    @builtin('round', 1, 2)
    def _round(args, line, interp):
        n = _require_number(args[0], 'round', line)
        digits = int(_require_number(args[1], 'round', line)) if len(args) > 1 else 0
        result = round(n, digits)
        return _normalize_number(result) if digits <= 0 else result

    @builtin('basin', 1, 1, aliases=('floor',))
    def _floor(args, line, interp):
        return math.floor(_require_number(args[0], 'basin', line))

    @builtin('cornice', 1, 1, aliases=('ceil',))
    def _ceil(args, line, interp):
        return math.ceil(_require_number(args[0], 'cornice', line))

    @builtin('sqrt', 1, 1)
    def _sqrt(args, line, interp):
        n = _require_number(args[0], 'sqrt', line)
        if n < 0:
            raise SlopeRuntimeError("sqrt() of a negative number — that slope does not exist", line)
        return _normalize_number(math.sqrt(n))

    @builtin('min', 1, None)
    def _min(args, line, interp):
        values = args[0] if len(args) == 1 and isinstance(args[0], list) else args
        if not values:
            raise SlopeRuntimeError("min() of an empty rack", line)
        return min(values)

    @builtin('max', 1, None)
    def _max(args, line, interp):
        values = args[0] if len(args) == 1 and isinstance(args[0], list) else args
        if not values:
            raise SlopeRuntimeError("max() of an empty rack", line)
        return max(values)

    @builtin('sum', 1, 1)
    def _sum(args, line, interp):
        rack = _require_rack(args[0], 'sum', line)
        total = 0
        for v in rack:
            total += _require_number(v, 'sum', line)
        return total

    @builtin('snowflake', 0, 2, aliases=('random',))
    def _snowflake(args, line, interp):
        if len(args) == 0:
            return random.random()
        if len(args) == 2:
            lo = _require_number(args[0], 'snowflake', line)
            hi = _require_number(args[1], 'snowflake', line)
            if isinstance(lo, int) and isinstance(hi, int):
                if lo > hi:
                    raise SlopeRuntimeError("snowflake(low, high) needs low <= high", line)
                return random.randint(lo, hi)
            return random.uniform(lo, hi)
        raise SlopeRuntimeError("snowflake() takes zero arguments or two (low, high)", line)

    # ---- higher-order tricks ----
    @builtin('map', 2, 2)
    def _map(args, line, interp):
        rack = _require_rack(args[0], 'map', line)
        fn = args[1]
        return [interp.call_value(fn, [item], line) for item in rack]

    @builtin('filter', 2, 2)
    def _filter(args, line, interp):
        rack = _require_rack(args[0], 'filter', line)
        fn = args[1]
        return [item for item in rack if is_truthy(interp.call_value(fn, [item], line))]

    @builtin('reduce', 2, 3)
    def _reduce(args, line, interp):
        rack = _require_rack(args[0], 'reduce', line)
        fn = args[1]
        if len(args) > 2:
            acc = args[2]
            items = rack
        else:
            if not rack:
                raise SlopeRuntimeError("reduce() on an empty rack needs a starting value: "
                                        "reduce(rack, fn, start)", line)
            acc = rack[0]
            items = rack[1:]
        for item in items:
            acc = interp.call_value(fn, [acc, item], line)
        return acc

    @builtin('each', 2, 2)
    def _each(args, line, interp):
        rack = _require_rack(args[0], 'each', line)
        fn = args[1]
        for item in rack:
            interp.call_value(fn, [item], line)
        return None

    # ---- files (the trail journal) ----
    def _open_error(action, path, err, line):
        reason = err.strerror or type(err).__name__
        return SlopeRuntimeError(f"Couldn't {action} '{path}': {reason}", line)

    @builtin('readFile', 1, 1)
    def _read_file(args, line, interp):
        path = _require_text(args[0], 'readFile', line)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except OSError as e:
            raise _open_error('read', path, e, line)

    @builtin('readLines', 1, 1)
    def _read_lines(args, line, interp):
        path = _require_text(args[0], 'readLines', line)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return [ln.rstrip('\n') for ln in f]
        except OSError as e:
            raise _open_error('read', path, e, line)

    @builtin('writeFile', 2, 2)
    def _write_file(args, line, interp):
        path = _require_text(args[0], 'writeFile', line)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(format_value(args[1]))
        except OSError as e:
            raise _open_error('write', path, e, line)
        return None

    @builtin('appendFile', 2, 2)
    def _append_file(args, line, interp):
        path = _require_text(args[0], 'appendFile', line)
        try:
            with open(path, 'a', encoding='utf-8') as f:
                f.write(format_value(args[1]))
        except OSError as e:
            raise _open_error('append to', path, e, line)
        return None

    @builtin('fileExists', 1, 1)
    def _file_exists(args, line, interp):
        return os.path.isfile(_require_text(args[0], 'fileExists', line))

    @builtin('deleteFile', 1, 1)
    def _delete_file(args, line, interp):
        path = _require_text(args[0], 'deleteFile', line)
        try:
            os.remove(path)
            return True
        except FileNotFoundError:
            return False
        except OSError as e:
            raise _open_error('delete', path, e, line)

    # ---- the radio (HTTP) ----
    def _headers_from(value, line):
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise SlopeRuntimeError(f"Headers must be a locker, not {type_name(value)}", line)
        return {str(k): format_value(v) for k, v in value.items()}

    def _http_get(url, headers, line):
        url = _require_text(url, 'radioBase', line)
        if not url.startswith(('http://', 'https://')):
            raise SlopeRuntimeError(f"radioBase needs an http(s) URL, got '{url}'", line)
        if sys.platform == 'emscripten':
            # Browser playground: ride the browser's own network stack.
            try:
                from pyodide.http import open_url
                return open_url(url).read()
            except Exception as e:
                raise SlopeRuntimeError(f"Couldn't reach {url} from the browser "
                                        f"(CORS or network): {e}", line)
        request = urllib.request.Request(
            url, headers={'User-Agent': f'SlopeScript/{VERSION}', **headers})
        try:
            with urllib.request.urlopen(request, timeout=30) as resp:
                return resp.read().decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            raise SlopeRuntimeError(f"HTTP {e.code} {e.reason} from {url}", line)
        except urllib.error.URLError as e:
            raise SlopeRuntimeError(f"Couldn't reach {url}: {e.reason}", line)
        except ValueError as e:
            raise SlopeRuntimeError(f"Bad URL '{url}': {e}", line)

    @builtin('radioBase', 1, 2, aliases=('fetch',))
    def _radio_base(args, line, interp):
        headers = _headers_from(args[1] if len(args) > 1 else None, line)
        return _http_get(args[0], headers, line)

    @builtin('radioJson', 1, 2, aliases=('fetchJson',))
    def _radio_json(args, line, interp):
        headers = _headers_from(args[1] if len(args) > 1 else None, line)
        headers.setdefault('Accept', 'application/json')
        body = _http_get(args[0], headers, line)
        try:
            return json.loads(body)
        except ValueError as e:
            raise SlopeRuntimeError(f"The radio answered, but it wasn't JSON: {e}", line)

    @builtin('radioPost', 2, 3, aliases=('post',))
    def _radio_post(args, line, interp):
        url = _require_text(args[0], 'radioPost', line)
        if not url.startswith(('http://', 'https://')):
            raise SlopeRuntimeError(f"radioPost needs an http(s) URL, got '{url}'", line)
        if sys.platform == 'emscripten':
            raise SlopeRuntimeError("radioPost isn't available in the web playground — "
                                    "run this program with the slope CLI", line)
        payload = args[1]
        headers = _headers_from(args[2] if len(args) > 2 else None, line)
        if isinstance(payload, (dict, list)):
            data = _to_json_text(payload, False, line).encode('utf-8')
            headers.setdefault('Content-Type', 'application/json')
        else:
            data = format_value(payload).encode('utf-8')
            headers.setdefault('Content-Type', 'text/plain; charset=utf-8')
        request = urllib.request.Request(
            url, data=data, method='POST',
            headers={'User-Agent': f'SlopeScript/{VERSION}', **headers})
        try:
            with urllib.request.urlopen(request, timeout=30) as resp:
                return resp.read().decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            raise SlopeRuntimeError(f"HTTP {e.code} {e.reason} from {url}", line)
        except urllib.error.URLError as e:
            raise SlopeRuntimeError(f"Couldn't reach {url}: {e.reason}", line)

    # ---- JSON ----
    def _to_json_text(value, pretty, line):
        try:
            return json.dumps(value, indent=2 if pretty else None, ensure_ascii=False)
        except (TypeError, ValueError):
            raise SlopeRuntimeError(f"Can't turn {type_name(value)} into JSON — "
                                    "use numbers, text, conditions, whiteout, racks, and lockers", line)

    @builtin('parseJson', 1, 1)
    def _parse_json(args, line, interp):
        text = _require_text(args[0], 'parseJson', line)
        try:
            return json.loads(text)
        except ValueError as e:
            raise SlopeRuntimeError(f"Couldn't parse JSON: {e}", line)

    @builtin('toJson', 1, 2)
    def _to_json(args, line, interp):
        pretty = is_truthy(args[1]) if len(args) > 1 else False
        return _to_json_text(args[0], pretty, line)

    # ---- misc ----
    @builtin('clock', 0, 0)
    def _clock(args, line, interp):
        return time.time()

    return B


BUILTINS = build_builtins()

MAX_TRICK_DEPTH = 200

# Each trick call uses a handful of Python stack frames; give the host
# interpreter enough headroom that MAX_TRICK_DEPTH is the limit users hit.
sys.setrecursionlimit(max(sys.getrecursionlimit(), 6000))


# ---------------------------------------------------------------------------
# Interpreter
# ---------------------------------------------------------------------------

class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.trick_depth = 0
        self.loaded_trails: set = set()   # absolute paths already traversed
        self.loading_trails: set = set()  # traversal in progress (cycle guard)
        self.dir_stack: List[str] = []    # directory context for relative traverses
        # Optional wall-clock budget: a time.monotonic() cutoff after which
        # loops raise SlopeTimeout. Left as None (no limit) for the CLI/REPL;
        # the browser playground sets it so an endless gondola can't hang a tab.
        self.deadline: Optional[float] = None

    def _tick(self):
        """Stop a run that has blown its wall-clock budget. Called once per
        loop iteration — the only place SlopeScript can spin unboundedly."""
        if self.deadline is not None and time.monotonic() > self.deadline:
            raise SlopeTimeout()

    def credit_wait(self, seconds: float):
        """Push the deadline forward to exclude time the interpreter spent
        blocked (e.g. waiting for chairlift input) from the compute budget."""
        if self.deadline is not None:
            self.deadline += seconds

    # -- statements ---------------------------------------------------------

    def run(self, statements: List[Tuple], env: Optional[Environment] = None):
        env = env or self.globals
        for stmt in statements:
            self.execute(stmt, env)

    def execute(self, stmt: Tuple, env: Environment):
        kind = stmt[0]

        if kind == 'pack':
            _, name, expr, line = stmt
            env.declare(name, self.evaluate(expr, env))

        elif kind == 'assign':
            _, target, op, expr, line = stmt
            self.assign_target(target, op, self.evaluate(expr, env), env, line)

        elif kind == 'carve':
            _, exprs, line = stmt
            print(' '.join(format_value(self.evaluate(e, env)) for e in exprs))

        elif kind == 'cond':
            _, branches, line = stmt
            for condition, body in branches:
                if condition is None or is_truthy(self.evaluate(condition, env)):
                    self.run(body, env)
                    break

        elif kind == 'gondola':
            _, condition, body, line = stmt
            while is_truthy(self.evaluate(condition, env)):
                self._tick()
                try:
                    self.run(body, env)
                except BailSignal:
                    break
                except SendItSignal:
                    continue

        elif kind == 'liftline':
            _, var, iterable_expr, body, line = stmt
            iterable = self.evaluate(iterable_expr, env)
            items = self.iterate(iterable, line)
            env.declare(var, None)
            for item in items:
                self._tick()
                env.declare(var, item)
                try:
                    self.run(body, env)
                except BailSignal:
                    break
                except SendItSignal:
                    continue

        elif kind == 'trick':
            _, name, params, body, line = stmt
            env.declare(name, Trick(name, params, body, env))

        elif kind == 'stomp':
            _, expr, line = stmt
            if self.trick_depth == 0:
                raise SlopeRuntimeError("stomp outside a trick — there is nothing to land", line)
            value = self.evaluate(expr, env) if expr is not None else None
            raise StompSignal(value, line)

        elif kind == 'bail':
            raise BailSignal(stmt[1])

        elif kind == 'sendit':
            raise SendItSignal(stmt[1])

        elif kind == 'patrol':
            _, body, err_name, handler, line = stmt
            try:
                self.run(body, env)
            except AvalancheError as e:
                env.declare(err_name, e.value)
                self.run(handler, env)
            except LiftsClosedError:
                raise
            except SlopeRuntimeError as e:
                env.declare(err_name, e.message)
                self.run(handler, env)

        elif kind == 'avalanche':
            _, expr, line = stmt
            raise AvalancheError(self.evaluate(expr, env), line)

        elif kind == 'traverse':
            _, expr, line = stmt
            path = self.evaluate(expr, env)
            if not isinstance(path, str):
                raise SlopeRuntimeError(f"traverse needs a file path as text, not {type_name(path)}", line)
            self.traverse(path, line)

        elif kind == 'expr':
            self.evaluate(stmt[1], env)

        else:  # pragma: no cover
            raise SlopeRuntimeError(f"Unknown statement: {kind}", stmt[-1])

    def traverse(self, path: str, line: int):
        """Load another .slope file into this program (import). The file runs
        once in the global scope; repeat traverses are no-ops."""
        base = self.dir_stack[-1] if self.dir_stack else os.getcwd()
        full = os.path.abspath(os.path.join(base, path))
        if not os.path.isfile(full) and os.path.isfile(full + '.slope'):
            full = full + '.slope'
        if full in self.loaded_trails:
            return
        if full in self.loading_trails:
            raise SlopeRuntimeError(f"Traverse loop! '{path}' is already being traversed — "
                                    "two trails can't each lead to the other", line)
        try:
            with open(full, 'r', encoding='utf-8') as f:
                source = f.read()
        except OSError as e:
            raise SlopeRuntimeError(f"Can't traverse to '{path}': {e.strerror or 'trail not found'}", line)
        self.loading_trails.add(full)
        self.dir_stack.append(os.path.dirname(full))
        try:
            ast = compile_source(source, snippet=True)
            self.run(ast, self.globals)
        except SlopeError as e:
            if '(while traversing' not in e.message:
                e.message = f"{e.message} (while traversing {path})"
                e.args = (e.message,)
            raise
        finally:
            self.dir_stack.pop()
            self.loading_trails.discard(full)
        self.loaded_trails.add(full)

    def iterate(self, iterable: Any, line: int) -> List[Any]:
        if isinstance(iterable, list):
            return list(iterable)
        if isinstance(iterable, str):
            return list(iterable)
        if isinstance(iterable, dict):
            return list(iterable.keys())
        if isinstance(iterable, (int, float)):
            raise SlopeRuntimeError("Can't ride a liftline through a number — "
                                    "use laps(n) to make a rack of numbers", line)
        raise SlopeRuntimeError(f"Can't ride a liftline through {type_name(iterable)}", line)

    def assign_target(self, target: Tuple, op: str, value: Any, env: Environment, line: int):
        if op != '=':
            current = self.evaluate(target, env)
            value = self.binary_op(op[0], current, value, line)
        kind = target[0]
        if kind == 'var':
            env.assign(target[1], value, line)
        elif kind == 'index':
            container = self.evaluate(target[1], env)
            index = self.evaluate(target[2], env)
            self.set_item(container, index, value, line)
        elif kind == 'member':
            container = self.evaluate(target[1], env)
            if not isinstance(container, dict):
                raise SlopeRuntimeError(f"Can't set .{target[2]} on {type_name(container)} — "
                                        "dot assignment works on lockers", line)
            container[target[2]] = value
        else:  # pragma: no cover
            raise SlopeRuntimeError("Invalid assignment target", line)

    def set_item(self, container: Any, index: Any, value: Any, line: int):
        if isinstance(container, list):
            if isinstance(index, bool) or not isinstance(index, int):
                raise SlopeRuntimeError(f"Rack positions must be whole numbers, not {type_name(index)}", line)
            try:
                container[index] = value
            except IndexError:
                raise SlopeRuntimeError(f"Rack position {index} is off the edge "
                                        f"(the rack holds {len(container)} items)", line)
        elif isinstance(container, dict):
            container[index] = value
        elif isinstance(container, str):
            raise SlopeRuntimeError("Text can't be changed in place — build new text instead", line)
        else:
            raise SlopeRuntimeError(f"Can't store into {type_name(container)}", line)

    # -- expressions --------------------------------------------------------

    def evaluate(self, expr: Tuple, env: Environment) -> Any:
        kind = expr[0]

        if kind == 'lit':
            return expr[1]

        if kind == 'var':
            name = expr[1]
            scope: Optional[Environment] = env
            while scope is not None:
                if name in scope.vars:
                    return scope.vars[name]
                scope = scope.parent
            ref = BUILTINS.get(name)
            if ref is not None:
                return ref
            raise SlopeRuntimeError(f"'{name}' is not packed — pack it first, like: pack {name} = ...",
                                    expr[2])

        if kind == 'bin':
            op = expr[1]
            if op == '&&':
                left = self.evaluate(expr[2], env)
                return self.evaluate(expr[3], env) if is_truthy(left) else left
            if op == '||':
                left = self.evaluate(expr[2], env)
                return left if is_truthy(left) else self.evaluate(expr[3], env)
            return self.binary_op(op, self.evaluate(expr[2], env),
                                  self.evaluate(expr[3], env), expr[4])

        if kind == 'call':
            return self.call(expr[1], expr[2], env, expr[3])

        if kind == 'interp':
            pieces: List[str] = []
            for part in expr[1]:
                if part[0] == 't':
                    pieces.append(part[1])
                else:
                    pieces.append(format_value(self.evaluate(part[1], env)))
            return ''.join(pieces)

        if kind == 'trickexpr':
            _, params, body, line = expr
            return Trick('(anonymous)', params, body, env)

        if kind == 'rack':
            return [self.evaluate(e, env) for e in expr[1]]

        if kind == 'locker':
            return {key: self.evaluate(value, env) for key, value in expr[1]}

        if kind == 'index':
            _, base, index_expr, line = expr
            container = self.evaluate(base, env)
            index = self.evaluate(index_expr, env)
            return self.get_item(container, index, line)

        if kind == 'member':
            _, base, name, line = expr
            container = self.evaluate(base, env)
            if isinstance(container, dict):
                if name in container:
                    return container[name]
                raise SlopeRuntimeError(f"This locker has no '{name}' — "
                                        f"it holds {format_value(list(container.keys()))}", line)
            raise SlopeRuntimeError(f"Can't look up .{name} on {type_name(container)}", line)

        if kind == 'callexpr':
            _, base, arg_exprs, line = expr
            callee = self.evaluate(base, env)
            args = [self.evaluate(a, env) for a in arg_exprs]
            return self.call_value(callee, args, line)

        if kind == 'un':
            _, op, operand_expr, line = expr
            operand = self.evaluate(operand_expr, env)
            if op == '!':
                return not is_truthy(operand)
            if op == '-':
                if isinstance(operand, bool) or not isinstance(operand, (int, float)):
                    raise SlopeRuntimeError(f"Can't negate {type_name(operand)}", line)
                return -operand
        raise SlopeRuntimeError(f"Unknown expression: {kind}")  # pragma: no cover

    def get_item(self, container: Any, index: Any, line: int) -> Any:
        if isinstance(container, (list, str)):
            if isinstance(index, bool) or not isinstance(index, int):
                what = 'Rack' if isinstance(container, list) else 'Text'
                raise SlopeRuntimeError(f"{what} positions must be whole numbers, not {type_name(index)}", line)
            try:
                return container[index]
            except IndexError:
                what = 'rack' if isinstance(container, list) else 'text'
                raise SlopeRuntimeError(f"Position {index} is off the edge of the {what} "
                                        f"(it holds {len(container)} items)", line)
        if isinstance(container, dict):
            if index in container:
                return container[index]
            raise SlopeRuntimeError(f"This locker has no {format_inner(index)} — "
                                    f"it holds {format_value(list(container.keys()))}", line)
        raise SlopeRuntimeError(f"Can't index into {type_name(container)}", line)

    def call(self, name: str, arg_exprs: List[Tuple], env: Environment, line: int) -> Any:
        evaluate = self.evaluate
        args = [evaluate(a, env) for a in arg_exprs]

        # User-defined tricks shadow builtins.
        lookup: Optional[Environment] = env
        while lookup is not None:
            if name in lookup.vars:
                target = lookup.vars[name]
                if type(target) is Trick:
                    return self.call_trick(target, args, line)
                if type(target) is BuiltinRef:
                    return self.call_value(target, args, line)
                raise SlopeRuntimeError(f"'{name}' is {type_name(target)}, not a trick — "
                                        "it can't be called", line)
            lookup = lookup.parent

        target = BUILTINS.get(name)
        if target is None:
            raise SlopeRuntimeError(f"Unknown trick '{name}' — define it with: "
                                    f"trick {name}(...) ... nail", line)
        return self.call_value(target, args, line)

    def call_value(self, callee: Any, args: List[Any], line: int) -> Any:
        if isinstance(callee, Trick):
            return self.call_trick(callee, args, line)
        if isinstance(callee, BuiltinRef):
            min_args, max_args = callee.min_args, callee.max_args
            if len(args) < min_args or (max_args is not None and len(args) > max_args):
                if max_args == min_args:
                    expected = str(min_args)
                elif max_args is None:
                    expected = f"at least {min_args}"
                else:
                    expected = f"{min_args} to {max_args}"
                raise SlopeRuntimeError(f"{callee.name}() takes {expected} argument(s), got {len(args)}", line)
            return callee.fn(args, line, self)
        raise SlopeRuntimeError(f"Can't call {type_name(callee)} — only tricks can be called", line)

    def call_trick(self, trick: Trick, args: List[Any], line: int) -> Any:
        if len(args) != len(trick.params):
            raise SlopeRuntimeError(
                f"Trick '{trick.name}' takes {len(trick.params)} argument(s) "
                f"({', '.join(trick.params) or 'none'}), got {len(args)}", line)
        if self.trick_depth >= MAX_TRICK_DEPTH:
            raise SlopeRuntimeError(f"Avalanche risk! Trick '{trick.name}' recursed more than "
                                    f"{MAX_TRICK_DEPTH} times", line)
        local = Environment(parent=trick.closure)
        for param, arg in zip(trick.params, args):
            local.declare(param, arg)
        self.trick_depth += 1
        try:
            self.run(trick.body, local)
        except StompSignal as s:
            return s.value
        finally:
            self.trick_depth -= 1
        return None

    def binary_op(self, op: str, left: Any, right: Any, line: int) -> Any:
        # Fast path: pure number math. type() checks exclude bool (which is a
        # subclass of int) so powder/ice never sneak into arithmetic.
        lt = type(left)
        if (lt is int or lt is float):
            rt = type(right)
            if (rt is int or rt is float):
                if op == '+':
                    return left + right
                if op == '-':
                    return left - right
                if op == '<':
                    return left < right
                if op == '>':
                    return left > right
                if op == '<=':
                    return left <= right
                if op == '>=':
                    return left >= right
                if op == '==':
                    return left == right
                if op == '!=':
                    return left != right
                if op == '*':
                    return left * right
                if op == '/':
                    if right == 0:
                        raise SlopeRuntimeError("Yard sale! Division by zero", line)
                    result = left / right
                    return _normalize_number(result) if lt is int and rt is int else result
                if op == '%':
                    if right == 0:
                        raise SlopeRuntimeError("Yard sale! Modulo by zero", line)
                    return left % right
        if op == '+':
            if isinstance(left, str) or isinstance(right, str):
                return (left if isinstance(left, str) else format_value(left)) + \
                       (right if isinstance(right, str) else format_value(right))
            if isinstance(left, list) and isinstance(right, list):
                return left + right
            if self.both_numbers(left, right):
                return left + right
            raise SlopeRuntimeError(f"Can't add {type_name(left)} and {type_name(right)}", line)
        if op == '-':
            if self.both_numbers(left, right):
                return left - right
            raise SlopeRuntimeError(f"Can't subtract {type_name(right)} from {type_name(left)}", line)
        if op == '*':
            if self.both_numbers(left, right):
                return left * right
            if isinstance(left, str) and isinstance(right, int) and not isinstance(right, bool):
                return left * right
            if isinstance(left, int) and not isinstance(left, bool) and isinstance(right, str):
                return left * right
            raise SlopeRuntimeError(f"Can't multiply {type_name(left)} by {type_name(right)}", line)
        if op == '/':
            if self.both_numbers(left, right):
                if right == 0:
                    raise SlopeRuntimeError("Yard sale! Division by zero", line)
                result = left / right
                return _normalize_number(result) if isinstance(left, int) and isinstance(right, int) else result
            raise SlopeRuntimeError(f"Can't divide {type_name(left)} by {type_name(right)}", line)
        if op == '%':
            if self.both_numbers(left, right):
                if right == 0:
                    raise SlopeRuntimeError("Yard sale! Modulo by zero", line)
                return left % right
            raise SlopeRuntimeError(f"Can't take {type_name(left)} modulo {type_name(right)}", line)
        if op == '**':
            if self.both_numbers(left, right):
                try:
                    return left ** right
                except (OverflowError, ZeroDivisionError):
                    raise SlopeRuntimeError("That jump was too big (power overflow)", line)
            raise SlopeRuntimeError(f"Can't raise {type_name(left)} to {type_name(right)}", line)
        if op == '==':
            return self.values_equal(left, right)
        if op == '!=':
            return not self.values_equal(left, right)
        if op in ('<', '>', '<=', '>='):
            if self.both_numbers(left, right) or (isinstance(left, str) and isinstance(right, str)):
                if op == '<':
                    return left < right
                if op == '>':
                    return left > right
                if op == '<=':
                    return left <= right
                return left >= right
            raise SlopeRuntimeError(f"Can't compare {type_name(left)} with {type_name(right)} — "
                                    "compare numbers with numbers, text with text", line)
        if op == 'in':
            if isinstance(right, (list, dict)):
                return left in right
            if isinstance(right, str):
                if not isinstance(left, str):
                    raise SlopeRuntimeError(f"Can't look for {type_name(left)} inside text", line)
                return left in right
            raise SlopeRuntimeError(f"'in' needs a rack, text, or locker on the right, "
                                    f"not {type_name(right)}", line)
        raise SlopeRuntimeError(f"Unknown operator '{op}'", line)  # pragma: no cover

    @staticmethod
    def both_numbers(left: Any, right: Any) -> bool:
        return (isinstance(left, (int, float)) and not isinstance(left, bool)
                and isinstance(right, (int, float)) and not isinstance(right, bool))

    @staticmethod
    def values_equal(left: Any, right: Any) -> bool:
        if isinstance(left, bool) != isinstance(right, bool):
            return False
        return left == right


# ---------------------------------------------------------------------------
# Running programs
# ---------------------------------------------------------------------------

def compile_source(code: str, snippet: bool = False) -> List[Tuple]:
    tokens = Lexer(code).tokenize()
    parser = Parser(tokens)
    return parser.parse_snippet() if snippet else parser.parse_program()


def run_source(code: str, interpreter: Optional[Interpreter] = None, snippet: bool = False,
               base_dir: Optional[str] = None):
    """Parse and execute SlopeScript source. Raises SlopeError on failure."""
    interp = interpreter or Interpreter()
    if base_dir and not interp.dir_stack:
        interp.dir_stack.append(base_dir)
    ast = compile_source(code, snippet=snippet)
    try:
        interp.run(ast)
    except BailSignal as s:
        raise SlopeRuntimeError("bail outside a loop — there is nothing to bail from", s.line)
    except SendItSignal as s:
        raise SlopeRuntimeError("sendIt outside a loop — there is nothing to send", s.line)
    except StompSignal as s:
        raise SlopeRuntimeError("stomp outside a trick — there is nothing to land", s.line)
    return interp


# Backwards-compatible alias for the v1 API.
def run_slopescript(code: str):
    try:
        run_source(code)
    except SlopeError as e:
        print(report_error(e), file=sys.stderr)
        sys.exit(1)


def report_error(err: SlopeError, filename: Optional[str] = None) -> str:
    where = ''
    if err.line is not None:
        where = f"line {err.line}"
        if filename:
            where = f"{filename}, {where}"
        where = f" ({where})"
    if isinstance(err, SlopeSyntaxError):
        return f"🚧 Trail closed{where}: {err.message}"
    if isinstance(err, AvalancheError):
        return f"🌨️  Avalanche{where}: {err.message}\n⛑️  No patroller caught it — wrap risky code in patrol ... patroller (whoops) ... runout"
    return f"⛑️  Ski Patrol Report{where}: {err.message}"


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

REPL_BANNER = f"""\
🏔️  SlopeScript {VERSION} — fresh corduroy, no waiting.
    Type any statement or expression. Blocks stay open until you close them
    with runout (or nail). Type 'apres' or press Ctrl-D to head home.
"""


def snippet_depth(code: str) -> int:
    """How many blocks are still open (for multi-line REPL input)."""
    try:
        tokens = Lexer(code).tokenize()
    except SlopeSyntaxError:
        return 0  # let execution surface the error
    depth = 0
    for tok in tokens:
        if tok.type in BLOCK_OPENERS or tok.type == 'SUMMIT':
            depth += 1
        elif tok.type in ('RUNOUT', 'LODGE'):
            depth -= 1
    return depth


def repl():  # pragma: no cover — interactive
    print(REPL_BANNER)
    interp = Interpreter()
    buffer: List[str] = []
    while True:
        prompt = '⛷️  ' if not buffer else '··· '
        try:
            line = input(prompt)
        except EOFError:
            print("\n🌙 Last run of the day. See you at first chair!")
            return
        except KeyboardInterrupt:
            print("\n(hockey stop — input cleared)")
            buffer = []
            continue
        if not buffer and line.strip() in ('apres', 'exit', 'quit'):
            print("🌙 Last run of the day. See you at first chair!")
            return
        buffer.append(line)
        code = '\n'.join(buffer)
        if not code.strip():
            buffer = []
            continue
        if snippet_depth(code) > 0:
            continue
        buffer = []
        try:
            # If the input is a single expression, evaluate and echo it.
            try:
                expr = Parser(Lexer(code).tokenize()).parse_expression_only()
            except SlopeSyntaxError:
                expr = None
            if expr is not None:
                value = interp.evaluate(expr, interp.globals)
                if value is not None:
                    print(format_value(value))
            else:
                run_snippet(code, interp)
        except SlopeError as e:
            print(report_error(e))
        except KeyboardInterrupt:
            print("\n(hockey stop)")


def run_snippet(code: str, interp: Interpreter):
    ast = compile_source(code, snippet=True)
    try:
        interp.run(ast)
    except BailSignal:
        raise SlopeRuntimeError("bail outside a loop — there is nothing to bail from")
    except SendItSignal:
        raise SlopeRuntimeError("sendIt outside a loop — there is nothing to send")
    except StompSignal:
        raise SlopeRuntimeError("stomp outside a trick — there is nothing to land")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

USAGE = f"""\
🎿 SlopeScript {VERSION}

Usage:
  slope <program.slope>     run a program
  slope run <program.slope> same thing, more explicit
  slope                     start the interactive REPL
  slope --version           print the version
  slope --help              this message

Docs & examples: https://github.com/arnavj/slopescript
"""


def main(argv: Optional[List[str]] = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if not args:
        if sys.stdin.isatty():
            repl()
            return 0
        # Piped input: run it as a program.
        source = sys.stdin.read()
        return run_file_source(source, '<stdin>')

    if args[0] in ('--help', '-h', 'help'):
        print(USAGE)
        return 0
    if args[0] in ('--version', '-v', 'version'):
        print(f"SlopeScript {VERSION}")
        return 0
    if args[0] == 'repl':
        repl()
        return 0
    if args[0] == 'run':
        args = args[1:]
        if not args:
            print("🚧 'slope run' needs a file, like: slope run examples/hello.slope", file=sys.stderr)
            return 2

    filename = args[0]
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"🚧 Trail not found: {filename}", file=sys.stderr)
        return 2
    except IsADirectoryError:
        print(f"🚧 {filename} is a whole mountain (directory), not a trail (file)", file=sys.stderr)
        return 2
    return run_file_source(source, filename)


def run_file_source(source: str, filename: str) -> int:
    base_dir = None
    if filename not in ('<stdin>',):
        base_dir = os.path.dirname(os.path.abspath(filename))
    try:
        run_source(source, base_dir=base_dir)
        return 0
    except SlopeError as e:
        print(report_error(e, filename), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n(hockey stop)", file=sys.stderr)
        return 130
    except BrokenPipeError:
        try:
            sys.stdout.close()
        except Exception:
            pass
        return 141
    except RecursionError:
        print("⛑️  Ski Patrol Report: the program went too deep — avalanche risk", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
