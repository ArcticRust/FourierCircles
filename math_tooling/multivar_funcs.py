# Small (quite inefficient) symbolic library to work with
from __future__ import annotations
from abc import ABC, abstractmethod
import math 
from .expr_types import *
from copy import deepcopy
from .error_classes import *

class Multiply(Expr):
    """
    Multiplies any number of expressions

    Parameters
    ----------
    *args : Expr
        Any number of sub-expressions to multiply
    """
    precedence = 2

    def eval(self, var_dict: dict[Var, float]):
        total = 1
        for sub_expr in self.sub_nodes:
            total *= sub_expr.eval(var_dict)
        return total

    def diff(self, var: Var):
        if len(self.sub_nodes) >= 2:
            terms = []
            for i in range(len(self.sub_nodes)):
                term = deepcopy(self.sub_nodes)
                term[i] = term[i].diff(var)
                terms.append(Multiply(*term))
            return Add(*terms)
        if len(self.sub_nodes) == 1:
            return self.sub_nodes[0].diff(var)

    def simplify(self):
        i = 0
        const_num = 0
        divided_terms = []
        init_len = len(self.sub_nodes)
        while i < len(self.sub_nodes):
            if i < init_len: # prevent multiple simplifications 
                self.sub_nodes[i] = self.sub_nodes[i].simplify()

            if isinstance(self.sub_nodes[i], Multiply):
                for multiply_subnode in self.sub_nodes[i].sub_nodes:
                    self.sub_nodes.append(multiply_subnode)
                self.sub_nodes.pop(i)
                i -= 1

            if isinstance(self.sub_nodes[i], Const):
                const_num += 1
                if self.sub_nodes[i].value == 0:
                    return Const(0)
                if self.sub_nodes[i].value == 1:
                    self.sub_nodes.pop(i)
                    if len(self.sub_nodes) == 0:
                        return Const(1)
                    const_num -= 1
                    init_len -= 1 # const removal does not impact simplifications
                    i -= 1

            if isinstance(self.sub_nodes[i], Divide):
                divided_terms.append(self.sub_nodes[i].sub_nodes[1])
                self.sub_nodes.append(self.sub_nodes[i].sub_nodes[0])
                self.sub_nodes.pop(i)
                i -= 1

            i += 1

        if const_num > 1:
            i = 0
            total = 1
            while i < len(self.sub_nodes):
                if isinstance(self.sub_nodes[i], Const):
                    total *= self.sub_nodes.pop(i).value
                    i -= 1
                i += 1
            return Multiply(Const(total), *self.sub_nodes).simplify() # probably should be reworked

        # comparison shenanigans to reduce number of .simplify() calls and make strings cleaner
        if len(self.sub_nodes) == 1:
            if len(divided_terms) == 0: return self.sub_nodes[0]
            if len(divided_terms) == 1: return Divide(self.sub_nodes[0], divided_terms[0])
            return Divide(self.sub_nodes[0], Multiply(*divided_terms))
        
        if len(divided_terms) == 0: return Multiply(*self.sub_nodes)
        if len(divided_terms) == 1: return Divide(Multiply(*self.sub_nodes), divided_terms[0])
        return Divide(Multiply(*self.sub_nodes), Multiply(*divided_terms))
        

    def __init__(self, *args):
        super().__init__(*args)
        assert len(self.sub_nodes) >= 1

    def __str__(self):
        output = ""
        for i, val in enumerate(self.sub_nodes):
            if i != 0:
                output += " * "
            
            takes_precedence = (val.precedence < self.precedence)
            if takes_precedence: output += TextColors.set_color("(", TextColors.CYAN)
            output += str(val)
            if takes_precedence: output += TextColors.set_color(")", TextColors.CYAN)

        return output

class Add(Expr):
    """
    Adds any number of expressions

    Parameters
    ----------
    *args : Expr
        Any number of sub-expressions to add
    """
    precedence = 1

    def eval(self, var_dict: dict[Var, float]):
        total = 0
        for sub_expr in self.sub_nodes:
            total += sub_expr.eval(var_dict)
        return total

    def diff(self, var: Var):
        return Add(*(child.diff(var) for child in self.sub_nodes))

    def simplify(self):
        i = 0
        while i < len(self.sub_nodes):
            self.sub_nodes[i] = self.sub_nodes[i].simplify()
            if isinstance(self.sub_nodes[i], Const):
                if self.sub_nodes[i].value == 0:
                    self.sub_nodes.pop(i)
                    i -= 1
                    if len(self.sub_nodes) == 0:
                        return Const(0)
            i += 1
        if len(self.sub_nodes) == 1:
            return self.sub_nodes[0]
        
        return Add(*self.sub_nodes)


    def __init__(self, *args):
        super().__init__(*args)
        assert len(self.sub_nodes) >= 1
    
    def __str__(self):
        output = ""
        for i, val in enumerate(self.sub_nodes):
            if i != 0:
                output += " + "
            output += str(val)
        return output

