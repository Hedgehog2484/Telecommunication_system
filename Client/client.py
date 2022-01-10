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


    def download_file(self, sock: socket.socket, gost: Gost_replacement) -> None:
        """
        Эта функция получает файл и его имя, а затем сохраняет его.
        :param sock: Объект сокета, через который будут получены данные.
        :param gost: Объект класса Gost, необходимый для дешифрования данных.
        :return: None
        """
        while True:
            file_name = sock.recv(1024)
            file_size = self.get_file_size(sock)

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


    def send_file(self, sock: socket.socket, gost: Gost_replacement) -> None:
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
