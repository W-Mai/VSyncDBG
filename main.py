from io import StringIO
from Machine import Machine
from draw import draw
from random import randrange


class Prj(object):
    INITED = False

    @staticmethod
    def on_init(m: Machine):
        pollready = m.get_signal("pollready")
        pollmon = m.get_signal("pollmon")

        if not Prj.INITED:
            pollready.set(1)
            pollmon.set(1)
            Prj.INITED = True

    @staticmethod
    def update_lcd(m: Machine):
        lcd = m.get_signal("lcd")
        send_buffer = m.get_signal("send_buffer")

        if lcd.get() == 0:
            if not lcd.keeping(7):
                lcd.set(1)
                Prj.te_intr(m)

        else:
            if not lcd.keeping(8):
                if send_buffer.get():
                    Prj.frame_done(m)
                lcd.set(0)

    @staticmethod
    def update_render(m: Machine):
        pollready = m.get_signal("pollready")
        pollmon = m.get_signal("pollmon")
        render = m.get_signal("render")
        render_buffer = m.get_signal("render_buffer")
        commit_buffer = m.get_signal("commit_buffer")

        if pollmon.get() and pollready.get() and render.get() != 1:
            pollmon.set(0)
            render.set(1)
            Prj.check_corruption(m)
            render.update_time()

        if render.get() == 1:
            rnd = randrange(2, 100)
            # rnd = 20
            if not render.keeping(rnd):
                Prj.check_corruption(m)

                commit_buffer.set(render_buffer.get())
                render_buffer.set(1 - render_buffer.get())
                render.set(0)
                pollmon.set(1)

    @staticmethod
    def te_intr(m: Machine):
        commit_buffer = m.get_signal("commit_buffer")
        if (commit_buffer.get()):
            Prj.frame_start(m)

    @staticmethod
    def frame_start(m: Machine):
        send_buffer = m.get_signal("send_buffer")
        commit_buffer = m.get_signal("commit_buffer")

        send_buffer.set(commit_buffer.get())
        Prj.check_corruption(m)

    @staticmethod
    def frame_done(m: Machine):
        pollready = m.get_signal("pollready")
        send_buffer = m.get_signal("send_buffer")
        Prj.check_corruption(m)
        pollready.set(1)
        send_buffer.set(-1)

    @staticmethod
    def check_corruption(m: Machine):
        send_buffer = m.get_signal("send_buffer")
        render_buffer = m.get_signal("render_buffer")
        corruption = m.get_signal("corruption")
        render = m.get_signal("render")
        lcd = m.get_signal("lcd")

        if render.get() and lcd.get() and send_buffer.get() == render_buffer.get():
            corruption.set(corruption.get() + 1)
            print("corruption detected!")


if __name__ == '__main__':
    with StringIO() as f:
        machine = Machine(f, dump_signals=[
            'pollready',
            'pollmon',
            'lcd',
            'render',
            'render_buffer',
            'send_buffer',
            'commit_buffer',
            'crruption'
        ], tick_per_mil=1)

        machine.add_updater(Prj.on_init)
        machine.add_updater(Prj.update_lcd)
        machine.add_updater(Prj.update_render)

        for i in range(int(machine.calc_sim_time(200))):
            machine.update(machine.get_mil_per_tick())

        f.seek(0)

        draw(f)