class Subtract(Binary):
    """
    Subtracts one expression from another

    Parameters
    ----------
    base_expr : Expr
        Expression to be subtracted from
    subtracted_expr : Expr
        Expression to be subtracted
    """
    precedence = 1

    def eval(self, var_dict: dict[Var, float]):
        return self.sub_nodes[0].eval(var_dict) - self.sub_nodes[1].eval(var_dict)

    def diff(self, var: Var):
        return Subtract(self.sub_nodes[0].diff(var), self.sub_nodes[1].diff(var))
    
    def simplify(self):
        self.sub_nodes[0] = self.sub_nodes[0].simplify()
        self.sub_nodes[1] = self.sub_nodes[1].simplify()
        if isinstance(self.sub_nodes[1], Const):
            if isinstance(self.sub_nodes[0], Const):
                return Const(self.sub_nodes[0].value - self.sub_nodes[1].value)
            if self.sub_nodes[1].value == 0:
                return self.sub_nodes[0]
        if isinstance(self.sub_nodes[0], Const):
            if self.sub_nodes[0].value == 0:
                return Multiply(Const(-1), self.sub_nodes[1])
        return Subtract(self.sub_nodes[0], self.sub_nodes[1])

    def __str__(self):
        return str(self.sub_nodes[0]) + " - " + str(self.sub_nodes[1])

    def __init__(self, base_expr: Expr, subtracted_expr: Expr):
        super().__init__(base_expr, subtracted_expr)
    
class Divide(Binary):
    """
    Divides one expression by another

    Parameters
    ----------
    numerator : Expr
        Numerator in division
    denominator : Expr
        Denominator in division
    """
    precedence = 2

    def eval(self, var_dict: dict[Var, float]):
        denominator = self.sub_nodes[1].eval(var_dict)
        if abs(denominator) == 0:
            raise ZeroDivisionError("YOU FOOL!!! YOU HAVE DIVIDED BY ZEERRROOOOOOO")
        return self.sub_nodes[0].eval(var_dict) / denominator

    def diff(self, var: Var):
        f = self.sub_nodes[0]
        g = self.sub_nodes[1]
        return Divide(Subtract(Multiply(f.diff(var), g), Multiply(f, g.diff(var))), Pow(g, Const(2)))

    def simplify(self):
        self.sub_nodes[0] = self.sub_nodes[0].simplify()
        self.sub_nodes[1] = self.sub_nodes[1].simplify()
        if isinstance(self.sub_nodes[0], Const):
            if self.sub_nodes[0].value == 0:
                return Const(0)
        return Divide(self.sub_nodes[0], self.sub_nodes[1])

    def __str__(self):
        p1 = self.sub_nodes[0].precedence
        p2 = self.sub_nodes[1].precedence

        output = ""
        if p1 <= self.precedence: output += TextColors.set_color("(", TextColors.BLUE)
        output += str(self.sub_nodes[0])
        if p1 <= self.precedence: output += TextColors.set_color(")", TextColors.BLUE)
        output += " / "

        if p2 <= self.precedence: output += TextColors.set_color("(", TextColors.BLUE)
        output += str(self.sub_nodes[1])
        if p2 <= self.precedence: output += TextColors.set_color(")", TextColors.BLUE)
        return output

    def __init__(self, numerator: Expr, denominator: Expr):
        super().__init__(numerator, denominator)

class Cos(Unary):
    """
    Takes cosine of argument

    Parameters
    ----------
    argument : Expr
        Expression to take cosine of
    """
    def eval(self, var_dict: dict[Var, float]):
        return math.cos(self.sub_nodes[0].eval(var_dict))
    
    def simplify(self):
        self.sub_nodes[0] = self.sub_nodes[0].simplify()
        if isinstance(self.sub_nodes[0], Const):
            if self.sub_nodes[0].value == 0:
                return Const(1)
        return Cos(self.sub_nodes[0])

    def diff(self, var: Var):
        return Multiply(self.sub_nodes[0].diff(var), Sin(self.sub_nodes[0]), Const(-1))

    def __str__(self):
        return TextColors.set_color("cos(", TextColors.MAGENTA) + str(self.sub_nodes[0]) + TextColors.set_color(")", TextColors.MAGENTA)

