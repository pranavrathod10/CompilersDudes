from fractions import Fraction
from dataclasses import dataclass
from typing import Optional, NewType
from typing import List


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


keywords = "if then else end while do done let is in letMut letAnd and seq anth put get printing ".split()
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
        return if_else(c, t, f)
    def parse_let(self):
        self.lexer.match(Keyword("let"))
        v=self.parse_expr()
        self.lexer.match(Keyword("is"))
        e=self.parse_expr()
        self.lexer.match(Keyword("in"))
        b=self.parse_expr()
        self.lexer.match(Keyword("end"))
        return Let(v,e,b)
    
    def parse_LetMut(self):
        self.lexer.match(Keyword("letMut"))
        v=self.parse_expr()
        self.lexer.match(Keyword("is"))
        e=self.parse_expr()
        self.lexer.match(Keyword("in"))
        b=self.parse_expr()
        self.lexer.match(Keyword("end"))
        return LetMut(v,e,b)
    
    def parse_LetAnd(self):
        self.lexer.match(Keyword("letAnd"))
        v1=self.parse_expr()
        self.lexer.match(Keyword("is"))
        e1=self.parse_expr()
        self.lexer.match(Keyword("and"))
        v2=self.parse_expr()
        self.lexer.match(Keyword("is"))
        e2=self.parse_expr()
        self.lexer.match(Keyword("in"))
        b=self.parse_expr()
        self.lexer.match(Keyword("end"))
        return LetAnd(v1,e1,v2,e2,b)
    
    def parse_Seq(self):
        self.lexer.match(Keyword("seq"))
        lst=[]
        e1=self.parse_expr()
        lst.append(e1)
        self.lexer.match(Keyword("anth"))
        e2=self.parse_expr()
        lst.append(e2)
        self.lexer.match(Keyword("end"))
        # print(" helloo ")
        # a=True
        # while a:
            
        #     e1=self.parse_expr()
        #     lst.append(e1)
        #     print(" helloo 123")
        #     self.lexer.match(Keyword(" "))
        #     if self.lexer.match(Keyword("end")):
        #         a=False
        return Seq(lst)

    def parse_put(self):
        self.lexer.match(Keyword("put"))
        v=self.parse_expr()
        self.lexer.match(Keyword("is"))
        e=self.parse_expr()
        self.lexer.match(Keyword("end"))
        return Put(v,e)
    
    def parse_get(self):
        self.lexer.match(Keyword("get"))
        v=self.parse_expr()
        return Get(v)
    
    def parse_printing(self):
        self.lexer.match(Keyword("printing"))
        v=self.parse_expr()
        self.lexer.match(Keyword("end"))
        return Print(v)
    
    def parse_while(self):
        self.lexer.match(Keyword("while"))
        c = self.parse_expr()
        self.lexer.match(Keyword("do"))
        b = self.parse_expr()
        self.lexer.match(Keyword("done"))
        return while_loop(c, b)

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
            case Keyword("let"):
                return self.parse_let()
            case Keyword("letMut"):
                return self.parse_LetMut()
            case Keyword("put"):
                return self.parse_put()
            case Keyword("get"):
                return self.parse_get()
            case Keyword("letAnd"):
                return self.parse_LetAnd()
            case Keyword("seq"):
                return self.parse_Seq()
            case Keyword("printing"):
                return self.parse_printing()
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
#  The _init_ method takes any number of arguments and passes them to the Fraction constructor to create a new Fraction object, which is then stored in the value field.
class NumLiteral:
    value: Fraction
    type: SimType = NumType()
    def __init__(self, *args):
        self.value = Fraction(*args)


@dataclass
class StringLiteral:
    word : str 
    type: SimType = StringType()

@dataclass
class Integer:
    value:int
    type:SimType=NumType()

@dataclass
# this is kind of binary operation
class BinOp:                      
    operator: str      # '+' is the operator in addition
    # below are kind of two no. to be added
    left: 'AST'
    right: 'AST'

    type: Optional[SimType] = None


@dataclass
class Variable:
    name: str


@dataclass
class StringLiteral:
    word : str 
    type: SimType = StringType()


@dataclass
class Let:
    var: 'AST'
    e1: 'AST'
    e2: 'AST'

