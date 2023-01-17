class Machine(object):
    def __init__(self):
        self.millis = 0.0
        self._timestamps = {}
        self._signals = {}

    def update(self, delta: float):
        self.millis += delta

        self._update_lcd_c()
        self._update_render()

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
                self._set_current_time("lcd_c")
        else:
            if self.millis - self._get_time("lcd_c") > 7:
                self._set_signal("lcd_c", 1)
                self._set_signal("poll", 1)
                self._set_current_time("lcd_c")

    def _update_render(self):
        if self._get_signal("poll"):
            self._set_signal("poll", 0)
            self._set_signal("render", 1)

        if self._get_signal("render") == 1:
            if self.millis - self._get_time("render") > 15:
                self._set_signal("render", 0)
                self._set_current_time("render")

    # call
    def _te_intr(self):
        pass

    def _frame_done(self):
        pass


m = Machine()
for i in range(100):
    m.update(1)
    print(m._signals)
