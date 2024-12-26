import cv2
import tkinter as tk
from tkinter import ttk
from pyphantom import Phantom, utils
import threading
import copy
import logging

# Настройка логирования
logging.basicConfig(
    filename="phantom_camera_test.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Инициализация объектов Phantom
ph = Phantom()
try:
    cam = ph.Camera(0)  # Подключение к первой доступной камере
    logging.info("Camera successfully connected.")
except Exception as e:
    logging.error(f"Failed to connect to camera: {e}")
    raise

# Профили настроек
profiles = {
    "Profile 1": {"resolution": (1024, 768), "frame_rate": 100, "exposure": 1000},
    "Profile 2": {"resolution": (640, 480), "frame_rate": 200, "exposure": 500},
    "Profile 3": {"resolution": (1920, 1080), "frame_rate": 50, "exposure": 2000},
}
current_profile = "Profile 1"  # Активный профиль

# Функции для управления настройками
def apply_profile_settings(profile_name):
    try:
        global current_profile
        current_profile = profile_name
        settings = profiles[profile_name]
        cam.resolution = settings["resolution"]
        cam.frame_rate = settings["frame_rate"]
        cam.exposure = settings["exposure"]
        logging.info(f"Applied {profile_name}: {settings}")
    except Exception as e:
        logging.error(f"Failed to apply profile {profile_name}: {e}")

def update_current_profile(resolution, frame_rate, exposure):
    try:
        profiles[current_profile] = {
            "resolution": resolution,
            "frame_rate": frame_rate,
            "exposure": exposure,
        }
        apply_profile_settings(current_profile)
        logging.info(f"Updated {current_profile}: {profiles[current_profile]}")
    except Exception as e:
        logging.error(f"Failed to update current profile: {e}")

def show_video():
    try:
        while True:
            frame = cam.get_live_image()  # Получение живого изображения
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)  # Преобразование для отображения
            cv2.imshow("Phantom Live Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
        logging.info("Video feed closed successfully.")
    except Exception as e:
        logging.error(f"Error in video feed: {e}")

def create_gui():
    """ Создание графического интерфейса. """
    root = tk.Tk()
    root.title("Phantom Camera Controller")

    # Выбор профиля
    def on_profile_change(event):
        selected_profile = profile_combobox.get()
        apply_profile_settings(selected_profile)

    profile_combobox = ttk.Combobox(root, values=list(profiles.keys()), state="readonly")
    profile_combobox.set(current_profile)
    profile_combobox.bind("<<ComboboxSelected>>", on_profile_change)
    profile_combobox.pack(pady=10)

    # Поля для редактирования параметров
    ttk.Label(root, text="Resolution (width, height)").pack()
    res_input = ttk.Entry(root)
    res_input.insert(0, f"{profiles[current_profile]['resolution']}")
    res_input.pack()

    ttk.Label(root, text="Frame Rate").pack()
    fr_input = ttk.Entry(root)
    fr_input.insert(0, profiles[current_profile]["frame_rate"])
    fr_input.pack()

    ttk.Label(root, text="Exposure").pack()
    exp_input = ttk.Entry(root)
    exp_input.insert(0, profiles[current_profile]["exposure"])
    exp_input.pack()

    # Кнопка для сохранения настроек текущего профиля
    def save_profile():
        try:
            resolution = tuple(map(int, res_input.get().strip("()").split(',')))
            frame_rate = float(fr_input.get())
            exposure = float(exp_input.get())
            update_current_profile(resolution, frame_rate, exposure)
        except Exception as e:
            logging.error(f"Failed to save profile: {e}")

    ttk.Button(root, text="Save Current Profile", command=save_profile).pack(pady=10)

    # Запуск видео потока в отдельном потоке
    threading.Thread(target=show_video, daemon=True).start()

    root.mainloop()

# Запуск GUI
try:
    create_gui()
    logging.info("GUI launched successfully.")
except Exception as e:
    logging.error(f"Error during GUI execution: {e}")

# Закрытие камеры при завершении
try:
    cam.close()
    ph.close()
    logging.info("Camera and Phantom instance closed successfully.")
except Exception as e:
    logging.error(f"Error during cleanup: {e}")
