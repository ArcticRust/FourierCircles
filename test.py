from math_tooling import *
t = Var()


f = Add(Pow(Sin(t), Const(2)), Cos(Divide(Const(1), Cos(t))))
domain = [-math.pi / 2, math.pi / 2]

#fourier_f3 = Re(find_fourier_function(3, f))
#fourier_f5 = Re(find_fourier_function(5, f))
fourier_f100 = find_fourier_function(500, f, domain)

error_func = Abs(Subtract(f, fourier_f100))
error_on_interval = integrate(domain[0], domain[1], error_func)
print(error_on_interval)

BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

g_builder = GraphBuilder(x_scale=.5)
g_builder.draw_axis()
#g_builder.plot(fourier_f3)
#g_builder.plot(fourier_f5)
g_builder.plot(Re(fourier_f100), RED)
#g_builder.plot(error_func, GREEN)
g_builder.plot(Re(f), BLACK)


g_builder.run()
