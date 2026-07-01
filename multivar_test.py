from math_tooling import *

x = Var("x")
y = Var("y")

f = Pow(Add(x, Const(1)), Const(30))
eval_dict = {
    x: 3,
    y: 7
}
print(f)
print("")
print(f.diff(x).simplify())
print("")
print(f.diff(x).simplify().diff(x).simplify())
print("")
print(f.diff(x).simplify().diff(x).simplify().diff(x).simplify())