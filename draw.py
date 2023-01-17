from matplotlib import pyplot as plt
import numpy as np

with open("log") as f:
    lines = list(map(lambda x: x.split(), f.readlines()))
    arr = np.array(lines, dtype="int32")
    size = arr.shape[0]

x = np.arange(size)
poll_flag = arr[:, 0]
buffer_index = arr[:, 1]
send_index = arr[:, 2]
mipi_flag = arr[:, 3]
render_flag = arr[:, 4]

fig, ax = plt.subplots()

ax.step(x, poll_flag, linewidth=2.5)
ax.step(x, buffer_index + 1, linewidth=2.5)
ax.step(x, send_index + 2, linewidth=2.5)
ax.step(x, mipi_flag + 3, linewidth=2.5)
ax.step(x, render_flag + 4, linewidth=2.5)

# ax.set(ylim=(0, 1), yticks=np.arange(0, 2))


plt.show()
