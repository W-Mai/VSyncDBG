from io import StringIO


class Signal(object):
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

    def get(self):
        return self._machine._get_signal(self._name)

    def set(self, val):
        return self._machine._set_signal(self._name, val)

    def update_time(self):
        self._machine._set_current_time(self._name)


class Machine(object):
    def __init__(self, fd, dump_signals):
        self.millis = 0.0
        self._timestamps = {}
        self._signals = {}
        self._signals_obj = {}
        self._dump_signals = dump_signals
        self._updaters = []

        self.fd = fd
        self._dump_sig_header()

    def update(self, delta: float):
        for up in self._updaters:
            up(self)
            self.dump_sig()

        self.millis += delta

    def _dump_sig_header(self):
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
        sig = self._signals_obj.get(name, None)
        if not sig:
            sig = Signal(self, name)
            self._signals_obj[name] = sig
        return sig


# test only
if __name__ == '__main__':
    from io import StringIO
    from Machine import Machine
    from draw import draw

    with StringIO() as f:
        m = Machine(f, dump_signals=[
            'a'
        ])


        def updater1(u: Machine):
            a = u.get_signal("a")
            if not a.keeping(3):
                a.set(1 - a.get())


        m.add_updater(updater1)

        for i in range(21):
            m.update(1)

        f.seek(0)
        draw(f)
