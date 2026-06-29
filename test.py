from math_tooling import *
t = Var()
f = Multiply(Sin(Cos(t)), Pow(Const(2), Multiply(Const(-1), Cos(t))))
#fourier_f3 = Re(find_fourier_function(3, f))
#fourier_f5 = Re(find_fourier_function(5, f))
fourier_f100 = Re(find_fourier_function(100, f))


g_builder = GraphBuilder()
g_builder.draw_axis()
g_builder.plot(f)
#g_builder.plot(fourier_f3)
#g_builder.plot(fourier_f5)
g_builder.plot(fourier_f100)
g_builder.run()
