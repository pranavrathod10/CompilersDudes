from dataclasses import dataclass
from fractions import Fraction

from typing import Union, Mapping,  Optional  #Union is used to specify that a variable can have one of several types and Mapping is a type hint for dictionaries or mappings.
from typing import List



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
class LetMut:
    var: 'AST'
    e1: 'AST'
    e2: 'AST'

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
    var:'AST'  
    expr: 'AST' 


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

AST = NumLiteral | BinOp | Variable | Let | if_else | LetMut | Put | Get |Seq | Print | while_loop    
        raise KeyError()
    

AST = NumLiteral | BinOp | Variable | Let | if_else | LetMut | Put | Get | Assign |Seq | Print | while_loop | FunCall | StringLiteral | UBoolOp



# The AST type is defined as a union of several classes, including NumLiteral, BinOp, Variable, Let, and If_else.



Value = Fraction | bool | str


# The InvalidProgram exception is defined. This exception will be raised when an invalid program is encountered during evaluation.
class InvalidProgram(Exception):
    pass

# environment is a mapping of variable names to their values and is used to keep track of the state of the program during evaluation. 
# The function returns the final value of the program.

# Type check
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



#typecheck


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
        
        case for_loop(Variable(name),e1,condition,updt,body):
            if environment.check(name):
                environment.update(name,eval_(e1))
                
            else:
               environment.add(name,eval_(e1))
            
            v2=eval_(condition)
            if v2 == True:
                eval_(body)
                e2=eval_(updt)
                eval_(for_loop(name,e2,condition,updt,body))

            return None


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
        
        # case FnObject(params,body):
        #     for par in params:
        #         if(par is )
        case FunCall(Variable(name),args):
            fn=environment.get(name)
            argv=[]
            for arg in args:
                argv.append(eval_(arg))
            environment.enter_scope()
            for par,arg in zip(fn.params,argv):
                environment.add(par,arg)
            v=eval_(fn.body)
            environment.exit_scope()
            return v
            
        case UBoolOp(Variable(name),expr):
            v2=eval_(expr)
            z=NumLiteral(10)
            print("name: ",environment.check(name))
            if environment.check(name):
                v1=environment.get(name)
                print("v1",v2.type)
                print("typecheck: ", typecheck(NumLiteral(5)))
                if typecheck(NumLiteral(5)).type==NumType():
                    if v1 !=0:
                        print("yes")
                        return True
                    else:
                        return False
                elif typecheck(NumLiteral(5)).type==StringType():
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
            v1 = eval_(condition)
            
            if v1 == True:
                eval_(e1) 
                eval_(while_loop(condition,e1))
            
            return None

        case Print(e1):
            v1=eval_(e1)
            print(v1)
            return v1

    raise InvalidProgram()


def test_eval():
    e1 = NumLiteral(2)
    e2 = NumLiteral(7)
    e3 = NumLiteral(9)
    e4 = NumLiteral(5)
    e5 = BinOp("+", e2, e3)      
    e6 = BinOp("/", e5, e4)
    e7 = BinOp("*", e1, e6)
    assert eval(e7) == Fraction(32, 5)

def test_string_slicing():
    str1 = StringLiteral("abcdefg")
    start = NumLiteral(0)
    end = NumLiteral(4)
    expr = Str_slicing(str1,start,end)
    assert eval(expr) == 'abcd'


def test_let_eval():
    a  = Variable("a")
    e1 = NumLiteral(5)
    e2 = BinOp("+", a, a)
    e  = Let(a, e1, e2)
    assert eval(e) == 10
    e  = Let(a, e1, Let(a, e2, e2))
    assert eval(e) == 20
    e  = Let(a, e1, BinOp("+", a, Let(a, e2, e2)))
    assert eval(e) == 25
    e  = Let(a, e1, BinOp("+", Let(a, e2, e2), a))
    assert eval(e) == 25
    e3 = NumLiteral(6); 
    e  = BinOp("+", Let(a, e1, e2), Let(a, e3, e2))
    assert eval(e) == 22

def test_letmut():
    # a = Variable("a")
    b = Variable("b")
    e1 = LetMut(b, NumLiteral(2), Put(b, BinOp("+",Get(b), NumLiteral(1))))
    # e2 = LetMut(a, NumLiteral(1), Seq([e1, Get(a)]))
    assert eval(e1) == 3



