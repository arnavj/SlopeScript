#!/usr/bin/env python3
"""
SlopeScript Interpreter
A skiing-themed programming language interpreter
"""

import re
import sys
from typing import Any, Dict, List, Optional

class Token:
    def __init__(self, type: str, value: Any, line: int):
        self.type = type
        self.value = value
        self.line = line
    
    def __repr__(self):
        return f"Token({self.type}, {self.value}, line {self.line})"

class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.tokens = []
        
    def tokenize(self) -> List[Token]:
        while self.pos < len(self.code):
            self.skip_whitespace()
            if self.pos >= len(self.code):
                break
                
            # Skip comments
            if self.peek(2) == '//':
                self.skip_line_comment()
                continue
            if self.peek(2) == '/*':
                self.skip_block_comment()
                continue
            
            # Check for keywords and identifiers
            if self.current().isalpha() or self.current() == '_':
                self.read_identifier()
            # Numbers
            elif self.current().isdigit():
                self.read_number()
            # Strings
            elif self.current() == '"':
                self.read_string()
            # Operators and symbols
            else:
                self.read_operator()
        
        return self.tokens
    
    def current(self) -> str:
        if self.pos >= len(self.code):
            return '\0'
        return self.code[self.pos]
    
    def peek(self, n: int = 1) -> str:
        if self.pos + n > len(self.code):
            return '\0'
        return self.code[self.pos:self.pos + n]
    
    def advance(self, n: int = 1):
        for _ in range(n):
            if self.pos < len(self.code) and self.code[self.pos] == '\n':
                self.line += 1
            self.pos += 1
    
    def skip_whitespace(self):
        while self.current() in ' \t\r\n':
            self.advance()
    
    def skip_line_comment(self):
        while self.current() != '\n' and self.current() != '\0':
            self.advance()
    
    def skip_block_comment(self):
        self.advance(2)  # Skip /*
        while self.peek(2) != '*/' and self.current() != '\0':
            self.advance()
        self.advance(2)  # Skip */
    
    def read_identifier(self):
        start = self.pos
        while self.current().isalnum() or self.current() == '_':
            self.advance()
        
        value = self.code[start:self.pos]
        
        # Check if it's a keyword
        keywords = {
            'summit': 'SUMMIT',
            'lodge': 'LODGE',
            'pack': 'PACK',
            'carve': 'CARVE',
            'chairlift': 'CHAIRLIFT',
            'greenCircle': 'GREEN',
            'blueSquare': 'BLUE',
            'blackDiamond': 'BLACK',
            'gondola': 'GONDOLA',
            'liftline': 'LIFTLINE',
            'in': 'IN',
            'trick': 'TRICK',
            'nail': 'NAIL',
            'powder': 'TRUE',
            'ice': 'FALSE',
            'bail': 'BREAK',
            'sendIt': 'CONTINUE',
        }
        
        token_type = keywords.get(value, 'IDENTIFIER')
        token_value = True if token_type == 'TRUE' else (False if token_type == 'FALSE' else value)
        self.tokens.append(Token(token_type, token_value, self.line))
    
    def read_number(self):
        start = self.pos
        while self.current().isdigit() or self.current() == '.':
            self.advance()
        
        value = self.code[start:self.pos]
        num_value = float(value) if '.' in value else int(value)
        self.tokens.append(Token('NUMBER', num_value, self.line))
    
    def read_string(self):
        self.advance()  # Skip opening quote
        start = self.pos
        while self.current() != '"' and self.current() != '\0':
            self.advance()
        
        value = self.code[start:self.pos]
        self.advance()  # Skip closing quote
        self.tokens.append(Token('STRING', value, self.line))
    
    def read_operator(self):
        two_char_ops = {'==': 'EQ', '!=': 'NEQ', '<=': 'LTE', '>=': 'GTE', '&&': 'AND', '||': 'OR'}
        
        two_char = self.peek(2)
        if two_char in two_char_ops:
            self.tokens.append(Token(two_char_ops[two_char], two_char, self.line))
            self.advance(2)
            return
        
        char = self.current()
        ops = {
            '+': 'PLUS', '-': 'MINUS', '*': 'MULT', '/': 'DIV',
            '=': 'ASSIGN', '<': 'LT', '>': 'GT',
            '(': 'LPAREN', ')': 'RPAREN',
            '[': 'LBRACKET', ']': 'RBRACKET',
            ',': 'COMMA', '!': 'NOT'
        }
        
        if char in ops:
            self.tokens.append(Token(ops[char], char, self.line))
            self.advance()
        else:
            self.advance()  # Skip unknown character

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def parse(self) -> List[Any]:
        self.expect('SUMMIT')
        statements = []
        while not self.check('LODGE') and not self.is_at_end():
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        self.expect('LODGE')
        return statements
    
    def current(self) -> Optional[Token]:
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]
    
    def check(self, token_type: str) -> bool:
        token = self.current()
        return token and token.type == token_type
    
    def advance(self) -> Token:
        token = self.current()
        self.pos += 1
        return token
    
    def expect(self, token_type: str) -> Token:
        if not self.check(token_type):
            raise SyntaxError(f"Expected {token_type} but got {self.current()}")
        return self.advance()
    
    def is_at_end(self) -> bool:
        return self.pos >= len(self.tokens)
    
    def parse_statement(self):
        if self.check('PACK'):
            return self.parse_pack()
        elif self.check('CARVE'):
            return self.parse_carve()
        elif self.check('GREEN') or self.check('BLUE') or self.check('BLACK'):
            return self.parse_conditional()
        elif self.check('GONDOLA'):
            return self.parse_gondola()
        elif self.check('LIFTLINE'):
            return self.parse_liftline()
        elif self.check('BREAK'):
            self.advance()
            return ('break',)
        elif self.check('CONTINUE'):
            self.advance()
            return ('continue',)
        else:
            # Try parsing as expression statement (e.g., function call)
            expr = self.parse_expression()
            return ('expr', expr)
    
    def parse_pack(self):
        self.expect('PACK')
        name = self.expect('IDENTIFIER').value
        self.expect('ASSIGN')
        value = self.parse_expression()
        return ('pack', name, value)
    
    def parse_carve(self):
        self.expect('CARVE')
        value = self.parse_expression()
        return ('carve', value)
    
    def parse_conditional(self):
        branches = []
        
        while self.check('GREEN') or self.check('BLUE') or self.check('BLACK'):
            branch_type = self.advance().type
            
            # GREEN and BLUE have conditions, BLACK is else
            if branch_type in ('GREEN', 'BLUE'):
                self.expect('LPAREN')
                condition = self.parse_expression()
                self.expect('RPAREN')
            else:  # BLACK (else)
                condition = None
            
            # Parse block of statements until next branch
            body = []
            while not self.check('GREEN') and not self.check('BLUE') and not self.check('BLACK') and not self.check('GONDOLA') and not self.check('LIFTLINE') and not self.check('LODGE') and not self.is_at_end():
                stmt = self.parse_statement()
                if stmt:
                    body.append(stmt)
                else:
                    break
            
            branches.append((condition, body))
        
        return ('conditional', branches)
    
    def parse_gondola(self):
        self.expect('GONDOLA')
        self.expect('LPAREN')
        condition = self.parse_expression()
        self.expect('RPAREN')
        
        body = []
        while not self.check('GONDOLA') and not self.check('GREEN') and not self.check('BLUE') and not self.check('BLACK') and not self.check('LIFTLINE') and not self.check('LODGE') and not self.is_at_end():
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            else:
                break
        
        return ('gondola', condition, body)
    
    def parse_liftline(self):
        self.expect('LIFTLINE')
        var = self.expect('IDENTIFIER').value
        self.expect('IN')
        iterable = self.parse_expression()
        
        body = []
        while not self.check('GONDOLA') and not self.check('LIFTLINE') and not self.check('GREEN') and not self.check('BLUE') and not self.check('BLACK') and not self.check('LODGE') and not self.is_at_end():
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            else:
                break
        
        return ('liftline', var, iterable, body)
    
    def parse_expression(self):
        return self.parse_or()
    
    def parse_or(self):
        left = self.parse_and()
        while self.check('OR'):
            self.advance()
            right = self.parse_and()
            left = ('or', left, right)
        return left
    
    def parse_and(self):
        left = self.parse_equality()
        while self.check('AND'):
            self.advance()
            right = self.parse_equality()
            left = ('and', left, right)
        return left
    
    def parse_equality(self):
        left = self.parse_comparison()
        while self.check('EQ') or self.check('NEQ'):
            op = self.advance().type
            right = self.parse_comparison()
            left = (op.lower(), left, right)
        return left
    
    def parse_comparison(self):
        left = self.parse_addition()
        while self.check('LT') or self.check('GT') or self.check('LTE') or self.check('GTE'):
            op = self.advance().type
            right = self.parse_addition()
            left = (op.lower(), left, right)
        return left
    
    def parse_addition(self):
        left = self.parse_multiplication()
        while self.check('PLUS') or self.check('MINUS'):
            op = self.advance().type
            right = self.parse_multiplication()
            left = (op.lower(), left, right)
        return left
    
    def parse_multiplication(self):
        left = self.parse_unary()
        while self.check('MULT') or self.check('DIV'):
            op = self.advance().type
            right = self.parse_unary()
            left = (op.lower(), left, right)
        return left
    
    def parse_unary(self):
        if self.check('NOT') or self.check('MINUS'):
            op = self.advance().type
            expr = self.parse_unary()
            return (op.lower(), expr)
        return self.parse_primary()
    
    def parse_primary(self):
        if self.check('NUMBER'):
            return ('literal', self.advance().value)
        elif self.check('STRING'):
            return ('literal', self.advance().value)
        elif self.check('TRUE'):
            self.advance()
            return ('literal', True)
        elif self.check('FALSE'):
            self.advance()
            return ('literal', False)
        elif self.check('IDENTIFIER'):
            name = self.advance().value
            # Check for array access
            if self.check('LBRACKET'):
                self.advance()
                index = self.parse_expression()
                self.expect('RBRACKET')
                return ('index', name, index)
            return ('var', name)
        elif self.check('LPAREN'):
            self.advance()
            expr = self.parse_expression()
            self.expect('RPAREN')
            return expr
        elif self.check('LBRACKET'):
            return self.parse_array()
        elif self.check('CHAIRLIFT'):
            return self.parse_chairlift()
        else:
            raise SyntaxError(f"Unexpected token: {self.current()}")
    
    def parse_array(self):
        self.expect('LBRACKET')
        elements = []
        while not self.check('RBRACKET'):
            elements.append(self.parse_expression())
            if self.check('COMMA'):
                self.advance()
        self.expect('RBRACKET')
        return ('array', elements)
    
    def parse_chairlift(self):
        self.expect('CHAIRLIFT')
        self.expect('LPAREN')
        prompt = self.parse_expression()
        self.expect('RPAREN')
        return ('chairlift', prompt)

