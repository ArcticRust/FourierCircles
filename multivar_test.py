from math_tooling import *

t = Var("t")
x = Var("x")
y = Var("y")

f = Multiply(Sin(x), Cos(t), Pow(Cos(x), y))
print(f.diff(x).simplify())