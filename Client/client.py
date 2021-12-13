import os
import socket
import struct

from Cryptography import Gost_replacement


def get_file_size(sock: socket.socket) -> int:
    """
    Эта функция возвращает размер получаемого файла.
    :param sock: Объект сокета, через который будут получены данные.
    :return: Размер файла.
    """
    fmt = "<Q"
    expected_bytes = struct.calcsize(fmt)
    received_bytes = 0
    stream = bytes()

    while received_bytes < expected_bytes:
        chunk = sock.recv(expected_bytes - received_bytes)
        stream += chunk
        received_bytes += len(chunk)

    return struct.unpack(fmt, stream)[0]


def download_file(sock: socket.socket, gost: Gost_replacement) -> None:
    """
    Эта функция получает файл и его имя, а затем сохраняет его.
    :param sock: Объект сокета, через который будут получены данные.
    :param gost: Объект класса Gost, необходимый для дешифрования данных.
    :return: None
    """
    while True:
        file_name = sock.recv(1024)
        file_size = get_file_size(sock)

        with open("encrypted_file.txt", mode="wb") as f:
            received_bytes = 0

            while received_bytes < file_size:  # Сохраняем зашифрованные данные во временный файл.
                chunk = sock.recv(1024)
                if chunk:
                    f.write(chunk)
                    received_bytes += len(chunk)

        print("File was saved")

        with open("encrypted_file.txt", mode="rb") as file:  # Достаем зашифрованные данные из временного файла.
            data = file.read()
        cipher_text_blocks = gost.get_64bit_blocks(data)  # Разделяем зашифрованный текст на блоки.

        plain_text = b""
        for block in cipher_text_blocks:
            plain_text += gost.decrypt(int.from_bytes(block, byteorder="big"), gost.get_subkeys()).to_bytes(file_size, byteorder="big")

        with open(file_name, mode="wb") as file:  # Сохраняем дешифрованные данные в файл.
            file.write(plain_text)
        print("File decrypted")
        # TODO: прописать удаление временного файла (или обойтись совсем без него)


def send_file(sock: socket.socket, gost: Gost_replacement) -> None:
    """
    Отправляет файл, который был указан пользователем.
    :param sock: Объект сокета, через который будет происходить отправка данных.
    :param gost: Объект класса Gost, необходимый для зашифрования данных.
    :return: None
    """
    while True:
        filepath = input("Filepath: ")

        with open(filepath, mode="rb") as file:
            data = file.read()

        blocks = gost.get_64bit_blocks(data)  # Разделяем данные из файла на блоки.
        cipher_blocks = b""
        for block in blocks:  # Шифруем блоки.
            cipher_blocks += gost.encrypt(int.from_bytes(block, byteorder="big"), gost.get_subkeys()).to_bytes(8, byteorder="big")
        end_text = b""
        for i in cipher_blocks:
            if i != 0:
                end_text += i.to_bytes(1, "big")

        with open("cipher.txt", "wb") as file:  # Сохраняем во временный файл с зашифрованным текстом.
            file.write(end_text)

        filename = os.path.basename("cipher.txt")
        sock.send(filename.encode())
        file_size = os.path.getsize("cipher.txt")
        sock.sendall(struct.pack("<Q", file_size))
        with open("cipher.txt", mode="rb") as file:
            while read_bytes := file.read(1024):
                sock.sendall(read_bytes)

        print("File was sent")
        # TODO: прописать удаление временного файла (или обойтись совсем без него)


def main() -> None:
    """Устанавливает подключение к серверу и вызывает другие функции."""
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
    with socket.create_connection(('localhost', 9191)) as connection:
        send_file(connection, gost)  # Для получения файлов:
        # download_file(connection, gost)


main()
