from io import StringIO
from Machine import Machine
from draw import draw
from random import randrange


class Prj(object):
    POLL_LIMIT = 1
    VSYNC_QUEUE = []

    @staticmethod
    def update_lcd_c(m: Machine):
        lcd_c = m.get_signal("lcd_c")

        if lcd_c.get() == 0:
            if not lcd_c.keeping(7):
                lcd_c.set(1)
                Prj.te_intr(m)
        else:
            if not lcd_c.keeping(8):
                lcd_c.set(0)
                Prj.frame_done(m)

    @staticmethod
    def update_render(m: Machine):
        poll = m.get_signal("poll")
        render = m.get_signal("render")
        render_buffer = m.get_signal("render_buffer")

        if poll.get() and render.get() != 1:
            render.set(1)
            Prj.check_collision(m)
            render.update_time()

        if render.get() == 1:
            # rnd = randrange(10, 15)
            rnd = 20
            if not render.keeping(rnd):
                Prj.check_collision(m)
                render.set(0)
                poll.set(poll.get() - 1)

                Prj.VSYNC_QUEUE.append(render_buffer.get())
                render_buffer.set(1 - render_buffer.get())

    @staticmethod
    def te_intr(m: Machine):
        poll = m.get_signal("poll")
        send_buffer = m.get_signal("send_buffer")

        poll.set(poll.get() + 1
                 if poll.get() < Prj.POLL_LIMIT
                 else Prj.POLL_LIMIT)

        send_buffer.set(Prj.VSYNC_QUEUE.pop() if Prj.VSYNC_QUEUE else - 1)
        Prj.check_collision(m)

    @staticmethod
    def frame_done(m: Machine):
        Prj.check_collision(m)

    @staticmethod
    def check_collision(m: Machine):
        send_buffer = m.get_signal("send_buffer")
        render_buffer = m.get_signal("render_buffer")

        if send_buffer.get() == render_buffer.get():
            print("Collision detected!")


if __name__ == '__main__':
    with StringIO() as f:
        machine = Machine(f, dump_signals=[
            'poll',
            'lcd_c',
            'render',
            'render_buffer',
            'send_buffer'
        ], tick_per_mil=1)

        machine.add_updater(Prj.update_lcd_c)
        machine.add_updater(Prj.update_render)

        for i in range(int(machine.calc_sim_time(400))):
            machine.update(machine.get_mil_per_tick())

        f.seek(0)

        draw(f)
