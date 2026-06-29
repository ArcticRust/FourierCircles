from math_tooling import *

t = Var("t")
x = Var("x")
y = Var("y")

f = Sin(Multiply(x, t, Sin(Multiply(x, t))))

print(f.diff(x).simplify())