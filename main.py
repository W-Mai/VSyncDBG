class Machine(object):
    def __init__(self, fd):
        self.millis = 0.0
        self._timestamps = {}
        self._signals = {}

        self.fd = fd

    def update(self, delta: float):
        self.millis += delta

        self._update_lcd_c()
        print(self.dump_sig())
        self._update_render()
        print(self.dump_sig())

    def dump_sig(self):
        keys = ['lcd_c', 'poll', 'render', 'buffer', 'send', 'mipi_busy']
        self.fd.write(" ".join(map(str, [
            self._signals.get(key, 0) for key in keys
        ])) + "\n")

        return {
            key: self._signals.get(key, 0) for key in keys
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

    def _update_lcd_c(self):
        if self._get_signal("lcd_c") == 1:
            if self.millis - self._get_time("lcd_c") > 35:
                self._set_signal("lcd_c", 0)
                self._frame_done()
                self._set_current_time("lcd_c")
        else:
            if self.millis - self._get_time("lcd_c") > 7:
                self._set_signal("lcd_c", 1)
                self._set_current_time("lcd_c")
                self._te_intr()

    def _update_render(self):
        if self._get_signal("poll"):
            self._set_signal("poll", 0)
            self._set_signal("render", 1)
            self._set_current_time("render")

        if self._get_signal("render") == 1:
            if self.millis - self._get_time("render") > 15:
                self._set_signal("render", 0)
                self._set_signal("buffer", 1 - self._get_signal("buffer"))
                # self._set_current_time("render")

    # call
    def _te_intr(self):
        self._set_signal("poll", 1)
        self._set_signal("send", self._get_signal("buffer"))
        self._set_signal("mipi_busy", 1)

    def _frame_done(self):
        self._set_signal("mipi_busy", 0)


with open("log2", "w") as f:
    m = Machine(f)
    for i in range(200):
        m.update(1)

import draw