class Interpreter:
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.break_flag = False
        self.continue_flag = False
    
    def run(self, statements: List[Any]):
        for stmt in statements:
            self.execute(stmt)
            if self.break_flag or self.continue_flag:
                break
    
    def execute(self, stmt):
        if not stmt:
            return
        
        stmt_type = stmt[0]
        
        if stmt_type == 'pack':
            _, name, value_expr = stmt
            value = self.evaluate(value_expr)
            self.variables[name] = value
        
        elif stmt_type == 'carve':
            _, value_expr = stmt
            value = self.evaluate(value_expr)
            print(value)
        
        elif stmt_type == 'conditional':
            _, branches = stmt
            for condition, body in branches:
                if condition is None or self.evaluate(condition):
                    self.run(body)
                    break
        
        elif stmt_type == 'gondola':
            _, condition, body = stmt
            while self.evaluate(condition):
                self.run(body)
                if self.break_flag:
                    self.break_flag = False
                    break
                if self.continue_flag:
                    self.continue_flag = False
                    continue
        
        elif stmt_type == 'liftline':
            _, var, iterable_expr, body = stmt
            iterable = self.evaluate(iterable_expr)
            for item in iterable:
                self.variables[var] = item
                self.run(body)
                if self.break_flag:
                    self.break_flag = False
                    break
                if self.continue_flag:
                    self.continue_flag = False
                    continue
        
        elif stmt_type == 'break':
            self.break_flag = True
        
        elif stmt_type == 'continue':
            self.continue_flag = True
        
        elif stmt_type == 'expr':
            self.evaluate(stmt[1])
    
    def evaluate(self, expr) -> Any:
        if not expr:
            return None
        
        expr_type = expr[0]
        
        if expr_type == 'literal':
            return expr[1]
        
        elif expr_type == 'var':
            name = expr[1]
            if name not in self.variables:
                raise NameError(f"Variable '{name}' not defined")
            return self.variables[name]
        
        elif expr_type == 'array':
            return [self.evaluate(e) for e in expr[1]]
        
        elif expr_type == 'index':
            _, name, index_expr = expr
            if name not in self.variables:
                raise NameError(f"Variable '{name}' not defined")
            arr = self.variables[name]
            index = self.evaluate(index_expr)
            return arr[index]
        
        elif expr_type == 'chairlift':
            prompt = self.evaluate(expr[1])
            return input(str(prompt) + " ")
        
        elif expr_type == 'plus':
            return self.evaluate(expr[1]) + self.evaluate(expr[2])
        elif expr_type == 'minus':
            if len(expr) == 2:  # Unary minus
                return -self.evaluate(expr[1])
            return self.evaluate(expr[1]) - self.evaluate(expr[2])
        elif expr_type == 'mult':
            return self.evaluate(expr[1]) * self.evaluate(expr[2])
        elif expr_type == 'div':
            return self.evaluate(expr[1]) / self.evaluate(expr[2])
        
        elif expr_type == 'eq':
            return self.evaluate(expr[1]) == self.evaluate(expr[2])
        elif expr_type == 'neq':
            return self.evaluate(expr[1]) != self.evaluate(expr[2])
        elif expr_type == 'lt':
            return self.evaluate(expr[1]) < self.evaluate(expr[2])
        elif expr_type == 'gt':
            return self.evaluate(expr[1]) > self.evaluate(expr[2])
        elif expr_type == 'lte':
            return self.evaluate(expr[1]) <= self.evaluate(expr[2])
        elif expr_type == 'gte':
            return self.evaluate(expr[1]) >= self.evaluate(expr[2])
        
        elif expr_type == 'and':
            return self.evaluate(expr[1]) and self.evaluate(expr[2])
        elif expr_type == 'or':
            return self.evaluate(expr[1]) or self.evaluate(expr[2])
        elif expr_type == 'not':
            return not self.evaluate(expr[1])
        
        else:
            raise RuntimeError(f"Unknown expression type: {expr_type}")

def run_slopescript(code: str):
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        interpreter.run(ast)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python slopescript.py <file.slope>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    try:
        with open(filename, 'r') as f:
            code = f.read()
        run_slopescript(code)
    except FileNotFoundError:
        print(f"❌ File not found: {filename}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()