class Sin(Unary):
    """
    Takes sine of argument

    Parameters
    ----------
    argument : Expr
        Expression to take sine of
    """
    def eval(self, var_dict: dict[Var, float]):
        return math.sin(self.sub_nodes[0].eval(var_dict))
    
    def diff(self, var: Var):
        return Multiply(self.sub_nodes[0].diff(var), Cos(self.sub_nodes[0]))
    
    def simplify(self):
        self.sub_nodes[0] = self.sub_nodes[0].simplify()
        if isinstance(self.sub_nodes[0], Const):
            if self.sub_nodes[0].value == 0:
                return Const(0)
        return Sin(self.sub_nodes[0])

    def __str__(self):
        return TextColors.set_color("sin(", TextColors.MAGENTA) + str(self.sub_nodes[0]) + TextColors.set_color(")", TextColors.MAGENTA)

class Ln(Unary):
    """
    Takes natural logarithm of argument

    Parameters
    ----------
    argument : Expr
        Expression to take the natural logarithm of of
    """
    def eval(self, var_dict: dict[Var, float]):
        return math.log(self.sub_nodes[0].eval(var_dict))
    
    def diff(self, var: Var):
        return Divide(self.sub_nodes[0].diff(var), self.sub_nodes[0])

    def simplify(self):
        self.sub_nodes[0] = self.sub_nodes[0].simplify()
        if isinstance(self.sub_nodes[0], Const):
            if self.sub_nodes[0].value == 1:
                return Const(0)
        return Ln(self.sub_nodes[0])

    def __str__(self):
        return TextColors.set_color("ln(", TextColors.MAGENTA) + str(self.sub_nodes[0]) + TextColors.set_color(")", TextColors.MAGENTA)

class Pow(Binary):
    """
    Puts a base expression to the power of another expression

    Parameters
    ----------
    base : Expr
        Base of exponent
    
    power : Expr
        Power to put base to
    """
    precedence = 3
    def eval(self, var_dict: dict[Var, float]):
        return self.sub_nodes[0].eval(var_dict) ** self.sub_nodes[1].eval(var_dict)
    
    def diff(self, var: Var):
        f = self.sub_nodes[0]
        g = self.sub_nodes[1]
        return Multiply(Pow(f, g), Add(Multiply(g.diff(var), Ln(f)), Divide(Multiply(g, f.diff(var)), f)))

    def simplify(self):
        self.sub_nodes[0] = self.sub_nodes[0].simplify()
        self.sub_nodes[1] = self.sub_nodes[1].simplify()
        if isinstance(self.sub_nodes[0], Const):
            if (self.sub_nodes[0].value) == 1:
                return Const(1)
            if (self.sub_nodes[0].value) == 0:
                return Const(0)
        if isinstance(self.sub_nodes[1], Const):
            if (self.sub_nodes[1].value) == 1:
                return self.sub_nodes[0]
        return Pow(self.sub_nodes[0], self.sub_nodes[1])

    def __str__(self):
        p1 = self.sub_nodes[0].precedence
        p2 = self.sub_nodes[1].precedence

        output = ""
        if p1 <= self.precedence: output += TextColors.set_color("(", TextColors.RED)
        output += str(self.sub_nodes[0])
        if p1 <= self.precedence: output += TextColors.set_color(")", TextColors.RED)
        output += "^"

        if p2 <= self.precedence: output += TextColors.set_color("(", TextColors.RED)
        output += str(self.sub_nodes[1])
        if p2 <= self.precedence: output += TextColors.set_color(")", TextColors.RED)
        return output

class Tan(Unary):
    """
    Takes tangent of argument

    Parameters
    ----------
    argument : Expr
        Expression to take tangent of
    """
    def eval(self, var_dict: dict[Var, float]):
        return math.tan(self.sub_nodes[0].eval(var_dict))
    
    def diff(self, var: Var):
        return Multiply(self.sub_nodes[0].diff(var), Divide(Const(1), Pow(Cos(self.sub_nodes[0]), Const(2))))

    def simplify(self):
        self.sub_nodes[0] = self.sub_nodes[0].simplify()
        if isinstance(self.sub_nodes[0], Const):
            if self.sub_nodes[0].value == 0:
                return Const(0)
        return Tan(self.sub_nodes[0])

    def __str__(self):
        return TextColors.set_color("tan(", TextColors.MAGENTA) + str(self.sub_nodes[0]) + TextColors.set_color(")", TextColors.MAGENTA)

