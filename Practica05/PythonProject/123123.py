import time
import threading
import ctypes
from ctypes import wintypes
import keyboard

# Настройки
PRESSES_PER_SECOND = 30
PRESS_INTERVAL = 1.0 / PRESSES_PER_SECOND

# Код пробела в Windows
VK_SPACE = 0x20

# Настройка SendInput
SendInput = ctypes.windll.user32.SendInput


# Структуры для эмуляции нажатий
class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
    ]


class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [
            ("ki", KEYBDINPUT),
            ("mi", ctypes.c_ulong * 3),
            ("hi", ctypes.c_ulong * 3),
        ]

    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", _INPUT)
    ]


def send_key_event(vk_code, key_down=True):
    extra = ctypes.c_ulong(0)
    flags = 0 if key_down else 0x0002  # KEYEVENTF_KEYUP

    ii = INPUT._INPUT()
    ii.ki = KEYBDINPUT(vk_code, 0, flags, 0, ctypes.pointer(extra))

    x = INPUT(1, ii)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


class SpaceRepeater:
    def __init__(self):
        self.active = False
        self.thread = None
        self.lock = threading.Lock()

    def worker(self):
        while True:
            with self.lock:
                if not self.active:
                    break

            send_key_event(VK_SPACE, True)
            send_key_event(VK_SPACE, False)
            time.sleep(PRESS_INTERVAL)

    def start(self):
        with self.lock:
            if not self.active:
                self.active = True
                self.thread = threading.Thread(target=self.worker)
                self.thread.daemon = True
                self.thread.start()

    def stop(self):
        with self.lock:
            self.active = False


def main():
    repeater = SpaceRepeater()

    def on_space_press(event):
        if event.name == 'space' and event.event_type == keyboard.KEY_DOWN:
            repeater.start()

    def on_space_release(event):
        if event.name == 'space' and event.event_type == keyboard.KEY_UP:
            repeater.stop()

    keyboard.hook(on_space_press)
    keyboard.hook(on_space_release)

    print("Программа запущена. Удерживайте пробел для быстрых нажатий.")
    print("Для выхода нажмите Ctrl+C")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nЗавершение работы...")
    finally:
        repeater.stop()
        keyboard.unhook_all()


if __name__ == "__main__":
    # Проверяем права администратора
    try:
        ctypes.windll.shell32.IsUserAnAdmin()
    except:
        print("Ошибка: Программа требует прав администратора!")
        input("Нажмите Enter для выхода...")
        exit(1)

    main()