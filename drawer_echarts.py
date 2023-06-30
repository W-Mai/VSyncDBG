import random
import numpy as np
from io import StringIO

import pyecharts.options as opts
from pyecharts.charts import Line, Grid


def draw(f: StringIO):
    lines = iter(f.readlines())
    updaters = int(next(lines).split("/")[0])
    tick_per_mil = int(next(lines).split("/")[0])
    labels = next(lines).split()

    lines = map(lambda x0: x0.split(), lines)

    arr = np.array(list(lines), dtype="int32")
    size, row = arr.shape

    signal_graphs = [
        (
            Line()
            .add_xaxis(list(range(int(size / tick_per_mil / updaters))))
            .add_yaxis(
                labels[i],
                arr[:, i].flatten().tolist(),
                is_step=True,
                label_opts=opts.LabelOpts(is_show=False),
                linestyle_opts=opts.LineStyleOpts(width=3),
            )
            .set_global_opts(
                yaxis_opts=opts.AxisOpts(
                    interval=1,
                    grid_index=i,
                ),
                xaxis_opts=opts.AxisOpts(
                    interval=1,
                    grid_index=i,
                    type_="category",
                    boundary_gap=True,
                    axisline_opts=opts.AxisLineOpts(is_on_zero=True),
                ),
                datazoom_opts=[
                    opts.DataZoomOpts(
                        is_realtime=True,
                        type_="slider",
                        range_start=0,
                        range_end=int(size / tick_per_mil / updaters),
                        xaxis_index=list(range(row)),
                    )
                ],
                legend_opts=opts.LegendOpts(pos_left="10px", pos_top=f"{30 + (10 + 20) * i}", item_height=10),
            )
        ) for i in range(row)
    ]

    g = Grid(init_opts=opts.InitOpts(width="100%", height="90vh"))

    for i in range(row):
        g = g.add(
            chart=signal_graphs[i],
            grid_opts=opts.GridOpts(
                pos_top=f"{int(100 / row * i * 0.8) + 5}%",
                height=f"{100 / row * 0.6}%",
                is_contain_label=True,
                is_show=False,
            )
        )

    g.render("render.html")