@dataclass
class BoolLiteral:
    value: bool
    type: SimType = BoolType()


@dataclass
class if_else:
    expr: 'AST'
    et: 'AST'    #statement if expr is true
    ef: 'AST'    #statement if expr is false
    type: Optional[SimType] = None


@dataclass
class while_loop:
    condition: 'AST'
    body: 'AST'


@dataclass
class for_loop:
    var: 'AST'
    expr: 'AST'
    condition: 'AST'
    updt: 'AST'
    body: 'AST'


@dataclass
class Two_Str_concatenation:
    str1: 'AST'
    str2: 'AST'

@dataclass

class Str_slicing:
    str1: 'AST'
    start: 'AST'
    end: 'AST'


@dataclass
class LetMut:
    var: 'AST'
    e1: 'AST'
    e2: 'AST'


@dataclass
class Seq:
    body: List['AST']


@dataclass
class Put:
    var: 'AST'
    e1: 'AST'

@dataclass

class Assign:
    var: 'AST'
    e1: 'AST'

@dataclass

class Get:
    var: 'AST'

@dataclass
class Print:
    e1: 'AST'

@dataclass
class LetFun:
    name:'AST'
    params:List['AST']
    body:'AST'
    expr:'AST'

@dataclass
class FunCall:
    fn:'AST'
    args: List['AST']

@dataclass
class FnObject:
    params: List['AST']
    body: 'AST'

@dataclass
class LetAnd:
    var1:'AST'
    expr1: 'AST'
    var2:'AST'
    expr2:'AST'
    expr3:'AST'
@dataclass
class UBoolOp:
    expr: 'AST' 

AST = NumLiteral |BoolLiteral | StringLiteral | BinOp | Variable | Let | if_else | LetMut | Put | Get | Assign |Seq | Print | while_loop | FunCall | StringLiteral | UBoolOp | LetAnd
# TypedAST = NewType('TypedAST', AST)
class InvalidProgram(Exception):
    pass

# new code start
Value = Fraction | bool | str


class Environment:
    env: List

    def __init__(self):
        self.env=[{}]

    def enter_scope(self):
        self.env.append({})

    def exit_scope(self):
        assert self.env
        self.env.pop()

    def add(self,name,value):
        assert name not in self.env[-1]
        self.env[-1][name]=value

    def check(self,name):
        for dict in reversed(self.env):
            if name in dict:
                return True
            else:
                return False
            
    def get(self,name):
        for dict in reversed(self.env):
            if name in dict:
                return dict[name]
        raise KeyError()
    
    def update(self,name,value):

        for dict in reversed(self.env):
            if name in dict:
                dict[name]=value
                return

        raise KeyError()


class TypeError(Exception):
    pass

