import threading
import time

poll_flag = 0
buffer_index = 0
send_index = 1
mipi_busy_flag = 0
render_flag = 0

sync_sig = True


def wait(t):
    time.sleep(t / 1000)


def te_intr():
    global poll_flag, send_index, buffer_index, mipi_busy_flag
    poll_flag = 1
    send_index = buffer_index

    mipi_busy_flag = 1


def frame_done():
    global mipi_busy_flag
    mipi_busy_flag = 0


def loop_lcd_c():
    while sync_sig:
        te_intr()
        wait(35)
        frame_done()
        wait(7)


def loop_render():
    global poll_flag, buffer_index, render_flag
    while sync_sig:
        if poll_flag:
            poll_flag = 0
        render_flag = 1
        wait(15)  # render to buffer
        buffer_index = 1 - buffer_index
        render_flag = 0


def loop_probe():
    global sync_sig
    global poll_flag, buffer_index, render_flag
    count = 0
    try:
        with open("log", "w") as f:
            while sync_sig:
                if count == 80000:
                    sync_sig = False
                f.write(f"{poll_flag} {buffer_index} {send_index} {mipi_busy_flag} {render_flag}\n")
                print(render_flag)
                wait(0.1)
                count += 1
    except Exception:
        f.close()


l_lcd_t = threading.Thread(target=loop_lcd_c)
l_render_t = threading.Thread(target=loop_render)
l_probe_t = threading.Thread(target=loop_probe)

l_lcd_t.start()
l_render_t.start()
l_probe_t.start()

l_probe_t.join()
