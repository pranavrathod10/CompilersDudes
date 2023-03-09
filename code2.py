from fractions import Fraction
from dataclasses import dataclass
from typing import Optional, NewType

# A minimal example to illustrate typechecking.

class EndOfStream(Exception):
    pass

@dataclass
# This defines a class named Stream, which will store information 
# about a character stream
class Stream:
    # Stream contains the string and positon
    source: str  
    # This is an instance variable of the class, which stores the string data of the stream.
    pos: int
    #  stores the current position in the stream.
    def from_string(s):
        return Stream(s, 0)
    # create stream object
    def next_char(self):
    #gets the next char from the stream
        if self.pos >= len(self.source):
            raise EndOfStream()
        self.pos = self.pos + 1
        return self.source[self.pos - 1]

    def unget(self):
    #  move the position of the stream back by one character
        assert self.pos > 0
        self.pos = self.pos - 1

# Define the token types.

@dataclass
class Num:
    n: int

@dataclass
class Bool:
    b: bool

@dataclass
class Keyword:
    word: str

@dataclass
class Identifier:
    word: str

@dataclass
class Operator:
    op: str

Token = Num | Bool | Keyword | Identifier | Operator

class EndOfTokens(Exception):
    pass


keywords = "if then else end while do done".split()
symbolic_operators = "+ - * / < > ≤ ≥ = ≠".split()
word_operators = "and or not quot rem".split()
whitespace = " \t\n"

def word_to_token(word):
    if word in keywords:
        return Keyword(word)
    if word in word_operators:
        return Operator(word)
    if word == "True":
        return Bool(True)
    if word == "False":
        return Bool(False)
    return Identifier(word)

class TokenError(Exception):
    pass

@dataclass
class Lexer:
    stream: Stream
    save: Token = None
    # an instance variable, named save of type Token with a default value of None.
    def from_stream(s):
        return Lexer(s)

    def next_token(self) -> Token:
        # returns the next token in the input stream
        try:
            match self.stream.next_char():
                case c if c in symbolic_operators: return Operator(c)
                case c if c.isdigit():
                    n = int(c)
                    while True:
                        try:
                            c = self.stream.next_char()
                            if c.isdigit():
                                n = n*10 + int(c)
                            else:
                                self.stream.unget()
                                return Num(n)
                        except EndOfStream:
                            return Num(n)
                case c if c.isalpha():
                    s = c
                    while True:
                        try:
                            c = self.stream.next_char()
                            if c.isalpha():
                                s = s + c
                            else:
                                self.stream.unget()
                                return word_to_token(s)
                        except EndOfStream:
                            return word_to_token(s)
                case c if c in whitespace:
                    return self.next_token()
        except EndOfStream:
            raise EndOfTokens

    def peek_token(self) -> Token:

# to look ahead in the stream to see the next token without 
# actually consuming it. 
        if self.save is not None:
            return self.save
        self.save = self.next_token()
        return self.save

    def advance(self):
        #  This method advances the stream to the next token.
        assert self.save is not None
        self.save = None

    def match(self, expected):
        # matches the current token with the expected token. 
        # If the current token matches the expected token,
        if self.peek_token() == expected:
            return self.advance()
        raise TokenError()

    def __iter__(self):
        #makes the Lexer class iterable
        # so you can use a for loop to iterate over the tokens.
        return self

    def __next__(self):
        # It calls next_token to get the next token
        try:
            return self.next_token()
        except EndOfTokens:
            raise StopIteration

@dataclass
class Parser:
    lexer: Lexer

    def from_lexer(lexer):
        return Parser(lexer)

    def parse_if(self):
        #The match method is called on the Lexer object to check that the 
        # next token in the stream
        self.lexer.match(Keyword("if"))
        c = self.parse_expr()
        self.lexer.match(Keyword("then"))
        t = self.parse_expr()
        self.lexer.match(Keyword("else"))
        f = self.parse_expr()
        self.lexer.match(Keyword("end"))
        return IfElse(c, t, f)

    def parse_while(self):
        self.lexer.match(Keyword("while"))
        c = self.parse_expr()
        self.lexer.match(Keyword("do"))
        b = self.parse_expr()
        self.lexer.match(Keyword("done"))
        return While(c, b)

    def parse_atom(self):
        # checks the type of the next token
        match self.lexer.peek_token():
            case Identifier(name):
                self.lexer.advance()
                return Variable(name)
            case Num(value):
                self.lexer.advance()
                return NumLiteral(value)
            case Bool(value):
                self.lexer.advance()
                return BoolLiteral(value)

    def parse_mult(self):
        left = self.parse_atom()
        while True:
            match self.lexer.peek_token():
                case Operator(op) if op in "*/":
                    self.lexer.advance()
                    m = self.parse_atom()
                    left = BinOp(op, left, m)
                case _:
                    break
        return left

    def parse_add(self):
        left = self.parse_mult()
        while True:
            match self.lexer.peek_token():
                case Operator(op) if op in "+-":
                    self.lexer.advance()
                    m = self.parse_mult()
                    left = BinOp(op, left, m)
                case _:
                    break
        return left

    def parse_cmp(self):
        left = self.parse_add()
        match self.lexer.peek_token():
            case Operator(op) if op in "<>":
                self.lexer.advance()
                right = self.parse_add()
                return BinOp(op, left, right)
        return left

    def parse_simple(self):
        return self.parse_cmp()

    def parse_expr(self):
        #which handles the different cases for a valid expression: 
        # if-else, while loop or 
        # simple expression (a combination of basic mathematical operations 
        # like addition, subtraction, multiplication, and division and comparison operations like less than, greater than).
        match self.lexer.peek_token():
            case Keyword("if"):
                return self.parse_if()
            case Keyword("while"):
                return self.parse_while()
            case _:
                return self.parse_simple()

