# Small (quite inefficient) symbolic library to work with
from __future__ import annotations
from abc import ABC, abstractmethod
import math 
from .expr_types import *
from copy import deepcopy

class Multiply(Expr):
    precedence = 2

    def eval(self, t):
        total = 1
        for sub_expr in self.sub_nodes:
            total *= sub_expr.eval(t)
        return total

    def diff(self):
        if len(self.sub_nodes) >= 2:
            terms = []
            for i in range(len(self.sub_nodes)):
                term = deepcopy(self.sub_nodes)
                term[i] = term[i].diff()
                terms.append(Multiply(*term))
            return Add(*terms)
        if len(self.sub_nodes) == 1:
            return self.sub_nodes[0].diff()

    def simplify(self):
        i = 0
        while i < len(self.sub_nodes):
            self.sub_nodes[i] = self.sub_nodes[i].simplify()
            if isinstance(self.sub_nodes[i], Const):
                if self.sub_nodes[i].eval(0) == 0:
                    return Const(0)
                if self.sub_nodes[i].eval(0) == 1:
                    self.sub_nodes.pop(i)
                    i -= 1
                    if len(self.sub_nodes) == 0:
                        return Const(1)
            i += 1
        if len(self.sub_nodes) == 1:
            return self.sub_nodes[0]
        
        return Multiply(*self.sub_nodes)

    def __init__(self, *args):
        super().__init__(*args)
        assert len(self.sub_nodes) >= 1

    def __str__(self):
        output = ""
        for i, val in enumerate(self.sub_nodes):
            if i != 0:
                output += " * "
            
            takes_precedence = (val.precedence < self.precedence)
            if takes_precedence: output += "("
            output += str(val)
            if takes_precedence: output += ")"

        return output

class Add(Expr):
    precedence = 1

    def eval(self, t):
        total = 0
        for sub_expr in self.sub_nodes:
            total += sub_expr.eval(t)
        return total

    def diff(self):
        return Add(*(child.diff() for child in self.sub_nodes))

    def simplify(self):
        i = 0
        while i < len(self.sub_nodes):
            self.sub_nodes[i] = self.sub_nodes[i].simplify()
            if isinstance(self.sub_nodes[i], Const):
                if self.sub_nodes[i].eval(1) == 0:
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
    precedence = 1

    def eval(self, t):
        return self.sub_nodes[0].eval(t) - self.sub_nodes[1].eval(t)

    def diff(self):
        return Subtract(self.sub_nodes[0].diff(), self.sub_nodes[1].diff())
    
    def simplify(self):
        self.sub_nodes[0] = self.sub_nodes[0].simplify()
        self.sub_nodes[1] = self.sub_nodes[1].simplify()
        if isinstance(self.sub_nodes[1], Const):
            if self.sub_nodes[1].eval(0) == 0:
                return self.sub_nodes[0]
        return Subtract(self.sub_nodes[0], self.sub_nodes[1])

    def __str__(self):
        return str(self.sub_nodes[0]) + " - " + str(self.sub_nodes[1])
    
class Divide(Binary):
    precedence = 2

    def eval(self, t):
        denominator = self.sub_nodes[1].eval(t)
        if abs(denominator) == 0:
            raise ZeroDivisionError("YOU FOOL!!! YOU HAVE DIVIDED BY ZEERRROOOOOOO")
        return self.sub_nodes[0].eval(t) / denominator

    def diff(self):
        f = self.sub_nodes[0]
        g = self.sub_nodes[1]
        return Divide(Subtract(Multiply(f.diff(), g), Multiply(f, g.diff())), Pow(g, Const(2)))

    def simplify(self):
        self.sub_nodes[0] = self.sub_nodes[0].simplify()
        self.sub_nodes[1] = self.sub_nodes[1].simplify()
        if isinstance(self.sub_nodes[0], Const):
            if self.sub_nodes[0].eval(0) == 0:
                return Const(0)
        return Divide(self.sub_nodes[0], self.sub_nodes[1])

    def __str__(self):
        p1 = self.sub_nodes[0].precedence
        p2 = self.sub_nodes[1].precedence

        output = ""
        if p1 <= self.precedence: output += "("
        output += str(self.sub_nodes[0])
        if p1 <= self.precedence: output += ")"
        output += " / "

        if p2 <= self.precedence: output += "("
        output += str(self.sub_nodes[1])
        if p2 <= self.precedence: output += ")"
        return output