def test_while_eval():
    a = Variable("a")
    e1=NumLiteral(10)
    e2 = LetMut(a, NumLiteral(2), while_loop(BinOp("<",Get(a),e1),Put(a, BinOp("+", Get(a), NumLiteral(2)))) )
    assert eval(e2)==None




def test_if_else_eval():
    e1=NumLiteral(10)
    e2=NumLiteral(5)
    e3=NumLiteral(6)
    e4=NumLiteral(6)
    e5=BinOp("*",e2,e1)
    e6=BinOp("*",e3,e4)
    e7=BinOp(">",e5,e6)
    e10=if_else(e7,e5,e6)
    assert eval(e10) == 50

def test_letmut_eg1():
    a=Variable("a")
    e1=NumLiteral(5)
    e2=LetMut(a,e1,Put(a,BinOp("+",Get(a),NumLiteral(6))))
    assert eval(e2)==11


def test_letmut_eg2():
    a=Variable("a")
    e1=NumLiteral(5)
    b=Variable("b")
    e2=NumLiteral(4)
    e3=Put(a,BinOp("+",Get(a),Get(b)))
    e4=Put(b,BinOp("+",Get(a),Get(b)))
    e5=LetMut(b,e2,Seq([e3,e4]))
    e6=LetMut(a,e1,Seq([e5,Get(a)]))
    assert eval(e6)==9


def test_while_eval():
    a = Variable("a")
    e1=NumLiteral(10)
    e2 = LetMut(a, NumLiteral(2), while_loop(BinOp("<",Get(a),e1),Put(a, BinOp("+", Get(a), NumLiteral(2)))) )
    print("hi",Print(a))
    assert eval(e2)==None

def test_for_eval():
    a = Variable("a")
    e1=NumLiteral(10)
    i=Variable("i")
    e2=NumLiteral(0)
    e3=Put(i,BinOp("+",Get(i),NumLiteral(1)))
    e4=Put(a,BinOp("+",Get(i),Get(a)))
    e5=LetMut(a,e1, for_loop(i,e2,BinOp(">",Get(i),e2),e3,e4))
    assert eval(e5)==None


def test_print():
    a=Variable("a")
    e1=NumLiteral(5)
    e2=LetMut(a,e1,Put(a,BinOp("+",Get(a),NumLiteral(6))))
    e3=Print(e2)
    assert eval(e3)==11

def test_str_concatenation():
    str1 = StringLiteral("ab")
    str2 = StringLiteral("cd")
    expr = Two_Str_concatenation(str1,str2)
    assert eval(expr) == 'abcd'



# print(test_eval())
# print(test_if_else_eval())
# print(test_let_eval())
# print(test_letmut_eg1())
# print(test_letmut_eg2())
# print(test_print())
# print(test_letmut())
# print(test_while_eval())

def test_Letfun():
    a=Variable('a')
    b=Variable('b')
    f=Variable('f')
    e=LetFun(f,[a,b],BinOp("+",a,b),FunCall(f,[NumLiteral(15),NumLiteral(2)]))
    assert eval(e)==17    

def test_LetAnd():
    a=Variable('a')
    b=Variable('b')
    e1=NumLiteral(5)
    e2=BinOp("+",a,NumLiteral(1))
    e3=BinOp("+",a,b)
    e4=LetMut(a,e1,LetAnd(a,NumLiteral(3),b,e2,e3)) 
    assert eval(e4)==9

def test_UBoolOp():
    a=Variable("a")
    e1=NumLiteral(5)
    e2=Assign(a,e1)
    e3=UBoolOp(a,e2)
    assert eval(e3)==True

print("test_eval(): ",test_eval())
print("test_if_else_eval(): ", test_if_else_eval())
print("test_let_eval(): ",test_let_eval())
print("test_letmut_eg1(): ",test_letmut_eg1())
print("test_letmut_eg2(): ",test_letmut_eg2())
print("test_print(): ",test_print())
print("test_letmut(): ",test_letmut())
print("test_while_eval(): ",test_while_eval())
print("test_for_eval(): ",test_for_eval())
# print("test_Letfun(): ",test_Letfun())
print("test_LetAnd(): ",test_LetAnd())
print("test_UBoolOp(): ",test_UBoolOp())

