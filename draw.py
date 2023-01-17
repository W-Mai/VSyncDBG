from io import StringIO

from matplotlib import pyplot as plt
import numpy as np


def draw(f: StringIO):
    lines = list(map(lambda x0: x0.split(), f.readlines()))
    labels = lines[0]
    arr = np.array(lines[1:], dtype="int32")
    size, row = arr.shape

    x = np.arange(size)

    fig, ax = plt.subplots()
    ax.get_yaxis().set_visible(False)

    for i in range(row):
        ax.step(x, arr[:, i] - 1.1 * i, linewidth=2.5, label=labels[i])

    plt.legend(title='Parameter where:')
    plt.show()