class Cos(Unary):
    def eval(self, t):
        return math.cos(self.sub_nodes[0].eval(t))
    
    def simplify(self):
        self.sub_nodes[0] = self.sub_nodes[0].simplify()
        if isinstance(self.sub_nodes[0], Const):
            if self.sub_nodes[0].eval(0) == 0:
                return Const(1)
        return Cos(self.sub_nodes[0])

    def diff(self):
        return Multiply(self.sub_nodes[0].diff(), Sin(self.sub_nodes[0]), Const(-1))

    def __str__(self):
        return "cos(" + str(self.sub_nodes[0]) + ")"

class Sin(Unary):
    def eval(self, t):
        return math.sin(self.sub_nodes[0].eval(t))
    
    def diff(self):
        return Multiply(self.sub_nodes[0].diff(), Cos(self.sub_nodes[0]))
    
    def simplify(self):
        self.sub_nodes[0] = self.sub_nodes[0].simplify()
        if isinstance(self.sub_nodes[0], Const):
            if self.sub_nodes[0].eval(0) == 0:
                return Const(0)
        return Sin(self.sub_nodes[0])

    def __str__(self):
        return "sin(" + str(self.sub_nodes[0]) + ")"

class Ln(Unary):
    def eval(self, t):
        return math.log(self.sub_nodes[0].eval(t))
    
    def diff(self):
        return Divide(self.sub_nodes[0].diff(), self.sub_nodes[0])

    def simplify(self):
        self.sub_nodes[0] = self.sub_nodes[0].simplify()
        if isinstance(self.sub_nodes[0], Const):
            if self.sub_nodes[0].eval(0) == 1:
                return Const(0)
        return Ln(self.sub_nodes[0])

    def __str__(self):
        return "ln(" + str(self.sub_nodes[0]) + ")"

class Pow(Binary):
    precedence = 3
    def eval(self, t):
        return self.sub_nodes[0].eval(t) ** self.sub_nodes[1].eval(t)
    
    def diff(self):
        f = self.sub_nodes[0]
        g = self.sub_nodes[1]
        return Multiply(Pow(f, g), Add(Multiply(g.diff(), Ln(f)), Divide(Multiply(g, f.diff()), f)))

    def simplify(self):
        self.sub_nodes[0] = self.sub_nodes[0].simplify()
        self.sub_nodes[1] = self.sub_nodes[1].simplify()
        if isinstance(self.sub_nodes[0], Const):
            if (self.sub_nodes[0].eval(0)) == 1:
                return Const(1)
            if (self.sub_nodes[0].eval(0)) == 0:
                return Const(0)
        if isinstance(self.sub_nodes[1], Const):
            if (self.sub_nodes[1].eval(0)) == 1:
                return self.sub_nodes[0]
        return Pow(self.sub_nodes[0], self.sub_nodes[1])

    def __str__(self):
        p1 = self.sub_nodes[0].precedence
        p2 = self.sub_nodes[1].precedence

        output = ""
        if p1 <= self.precedence: output += "("
        output += str(self.sub_nodes[0])
        if p1 <= self.precedence: output += ")"
        output += "^"

        if p2 <= self.precedence: output += "("
        output += str(self.sub_nodes[1])
        if p2 <= self.precedence: output += ")"
        return output

