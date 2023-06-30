from io import StringIO
from Machine import Project, Signal, Updater, Passive, Init, UpdateBefore, UpdateAfter
from draw import draw
from random import randrange


class Prj(object):
    INITED = False
    VSYNC_QUEUE_LEN = 2
    VSYNC_QUEUE = []

    @staticmethod
    def on_init(m: Machine):
        pollmon = m.get_signal("pollmon")
        send_buffer = m.get_signal("send_buffer")

        if not Prj.INITED:
            pollmon.set(1)
            send_buffer.set(-1)
            Prj.INITED = True

    @staticmethod
    def update_lcd(m: Machine):
        lcd = m.get_signal("lcd")
        send_buffer = m.get_signal("send_buffer")

        if lcd.get() == 0:
            if not lcd.keeping(8):
                lcd.set(1)
                Prj.te_intr(m)

        else:
            if not lcd.keeping(8):
                if send_buffer.get() > -1:
                    Prj.frame_done(m)
                lcd.set(0)
    
    @staticmethod
    def get_writeable(m: Machine):
        return len(Prj.VSYNC_QUEUE) < Prj.VSYNC_QUEUE_LEN
    
    @staticmethod
    def get_readable(m: Machine):
        return len(Prj.VSYNC_QUEUE) > 0

    @staticmethod
    def update_render(m: Machine):
        pollmon = m.get_signal("pollmon")
        render = m.get_signal("render")
        render_buffer = m.get_signal("render_buffer")

        if pollmon.get() and Prj.get_writeable(m) and render.get() != 1:
            pollmon.set(0)
            render.set(1)
            Prj.check_corruption(m)
            render.update_time()

        if render.get() == 0:
            # idle_time = randrange(2, 100)
            idle_time = 0
            if not render.keeping(idle_time):
                pollmon.set(1)
        else:
            render_time = randrange(2, 100)
            # render_time = 50
            if not render.keeping(render_time):
                Prj.check_corruption(m)
                Prj.VSYNC_QUEUE.append(render_buffer.get())
                render_buffer.set(1 - render_buffer.get())
                render.set(0)
                
    @staticmethod
    def te_intr(m: Machine):
        if (Prj.get_readable(m)):
            Prj.frame_start(m)

    @staticmethod
    def frame_start(m: Machine):
        send_buffer = m.get_signal("send_buffer")
        send_buffer.set(Prj.VSYNC_QUEUE[0])
        Prj.check_corruption(m)

    @staticmethod
    def frame_done(m: Machine):
        send_buffer = m.get_signal("send_buffer")
        Prj.check_corruption(m)
        Prj.VSYNC_QUEUE.pop(0)
        send_buffer.set(-1)

    @staticmethod
    def check_corruption(m: Machine):
        send_buffer = m.get_signal("send_buffer")
        render_buffer = m.get_signal("render_buffer")
        corruption = m.get_signal("corruption")
        render = m.get_signal("render")
        lcd = m.get_signal("lcd")
        queue_len = m.get_signal("queue_len")

        queue_len.set(len(Prj.VSYNC_QUEUE) - 1)

        if render.get() and lcd.get() and send_buffer.get() == render_buffer.get():
            corruption.set(corruption.get() + 1)
            print("corruption detected!")


if __name__ == '__main__':
    with StringIO() as f:
        machine = Machine(f, dump_signals=[
            'pollmon',
            'lcd',
            'render',
            'render_buffer',
            'send_buffer',
            'corruption',
            'queue_len'
        ], tick_per_mil=1)

        machine.add_updater(Prj.on_init)
        machine.add_updater(Prj.update_lcd)
        machine.add_updater(Prj.update_render)

        for i in range(int(machine.calc_sim_time(1000))):
            machine.update(machine.get_mil_per_tick())

        f.seek(0)

        draw(f)
