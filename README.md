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
from Machine import Project, Signal, Updater
from draw import draw


class Prj(Project):
    a = Signal(0)
    b = Signal(1)

    @Updater
    def updater(self):
        a = self.s.a
        b = self.s.b

        if not a.keeping(3):
            a.toggle()
        if not b.keeping(1.5):
            b.toggle()


with StringIO() as f:
    Prj.run(1000, 21, f)
    draw(f)
```

![img.png](snaps/img.png)