class Abs(Unary):
    """
    Takes absolute value of argument

    Parameters
    ----------
    argument : Expr
        Expression to take the absolute value of
    """
    def eval(self, var_dict: dict[Var, float]):
        return abs(self.sub_nodes[0].eval(var_dict))
    
    def diff(self, var: Var):
        f = self.sub_nodes[0]
        return Multiply(f.diff(var), Divide(f, Abs(f)))

    def simplify(self):
        self.sub_nodes[0] = self.sub_nodes[0].simplify()
        if isinstance(self.sub_nodes[0], Const):
            if self.sub_nodes[0].value == 0:
                return Const(0)
        return Abs(self.sub_nodes[0])

    def __str__(self):
        return TextColors.set_color("|", TextColors.MAGENTA) + str(self.sub_nodes[0]) + TextColors.set_color("|", TextColors.MAGENTA)
    
class Const(Unary):
    """
    A constant

    Parameters
    ----------
    value : float
        Value of constant
    """
    def eval(self, var_dict: dict[Var, float]):
        return self.sub_nodes[0]
    
    def diff(self, var: Var):
        return Const(0)

    def simplify(self):
        return Const(self.sub_nodes[0])

    def __str__(self):
        return str(self.sub_nodes[0])
    
    def __init__(self, value: float):
        super().__init__(value)
        self.value = value

class Var(Unary):
    """
    A variable. Variables are classified as different based on the string as input.
    It is recommended that you use the convention var_name = Var("var_name") when defining variables.

    Parameters
    ----------
    var_name : str
        Name of variable being used (Ex: "x", "y", "t")
    """
    precedence = 4

    def eval(self, var_dict: dict[Var, float]):
        if self not in var_dict:
            raise ValUndefinedError("The value of " + self.var_name + " is not provided in the dictionary")
        return var_dict[self]
    
    def diff(self, var: Var):
        if var.var_name == self.var_name:
            return Const(1)
        else:
            return Const(0)

    def simplify(self):
        return Var(self.var_name)

    def __init__(self, *args):
        super().__init__(*args) 
        assert isinstance(self.sub_nodes[0], str)
        self.var_name: str = self.sub_nodes[0]

    def __str__(self):
        return self.var_name
    
    def __eq__(self, value: Var):
        return self.var_name == value.var_name

    def __hash__(self):
        return hash(self.var_name)

    def get_var_dependencies(self):
        return {self}

class Re(Unary):
    """
    Takes the real part of a complex expression

    Parameters
    ----------
    argument : Expr
        Expression to take real part of
    """

    def eval(self, var_dict: dict[Var, float]):
        return self.sub_nodes[0].eval(var_dict).real

    def diff(self, var: Var):
        return Re(self.sub_nodes[0].diff())

    def simplify(self):
        return Re(self.sub_nodes[0].simplify())

    def __str__(self):
        return "Re(" + str(self.sub_nodes[0]) + ")"

class Im(Unary):
    """
    Takes the real part of a complex expression

    Parameters
    ----------
    argument : Expr
        Expression to take imaginary part of
    """

    def eval(self, var_dict: dict[Var, float]):
        return self.sub_nodes[0].eval(var_dict).imag

    def diff(self, var: Var):
        return Im(self.sub_nodes[0].diff())

    def simplify(self):
        return Im(self.sub_nodes[0].simplify())
    
    def __str__(self):
        return "Im(" + str(self.sub_nodes[0]) + ")"

class Step(Unary):
    """
    Step function around zero. Returns 1 for inputs greater than or equal to zero, returns 0 otherwise.

    Parameters
    ----------
    argument : Expr
        Expression to take step function of
    """
    def eval(self, var_dict: dict[Var, float]):
        val = self.sub_nodes[0].eval(var_dict)
        if val >= 0: return 1
        return 0

    def diff(self, var: Var):
        return Const(0)

    def simplify(self):
        self.sub_nodes[0] = self.sub_nodes[0].simplify()
        if isinstance(self.sub_nodes[0], Const):
            if self.sub_nodes[0].value >= 0:
                return Const(1)
            return Const(0)
        return Step(self.sub_nodes[0])

    def __str__(self):
        return "step(" + str(self.sub_nodes[0]) + ")"

def integrate(lower_bound: float, upper_bound: float, expr: Expr, var: Var, step_size: float = .001):
    assert lower_bound < upper_bound
    curr_point = lower_bound
    result = 0
    while (curr_point < upper_bound):
        result += (expr.eval(curr_point, var) + expr.eval(curr_point + step_size, var)) * step_size / 2
        curr_point += step_size
    return result
class TextColors:
    @staticmethod
    def set_color(input: str, color: str):
        return color + input + TextColors.RESET

    RED = "\x1b[31m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    BLUE = "\x1b[34m"
    MAGENTA = "\x1b[35m"
    CYAN = "\x1b[36m"
    WHITE = "\x1b[37m"
    RESET = "\x1b[0m"