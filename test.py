from math_tooling import *
t = Var()

f = Multiply(Sin(t), Pow(Const(2), Pow(t, Const(2))))


#fourier_f3 = Re(find_fourier_function(3, f))
#fourier_f5 = Re(find_fourier_function(5, f))
fourier_f100 = find_fourier_function(60, f, 1 * math.pi)

BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

g_builder = GraphBuilder()
g_builder.draw_axis()
#g_builder.plot(fourier_f3)
#g_builder.plot(fourier_f5)
g_builder.plot(Re(fourier_f100), RED)
g_builder.plot(Abs(Subtract(f, fourier_f100)), GREEN)
g_builder.plot(Re(f), BLACK)


g_builder.run()
