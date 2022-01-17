import os
import socket
import struct

from Cryptography import Gost_replacement


class Client:
    def get_file_size(self, sock: socket.socket) -> int:
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


    def send_file(self, sock: socket.socket, gost: Gost_replacement, filepath: str) -> None:
        """
        Отправляет файл, который был указан пользователем.
        :param sock: Объект сокета, через который будет происходить отправка данных.
        :param gost: Объект класса Gost, необходимый для зашифрования данных.
        :return: None
        """
        with open(filepath, mode="rb") as file:
            data = file.read()  # Чтение файла.

        blocks = gost.get_64bit_blocks(data)  # Разделяем данные из файла на блоки.
        cipher_text = b""
        for block in blocks:  # Шифруем блоки:
            encrypted = gost.encrypt(int.from_bytes(block, byteorder="big"), gost.get_subkeys())
            cipher_text += encrypted.to_bytes((max(encrypted.bit_length(), 1) + 7) // 8, byteorder="big")

        with open("cipher", "wb") as file:  # Сохраняем во временный файл с зашифрованным текстом.
            file.write(cipher_text)

        filename = os.path.basename(filepath)
        sock.send(filename.encode())  # Получение и отправка имени файла.
        file_size = os.path.getsize("cipher")  # Получение размера зашифрованного файла.
        sock.sendall(struct.pack("<Q", file_size))
        with open("cipher", mode="rb") as file:
            while read_bytes := file.read(1024):
                sock.sendall(read_bytes)  # Чтение зашифрованного файла и отправка данных.
        os.remove("cipher")  # Удаляем временный файл.


    def download_file(self, sock: socket.socket, gost: Gost_replacement) -> None:
        """
        Эта функция получает файл и его имя, а затем сохраняет и дешифрует его.
        :param sock: Объект сокета, через который будут получены данные.
        :param gost: Объект класса Gost, необходимый для дешифрования данных.
        :return: None
        """
        file_name = sock.recv(1024)  # Получаем название файла.
        file_size = self.get_file_size(sock)  # Получаем размер файла.

        with open("cipher", mode="wb") as f:
            received_bytes = 0
            while received_bytes < file_size:  # Сохраняем все полученные зашифрованные данные во временный файл.
                chunk = sock.recv(1024)
                if chunk:
                    f.write(chunk)
                    received_bytes += len(chunk)

        with open("cipher", mode="rb") as file:
            data = file.read()  # Читаем зашифрованные данные из временного файла.

        cipher_text_blocks = gost.get_64bit_blocks(data)  # Разделяем зашифрованный текст на блоки.
        plain_text = b""
        for block in cipher_text_blocks:  # Процесс дешифрования блоков:
            decrypted = gost.decrypt(int.from_bytes(block, byteorder="big"), gost.get_subkeys())
            plain_text += decrypted.to_bytes((max(decrypted.bit_length(), 1) + 7) // 8, byteorder="big")

        end_text = b""
        for i in plain_text:  # Очищаем полученное исходное сообщение от мусора.
            if i != 1 and i != 0:
                end_text += i.to_bytes((max(i.bit_length(), 1) + 7) // 8, "big")

        with open(file_name, mode="wb") as file:  # Сохраняем дешифрованные данные в файл.
            file.write(end_text)
        os.remove("cipher")  # Удаление временного файла.
