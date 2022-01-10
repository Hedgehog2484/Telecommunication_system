import socket
from tkinter import Tk, BOTH, Label, Entry, StringVar, BooleanVar, Radiobutton, IntVar, DISABLED
from tkinter.ttk import Frame, Button, Style
from tkinter import filedialog as fd

from client import Client


class UI(Frame):
    def __init__(self, parent, gost_obj, client_obj):
        Frame.__init__(self, parent)
        self.parent = parent
        self.gost_obj = gost_obj
        self.client_obj = client_obj

        self.selected_radio_button = IntVar()  # Выбранная radio button (0 - отправка файла, 1 - получение).
        self.selected_radio_button.set(0)  # Дефолтное значение - отправка файла.

        self.filepath = StringVar()  # Путь к файлу для отправки.
        self.server_ip = StringVar()  # IP адрес сервера, на который будут отправляться данные.

        self.init_UI()  # Инициализируем интерфейс.
        self.center_window()  # Центрируем окно.

    def init_UI(self):
        """Основной метод инициализации интерфейса."""
        self.parent.title("Telecommunication system")  # Установка заголовка окна.
        self.style = Style()  # Установка стиля окна.
        self.style.theme_use("default")  # Установка темы интерфейса.
        self.pack()

        self.create_ip_address_input_field()  # Поле ввода IP.
        self.create_filepath_field()  # Поле и кнопка выбора файла.
        self.create_mode_radio_buttons()  # Кнопки режима работы.
        self.create_start_button()  # Кнопка запуска.

    def create_ip_address_input_field(self):
        """Создание поля для ввода IP адреса сервера."""
        # Подпись к полю:
        label_input_server_ip = Label(self, text="IP адрес сервера: ")
        label_input_server_ip.grid(column=0, row=0)

        # Поле для ввода:
        entry_server_ip = Entry(self, width=20, textvariable=self.server_ip)
        entry_server_ip.grid(column=1, row=0, padx=10)

    def create_filepath_field(self):
        """Создание поля и кнопки для выбора файла для отправки."""
        # Подпись к полю:
        label_input_filepath = Label(self, text="Путь к файлу: ")
        label_input_filepath.grid(column=0, row=1)

        # Поле для ввода:
        self.entry_filepath = Entry(self, width=30, textvariable=self.filepath)
        self.entry_filepath.grid(column=1, row=1, padx=10)

        # Кнопка открытия диалогового окна для выбора файла к отправке:
        button_select_file = Button(text="Выбрать файл", command=self.select_file)
        button_select_file.pack()

    def create_mode_radio_buttons(self):
        """Создание кнопок для выбора режимма работы (отправка или получение файла)."""
        r_button_send = Radiobutton(text="Отправить файл", variable=self.selected_radio_button, value=0)
        r_button_download = Radiobutton(text="Принять файл", variable=self.selected_radio_button, value=1)
        r_button_send.pack()
        r_button_download.pack()

    def create_start_button(self):
        """Создание кнопки запуска основных процессов приложения."""
        check_mode_button = Button(text="Продолжить", command=self.check_radiobuttons)
        check_mode_button.pack()

    def check_radiobuttons(self):
        checked_radio_button = self.selected_radio_button.get()
        if checked_radio_button == 0 and self.filepath != "" and self.server_ip.get() != "":
            # Отправка файла:
            with socket.create_connection((self.server_ip.get(), 9191)) as connection:
                self.client_obj.send_file(connection, self.gost_obj)

        elif checked_radio_button == 1 and self.server_ip.get() != "":
            # Получение файлов:
            with socket.create_connection((self.server_ip.get(), 9191)) as connection:
                self.client_obj.download_file(connection, self.gost_obj)

    def select_file(self):
        filepath = fd.askopenfilename(
            filetypes=(("TXT files", "*.txt"),
                       ("All files", "*.*"))
        )
        self.filepath = filepath
        self.entry_filepath.insert(0, filepath)

    def center_window(self):
        """Устанавливает окно в центре экрана."""
        weight = 390
        height = 200

        screen_weight = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()

        pos_x = (screen_weight - weight) / 2
        pos_y = (screen_height - height) / 2
        self.parent.geometry('%dx%d+%d+%d' % (weight, height, pos_x, pos_y))


def main():
    key = 67251403547312709632341550862392194146995365498083999511474347784065662509762  # Пример ключа.

    sbox = (
        ([3, 5, 6, 1, 0, 8, 14, 10, 2, 11, 9, 12, 13, 4, 7, 15]),
        ([6, 4, 15, 5, 10, 7, 0, 2, 14, 11, 8, 13, 1, 12, 3, 9]),
        ([12, 7, 2, 1, 8, 9, 11, 5, 15, 6, 10, 4, 3, 14, 0, 13]),
        ([6, 10, 5, 14, 1, 4, 15, 7, 12, 11, 2, 9, 8, 3, 13, 0]),
        ([6, 0, 7, 14, 3, 4, 13, 8, 11, 15, 10, 5, 12, 2, 1, 9]),
        ([13, 1, 15, 5, 3, 14, 7, 2, 0, 4, 6, 8, 12, 9, 10, 11]),
        ([9, 14, 4, 2, 8, 10, 15, 6, 0, 12, 5, 13, 3, 11, 7, 1]),
        ([8, 9, 12, 10, 6, 14, 2, 3, 13, 1, 7, 0, 5, 11, 15, 4])
    )  # Пример S-блока.

    gost = Gost_replacement(key, sbox)
    client = Client()

    root = Tk()
    # root.geometry("250x150+300+300")  # Ширина Х высота + координаты на экране.
    UI(root, gost, client)
    root.mainloop()


if __name__ == '__main__':
    main()
