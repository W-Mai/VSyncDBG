from io import StringIO
from Machine import Project, Signal, Updater
from draw import draw
from random import randrange


class Prj(Project):
    POLL_LIMIT = 1
    VSYNC_QUEUE = []

    poll = Signal(1)
    lcd_c = Signal(0)
    render = Signal(0)
    render_buffer = Signal(0)
    send_buffer = Signal(0)

    @Updater
    def update_lcd_c(self):
        lcd_c = self.s.lcd_c

        if lcd_c() == 0:
            if not lcd_c.keeping(7):
                lcd_c(1)
                Prj.te_intr()
        else:
            if not lcd_c.keeping(8):
                lcd_c(0)
                Prj.frame_done()

    @Updater
    def update_render(self):
        poll, render, render_buffer = self.s.poll, self.s.render, self.s.render_buffer

        if poll() and render() != 1:
            render(1)
            Prj.check_collision()
            render.update_time()

        if render() == 1:
            rnd = randrange(2, 100)
            # rnd = 20
            if not render.keeping(rnd):
                Prj.check_collision()
                render(0)
                poll(poll() - 1)

                Prj.VSYNC_QUEUE.append(render_buffer())
                render_buffer(1 - render_buffer())

    @classmethod
    def te_intr(cls):
        send_buffer, poll = cls.s.send_buffer, cls.s.poll

        poll(poll() + 1
             if poll() < Prj.POLL_LIMIT
             else Prj.POLL_LIMIT)

        send_buffer(Prj.VSYNC_QUEUE.pop(0) if Prj.VSYNC_QUEUE else - 1)
        Prj.check_collision()

    @classmethod
    def frame_done(cls):
        Prj.check_collision()

    @classmethod
    def check_collision(cls):
        send_buffer, render_buffer = cls.s.send_buffer, cls.s.render_buffer

        if send_buffer() == render_buffer():
            print("Collision detected!")


if __name__ == '__main__':
    with StringIO() as f:
        Prj.run(1, 400, f)
        draw(f)
