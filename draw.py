from matplotlib import pyplot as plt
import numpy as np

SEP = True

with open("log") as f:
    lines = list(map(lambda x0: x0.split(), f.readlines()))
    arr = np.array(lines, dtype="int32")
    size, row = arr.shape

x = np.arange(size)

fig, ax = plt.subplots(nrows=row if SEP else 1)

for i in range(row):
    if SEP:
        ax[i].step(x, arr[:, i], linewidth=2.5)
    else:
        ax.step(x, arr[:, i] + 1.1 * i, linewidth=2.5)

plt.show()
