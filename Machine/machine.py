class _Signal(object):
    def __init__(self, machine: 'Machine', name: str):
        self._name = name
        self._machine = machine
        self._keep_time = None

    def keeping(self, t):
        self._keep_time = t
        if self._keep_time:
            millis = self._machine.millis
            ct = self._machine._get_time(self._name)
            if millis >= ct + self._keep_time:
                self._keep_time = None
                self.update_time()
            else:
                return True
        return False

    def __call__(self, *args, **kwargs):
        if args:
            return self.set(args[0])
        return self.get()

    def get(self):
        return self._machine._get_signal(self._name)

    def set(self, val):
        return self._machine._set_signal(self._name, val)

    def toggle(self):
        self.set(0 if self.get() else 1)

    def update_time(self):
        self._machine._set_current_time(self._name)


class SignalsWrapper(object):
    def __init__(self, machine: 'Machine'):
        self._machine = machine

    def __getattr__(self, name):
        return self._machine.get_signal(name)

    def __dict__(self):
        return self._machine._signals_obj

    def __dir__(self):
        return list(self.__dict__().keys()) + dir(type(self))


class Machine(object):
    def __init__(self, dump_signals):
        self.millis = 0.0
        self._timestamps = {}
        self._signals = {}
        self._signals_obj = {}
        self._dump_signals = dump_signals
        self._updaters = []
        self._tick_per_mil = 0
        self.fd = None

        self.s = SignalsWrapper(self)

    def calc_sim_time(self, t):
        return t * self._tick_per_mil

    def get_mil_per_tick(self):
        return 1 / self._tick_per_mil

    def update(self, delta: float):
        for up in self._updaters:
            up(self)
            self.dump_sig()

        self.millis += delta

    def _dump_sig_header(self):
        self.fd.write(f"{len(self._updaters)}/updaters\n")
        self.fd.write(f"{self._tick_per_mil}/1ms\n")
        self.fd.write(" ".join(self._dump_signals) + "\n")

    def dump_sig(self):
        self.fd.write(" ".join(map(str, [
            self._signals.get(key, 0) for key in self._dump_signals
        ])) + "\n")

        return {
            key: self._signals.get(key, 0) for key in self._dump_signals
        }

    def _get_time(self, key):
        if not self._timestamps.get(key, None):
            self._timestamps[key] = self.millis
        return self._timestamps[key]

    def _set_time(self, key, val):
        self._timestamps[key] = val

    def _set_current_time(self, key):
        self._timestamps[key] = self.millis

    def _get_signal(self, key):
        if not self._signals.get(key, None):
            self._signals[key] = 0
        return self._signals[key]

    def _set_signal(self, key, val):
        self._signals[key] = val

    # Public Functions
    def add_updater(self, updater):
        self._updaters.append(updater)

    def get_signal(self, name):
        if name not in self._dump_signals:
            raise Exception(f"{name} is not in dump signals")

        sig = self._signals_obj.get(name, None)
        if not sig:
            sig = _Signal(self, name)
            self._signals_obj[name] = sig
        return sig


class Signal(object):
    def __init__(self, init_val):
        self.init_val = init_val


class Updater(object):
    def __init__(self, updater):
        self.updater = updater
        self.project = None

    def __call__(self, machine):
        # machine: not use
        return self.updater(self.project)

    def set_project(self, project):
        self.project = project

    @property
    def is_updater(self):
        return True


class ProjectMeta(type):
    def __new__(mcs, name, bases, attrs):
        dump_signals = []
        new_attrs = {}
        for key, val in attrs.items():
            if isinstance(val, Signal):
                dump_signals.append(key)
            else:
                new_attrs[key] = val

        machine = Machine(dump_signals)
        for sig in dump_signals:
            machine.get_signal(sig)(attrs[sig].init_val)

        new_attrs["_machine"] = machine
        new_attrs["s"] = machine.s

        obj = super().__new__(mcs, name, bases, new_attrs)

        for key, val in new_attrs.items():
            if isinstance(val, Updater):
                val.set_project(obj)
                machine.add_updater(val)

        return obj


# noinspection PyProtectedMember
class Project(object, metaclass=ProjectMeta):
    s = None
    _machine = None

    @classmethod
    def run(cls, tick_per_mil, lasted_time, fd):
        cls._machine._tick_per_mil = tick_per_mil
        cls._machine.fd = fd

        cls._machine._dump_sig_header()
        for 無駄 in range(int(cls._machine.calc_sim_time(lasted_time))):
            cls._machine.update(cls._machine.get_mil_per_tick())

        fd.seek(0)


# test only
if __name__ == '__main__':
    from io import StringIO
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
