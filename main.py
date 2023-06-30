from io import StringIO
from Machine import Project, Signal, Updater, Passive, Event
from draw import draw
from random import randrange


class Prj(Project):
    INITED = False
    VSYNC_QUEUE_LEN = 2
    VSYNC_QUEUE = []

    pollmon = Signal(1)
    lcd = Signal(0)
    render = Signal(0)
    render_buffer = Signal(0)
    send_buffer = Signal(-1)
    corruption = Signal(0)
    queue_len = Signal(0)

    @Event.Init
    def init(self):
        print("Simulation started!")

    @Updater
    def update_lcd(self):
        lcd = self.s.lcd
        send_buffer = self.s.send_buffer

        if lcd() == 0:
            if not lcd.keeping(8):
                lcd(1)
                self.te_intr()

        else:
            if not lcd.keeping(8):
                if send_buffer() > -1:
                    self.frame_done()
                lcd(0)

    @Updater
    def update_render(self):
        pollmon = self.s.pollmon
        render = self.s.render
        render_buffer = self.s.render_buffer

        if pollmon() and self.get_writeable() and render() != 1:
            pollmon(0)
            render(1)
            self.check_corruption()
            render.update_time()

        if render() == 0:
            # idle_time = randrange(2, 100)
            idle_time = 0
            if not render.keeping(idle_time):
                pollmon(1)
        else:
            render_time = randrange(2, 100)
            # render_time = 50
            if not render.keeping(render_time):
                self.check_corruption()
                self.VSYNC_QUEUE.append(render_buffer.get())
                render_buffer(1 - render_buffer.get())
                render(0)

    @Passive
    def get_writeable(self):
        return len(self.VSYNC_QUEUE) < self.VSYNC_QUEUE_LEN

    @Passive
    def get_readable(self):
        return len(self.VSYNC_QUEUE) > 0

    @Passive
    def te_intr(self):
        if self.get_readable():
            self.frame_start()

    @Passive
    def frame_start(self):
        send_buffer = self.s.send_buffer
        send_buffer(self.VSYNC_QUEUE[0])
        self.check_corruption()

    @Passive
    def frame_done(self):
        send_buffer = self.s.send_buffer
        self.check_corruption()
        self.VSYNC_QUEUE.pop(0)
        send_buffer(-1)

    @Passive
    def check_corruption(self):
        send_buffer = self.s.send_buffer
        render_buffer = self.s.render_buffer
        corruption = self.s.corruption
        render = self.s.render
        lcd = self.s.lcd
        queue_len = self.s.queue_len

        queue_len(len(self.VSYNC_QUEUE) - 1)

        if render() and lcd() and send_buffer() == render_buffer():
            corruption(corruption() + 1)
            print("corruption detected!")


if __name__ == '__main__':
    with StringIO() as f:
        Prj.run(1, 1000, f)

        draw(f)
