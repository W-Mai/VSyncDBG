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

        if lcd_c() == 0:
            if not lcd_c.keeping(7):
                lcd_c(1)
                Prj.te_intr(m)
        else:
            if not lcd_c.keeping(8):
                lcd_c(0)
                Prj.frame_done(m)

    @staticmethod
    def update_render(m: Machine):
        poll = m.get_signal("poll")
        render = m.get_signal("render")
        render_buffer = m.get_signal("render_buffer")

        if poll() and render() != 1:
            render(1)
            Prj.check_collision(m)
            render.update_time()

        if render() == 1:
            rnd = randrange(2, 100)
            # rnd = 20
            if not render.keeping(rnd):
                Prj.check_collision(m)
                render(0)
                poll(poll() - 1)

                Prj.VSYNC_QUEUE.append(render_buffer())
                render_buffer(1 - render_buffer())

    @staticmethod
    def te_intr(m: Machine):
        poll = m.get_signal("poll")
        send_buffer = m.get_signal("send_buffer")

        poll(poll() + 1
                 if poll() < Prj.POLL_LIMIT
                 else Prj.POLL_LIMIT)

        send_buffer(Prj.VSYNC_QUEUE.pop(0) if Prj.VSYNC_QUEUE else - 1)
        Prj.check_collision(m)

    @staticmethod
    def frame_done(m: Machine):
        Prj.check_collision(m)

    @staticmethod
    def check_collision(m: Machine):
        send_buffer = m.get_signal("send_buffer")
        render_buffer = m.get_signal("render_buffer")

        if send_buffer() == render_buffer():
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