def eval(program: AST, environment: Environment = None) -> Value:
    if environment is None:
        environment = Environment()

    def eval_(program):
        return eval(program, environment) 
       
    match program:
        case NumLiteral(value):
            return value
        case BoolLiteral(value):
            return value

        case StringLiteral(word):
            return word

        case Variable(name):
            return environment.get(name)
            
        case Put(Variable(name),e1): 
            environment.update(name,eval_(e1))
            return environment.get(name)
        
        case Get(Variable(name)):
            return environment.get(name)

        case Assign(Variable(name),e1):
            environment.add(name,eval_(e1))
            return name


        case Let(Variable(name), e1, e2) | LetMut(Variable(name),e1, e2):
            v1 = eval_(e1)
            environment.enter_scope()
            environment.add(name,v1)
            v2=eval_(e2)
            environment.exit_scope()
            return v2
        
        case Two_Str_concatenation(str1,str2):
            result_str = eval_(str1) + eval_(str2)
            return result_str

        case Str_slicing(str1,start,end):
            result_str = StringLiteral("")
            i = Variable("i")
            i = start
            body1 = LetMut(i,Get(i),BinOp("+",i,NumLiteral(1)))
            body2 = LetMut(result_str,Get(result_str),Two_Str_concatenation(result_str,str1[Get(i)]))
            body = Seq([body1,body2])
            condition = BinOp("<",i,end)
            eval_(while_loop(condition,body))
            return result_str


        case LetAnd(Variable(name1),expr1,Variable(name2),expr2,expr3):
            v1=eval_(expr1)
            v2=eval_(expr2)
            environment.enter_scope()
            if environment.check(name1):
                environment.update(name1,v1)
                
            else:
               environment.add(name1,v1)

            if environment.check(name2):
                environment.update(name2,v2)
                
            else:
               environment.add(name2,v2)
            
            v3=eval_(expr3)
            environment.exit_scope()
            return v3

        case LetFun(Variable(name),params, body,expr):
            environment.enter_scope()
            environment.add(name, FnObject(params,body))
            v=eval_(expr)
            environment.exit_scope()
            return v
        
        
        case FunCall(Variable(name),args):
            fn=environment.get(name)
            argv=[]
            for arg in args:
                argv.append(eval_(arg))
            environment.enter_scope()
            for par,arg in zip(fn.params,argv):
                environment.add(par.name,arg)
            v=eval_(fn.body)
            environment.exit_scope()
            return v
            
        case UBoolOp(expr):
            if typecheck(expr).type==NumType():
                    v1=eval_(expr)
                    if v1 !=0:
                        print("yes")
                        return True
                    else:
                        return False
            elif typecheck(expr).type==StringType():
                    v1=eval_(expr)
                    if v1 == "":
                        return False
                    else:
                        return True
            else:
                print("error")

        case Two_Str_concatenation(str1,str2):
            result_str = eval_(str1) + eval_(str2)
            return result_str
     

        case Seq(body):
            v1=None
            for item in body:
                v1=eval_(item)
            return v1    

        case BinOp("+", left, right):
            return eval_(left) + eval_(right)
        case BinOp("-", left, right):
            return eval_(left) - eval_(right)
        case BinOp("*", left, right):
            return eval_(left) * eval_(right)
        case BinOp("/", left, right):
            return eval_(left) / eval_(right)
        case BinOp(">",left,right):
            return eval_(left) > eval_(right)
        case BinOp("<", left,right):
            return eval_(left) < eval_(right)
        case BinOp("==", left,right):
            return eval_(left) == eval_(right)
        
        case if_else(expr,et,ef):
            v1 = eval_(expr)
            if v1 == True:
                return eval_(et)
            else:
                return eval_(ef)
                
        case while_loop(condition,e1):
            environment.enter_scope()
            vcond = eval_(condition)
            while(vcond):
                eval_(e1) 
                vcond=eval_(condition)
            environment.exit_scope()
            return None

        case for_loop(Variable(name),e1,condition,updt,body):
            environment.enter_scope()
            environment.add(name,eval_(e1))
            vcond=eval_(condition)
            while(vcond):
                eval_(body)
                eval_(updt)
                vcond=eval_(condition)    
            environment.exit_scope()
            return None
        
        case Print(e1):
            v1=eval_(e1)
            print(v1)
            return v1

    raise InvalidProgram()

#new code ends




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
        case if_else(c, t, f): # We have to typecheck both branches.
            tc = typecheck(c)
            if tc.type != BoolType():
                raise TypeError()
            tt = typecheck(t)
            tf = typecheck(f)
            if tt.type != tf.type: # Both branches must have the same type.
                raise TypeError()
            return if_else(tc, tt, tf, tt.type) # The common type becomes the type of the if-else.
    raise TypeError()

def test_typecheck():
    import pytest
    
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
    x=input()
    y=parse(x)
    print("y ",eval(y))
    # You should parse, evaluate and see whether the expression produces the expected value in your tests.
    # print(parse("if a+b > 2*d then a*b - c + d else e*f/g end"))
    # print(parse("if 10*5 > 6*6 then 10*5 else 6*6 end"))
    # print(" eval ")
    # b=parse("if 10*5 > 6*6 then 10*5 else 6*6 end")
    # print("b ",b)
    # print(eval(b))
    # c=parse("let a is 5 in let b is 7 in a+b end end ")
    # print("c ",c)
    # print(eval(c))
    # code1.eval(parse("if a+b > 2*d then a*b - c + d else e*f/g end"))

# test_parse() # Uncomment to see the created ASTs.
print("parse  ",test_parse())
# print(test_typecheck())