# VSyncDBG

# Install Requirements

```shell
pip3 install -r requirements.txt
```

# Run

```shell
python3 main.py
```

# Easy to Use

```python
from io import StringIO
from Machine import Machine
from draw import draw

with StringIO() as f:
    m = Machine(f, dump_signals=[
        'a'
    ], tick_per_mil=1000)


    def updater1(u: Machine):
        a = u.get_signal("a")
        if not a.keeping(3):
            a.toggle()


    m.add_updater(updater1)

    for i in range(int(m.calc_sim_time(21))):
        m.update(m.get_mil_per_tick())

    f.seek(0)
    draw(f)
```

![img.png](snaps/img.png)
