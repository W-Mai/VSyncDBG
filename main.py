from io import StringIO
from Machine import Machine
from draw import draw


class Prj(object):

    @staticmethod
    def update_lcd_c(m: Machine):
        lcd_c = m.get_signal("lcd_c")

        if lcd_c.get() == 0:
            if not lcd_c.keeping(7):
                lcd_c.set(1)
                Prj.te_intr(m)
        else:
            if not lcd_c.keeping(15):
                lcd_c.set(0)
                Prj.frame_done(m)

    @staticmethod
    def update_render(m: Machine):
        poll = m.get_signal("poll")
        render = m.get_signal("render")
        render_buffer = m.get_signal("render_buffer")
        commit_buffer = m.get_signal("commit_buffer")

        if poll.get() and render.get() != 1:
            render.set(1)
            render.update_time()

        if render.get() == 1:
            if not render.keeping(43):
                render.set(0)
                poll.set(0)

                commit_buffer.set(render_buffer.get())
                render_buffer.set(1 - render_buffer.get())

    @staticmethod
    def te_intr(m: Machine):
        poll = m.get_signal("poll")
        send_buffer = m.get_signal("send_buffer")
        commit_buffer = m.get_signal("commit_buffer")

        if poll.get() == 0:
            poll.set(1)
        send_buffer.set(commit_buffer.get())

    @staticmethod
    def frame_done(m: Machine):
        pass


if __name__ == '__main__':
    with StringIO() as f:
        machine = Machine(f, dump_signals=[
            'lcd_c', 'poll', 'render', 'render_buffer',
            'commit_buffer', 'send_buffer'
        ], tick_per_mil=10)

        machine.add_updater(Prj.update_lcd_c)
        machine.add_updater(Prj.update_render)

        for i in range(int(machine.calc_sim_time(500))):
            machine.update(machine.get_mil_per_tick())

        f.seek(0)

        draw(f)