@dataclass
class NumType:
    pass

@dataclass
class BoolType:
    pass
@dataclass
class StringType:
    pass

SimType = NumType | BoolType | StringType

@dataclass
class NumLiteral:
    value: Fraction
    type: SimType = NumType()

@dataclass
class BoolLiteral:
    value: bool
    type: SimType = BoolType()

@dataclass
class StringLiteral:
    value:bool
    type:SimType =StringType()

@dataclass
class BinOp:
    operator: str
    left: 'AST'
    right: 'AST'
    type: Optional[SimType] = None

@dataclass
class IfElse:
    condition: 'AST'
    iftrue: 'AST'
    iffalse: 'AST'
    type: Optional[SimType] = None

@dataclass
class While:
    condition: 'AST'
    body: 'AST'

@dataclass
class Variable:
    name: str



AST = NumLiteral | BoolLiteral | StringLiteral | BinOp | IfElse | While | Variable
# TypedAST = NewType('TypedAST', AST)


class TypeError(Exception):
    pass

# Since we don't have variables, environment is not needed.
def typecheck(program: AST, env = None) -> AST:
    match program:
        case NumLiteral() as t: # already typed.
            return t
        case BoolLiteral() as t: # already typed.
            return t
        case StringLiteral() as t:
            return t
        case BinOp(op, left, right) if op in "+*-/":
            tleft = typecheck(left)
            tright = typecheck(right)
            if tleft.type != NumType() or tright.type != NumType():
                raise TypeError()
            return BinOp(op, left, right, NumType())
        case BinOp("<", left, right):
            tleft = typecheck(left)
            tright = typecheck(right)
            if tleft.type != NumType() or tright.type != NumType():
                raise TypeError()
            return BinOp("<", left, right, BoolType())
        case BinOp("=", left, right):
            tleft = typecheck(left)
            tright = typecheck(right)
            if tleft.type != tright.type:
                raise TypeError()
            return BinOp("=", left, right, BoolType())
        case IfElse(c, t, f): # We have to typecheck both branches.
            tc = typecheck(c)
            if tc.type != BoolType():
                raise TypeError()
            tt = typecheck(t)
            tf = typecheck(f)
            if tt.type != tf.type: # Both branches must have the same type.
                raise TypeError()
            return IfElse(tc, tt, tf, tt.type) # The common type becomes the type of the if-else.
    raise TypeError()

def test_typecheck():
    import pytest
    t5=typecheck(a)
    print("t5: ",t5)
    te = typecheck(BinOp("+", NumLiteral(2), NumLiteral(3)))
    print("te: ",te)
    assert te.type == NumType()
    te = typecheck(BinOp("<", NumLiteral(2), NumLiteral(3)))
    print("te: ",te)
    assert te.type == BoolType()
    with pytest.raises(TypeError):
        typecheck(BinOp("+", BinOp("*", NumLiteral(2), NumLiteral(3)), BinOp("<", NumLiteral(2), NumLiteral(3))))

def test_parse():
    def parse(string):
        #First, the parse function creates a Stream object from the 
        # string argument and then creates a Lexer object from the Stream object.
        #The parse function then creates a Parser object from the Lexer object and calls the parse_expr method on the Parser object.
        return Parser.parse_expr (
            Parser.from_lexer(Lexer.from_stream(Stream.from_string(string)))
        )
    # You should parse, evaluate and see whether the expression produces the expected value in your tests.
    print(parse("if a+b > 2*d then a*b - c + d else e*f/g end"))

# test_parse() # Uncomment to see the created ASTs.
print(test_parse())
print(test_typecheck())