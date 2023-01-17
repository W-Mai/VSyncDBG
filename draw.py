from io import StringIO

from matplotlib import pyplot as plt
import numpy as np


def draw(f: StringIO):
    lines = iter(f.readlines())
    updaters = int(next(lines).split("/")[0])
    tick_per_mil = int(next(lines).split("/")[0])
    labels = next(lines).split()

    lines = map(lambda x0: x0.split(), lines)

    arr = np.array(list(lines), dtype="int32")
    size, row = arr.shape

    x = np.linspace(0, size / tick_per_mil / updaters, size)

    fig, ax = plt.subplots()
    ax.get_yaxis().set_visible(False)

    for i in range(row):
        ax.step(x, arr[:, i] - 1.1 * i, linewidth=2.5, label=labels[i])

    plt.legend(title='Parameter where:')
    plt.show()
