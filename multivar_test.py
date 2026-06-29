from math_tooling import *

x = Var("x")
y = Var("y")

f = Pow(Divide(Add(x, y), Multiply(x, Pow(y, Const(2)))), Const(2))
print(f.diff(x).simplify())
