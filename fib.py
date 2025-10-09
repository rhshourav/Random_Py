
from matplotlib import pyplot as plt


fib = [0, 1]

for i in range(1405):
    fib.append(fib[-1] + fib[-2])

plt.grid()
plt.plot(fib)
plt.show()