class Tan(Unary):
    def eval(self, t):
        return math.tan(self.sub_nodes[0].eval(t))
    
    def diff(self):
        return Multiply(self.sub_nodes[0].diff(), Divide(Const(1), Pow(Cos(self.sub_nodes[0]), Const(2))))

    def simplify(self):
        self.sub_nodes[0] = self.sub_nodes[0].simplify()
        if isinstance(self.sub_nodes[0], Const):
            if self.sub_nodes[0].eval(0) == 0:
                return Const(0)
        return Tan(self.sub_nodes[0])

    def __str__(self):
        return "tan(" + str(self.sub_nodes[0]) + ")"

class Abs(Unary):
    def eval(self, t):
        return abs(self.sub_nodes[0].eval(t))
    
    def diff(self):
        f = self.sub_nodes[0]
        return Multiply(f.diff(), Divide(f, Abs(f)))

    def simplify(self):
        self.sub_nodes[0] = self.sub_nodes[0].simplify()
        if isinstance(self.sub_nodes[0], Const):
            if self.sub_nodes[0].eval(0) == 0:
                return Const(0)
        return Abs(self.sub_nodes[0])

    def __str__(self):
        return "|" + str(self.sub_nodes[0]) + "|"
    
class Const(Unary):
    def eval(self, t):
        return self.sub_nodes[0]
    
    def diff(self):
        return Const(0)

    def simplify(self):
        return Const(self.sub_nodes[0])

    def __str__(self):
        return str(self.sub_nodes[0])
    
class Var(Expr):
    precedence = 4

    def eval(self, t):
        return t
    
    def diff(self):
        return Const(1)

    def simplify(self):
        return Var()

    def __init__(self, *args):
        super().__init__(*args)
        assert len(self.sub_nodes) == 0

    def __str__(self):
        return "t"

class Re(Unary):
    def eval(self, t):
        return self.sub_nodes[0].eval(t).real

    def diff(self):
        ...

    def simplify(self):
        return Re(self.sub_nodes[0].simplify())

    def __str__(self):
        return "Re(" + str(self.sub_nodes[0]) + ")"

class Im(Unary):
    def eval(self, t):
        return self.sub_nodes[0].eval(t).imag

    def diff(self):
        ...

    def simplify(self):
        return Im(self.sub_nodes[0].simplify())
    
    def __str__(self):
        return "Im(" + str(self.sub_nodes[0]) + ")"

class Step(Unary):
    def eval(self, t):
        val = self.sub_nodes[0].eval(t)
        if val >= 0: return 1
        return 0

    def diff(self):
        return Const(0)

    def simplify(self):
        self.sub_nodes[0] = self.sub_nodes[0].simplify()
        if isinstance(self.sub_nodes[0], Const):
            if self.sub_nodes[0].eval(0) >= 0:
                return Const(1)
            return Const(0)
        return Step(self.sub_nodes[0])

    def __str__(self):
        return "step(" + str(self.sub_nodes[0]) + ")"

def integrate(lower_bound: float, upper_bound: float, expr: Expr, step_size: float = .001):
    assert lower_bound < upper_bound
    curr_point = lower_bound
    result = 0
    while (curr_point < upper_bound):
        result += (expr.eval(curr_point) + expr.eval(curr_point + step_size)) * step_size / 2
        curr_point += step_size
    return result

def find_fourier_coefficient(n: int, func: Expr, L: float = 1) -> float:
    fourier_expression = Multiply(Const(1 / L), func, Pow(Const(math.e), Multiply(Const(-2 * math.pi * 1j * n / L), Var())))
    return integrate(0, L, fourier_expression)


def find_fourier_function(n: int, func: Expr, L: float) -> Expr:
    coefficient_list = [find_fourier_coefficient(0, func, L)]
    for i in range(1, n + 1):
        coefficient_list.insert(0, find_fourier_coefficient(-i, func, L))
        coefficient_list.append(find_fourier_coefficient(i, func, L))

    terms = []
    # idx goes from 0 to 2n
    # k will correctly map from -n to n
    for idx, coef in enumerate(coefficient_list):
        k = idx - n 
        exponent = Multiply(Const(2j * math.pi * k / L), Var())
        terms.append(Multiply(Const(coef), Pow(Const(math.e), exponent)))
        
    return Add(*terms)