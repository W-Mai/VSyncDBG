from matplotlib import pyplot as plt
import numpy as np

with open("log2") as f:
    lines = list(map(lambda x0: x0.split(), f.readlines()))
    arr = np.array(lines, dtype="int32")
    size, row = arr.shape

x = np.arange(size)

fig, ax = plt.subplots(nrows=row)

for i in range(row):
    ax[i].step(x, arr[:, i], linewidth=2.5)

plt.show()
