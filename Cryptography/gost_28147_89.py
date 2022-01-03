from typing import List


class Gost_replacement:
    """
    Реализация алгоритма шифрования Гост 28147-89 'Магма' - способ простой замены.
    """
    def __init__(self, key: int, sbox: tuple):
        self.key = key
        self.sbox = sbox

    def get_64bit_blocks(self, plain_text: bytes) -> List[bytes]:
        """
        Эта функция разбивает исходный текст на 64-битные блоки и возвращает список с ними.
        :param plain_text: Открытый текст, который должен быть поделен на блоки.
        :return: Список 64-битных блоков.
        """
        text_lenght = int.from_bytes(plain_text, byteorder="big").bit_length()  # Считаем длину открытого текста.
        if text_lenght % 64 != 0:
            plain_text += b"\xf0" * ((64 - text_lenght % 64) // 8)
        blocks_list = []
        block = b""
        for byte in plain_text:
            if len(block) * 8 == 64:
                blocks_list.append(block)
                block = b""
            block += byte.to_bytes(2, byteorder="big")
        return blocks_list

    def get_subkeys(self) -> List[int]:
        """
        Разбивает 256-битный ключ на 8 подключей и возвращает их списком.
        :return: Список подключей.
        """
        return [(self.key >> (32 * i)) & 0xFFFFFFFF for i in range(8)]  # Разбиение ключа на 8 подключей.

    def f(self, text_part: int, subkey: int) -> int:
        """
        Функция f(Ai, Xi), используемая в сети Фейстеля.
        :param text_part: 32-битный блок кода, который будет прогоняться через алгоритм.
        :param subkey: Подключ текущего раунда.
        :return:
        """
        crypt_text = text_part ^ subkey
        result = 0
        for step in range(8):
            result |= ((self.sbox[step][(crypt_text >> (4 * step)) & 0b1111]) << (4 * step))
        return ((result << 11) | (result >> (32 - 11))) & 0xFFFFFFFF

    def encrypt(self, open_text: int, subkeys: list) -> int:
        """
        Функция зашифровки 64-битного блока открытого текста. Возвращает зашифрованный блок.
        :param open_text: Блок открытого текста, размером 64-бит.
        :param subkeys: Список подключей.
        :return: Число, являющееся результатом шифрования блока.
        """
        left_part = open_text >> 32  # Старшие биты.
        right_part = open_text & 0xFFFFFFFF  # Младшие биты.

        for i in range(24):  # 24 раунда с ключами К1-К8:
            temp_var = right_part
            right_part = left_part ^ self.f(right_part, subkeys[i % 8])
            left_part = temp_var
        for i in range(8):  # 8 раундов с ключами K8-K1:
            temp_var = right_part
            right_part = left_part ^ self.f(right_part, subkeys[7 - i])
            left_part = temp_var
        return (left_part << 32) | right_part  # Возвращаем соединенные части блока.

    def decrypt(self, close_text: int, subkeys: list):
        """
        Функция дешифрования 64-битного блока зашифрованного текста. Возвращает блок изначального текста.
        :param close_text: Зашифрованный блок, размером 64-бит.
        :param subkeys: Список подключей.
        :param sbox: S-блок.
        :return: Число, являющееся открытым (исходным) текстом.
        """
        left_part = close_text >> 32  # Старшие биты.
        right_part = close_text & 0xFFFFFFFF  # Младшие биты.
        # Раунды как при шифровании, но инвертированные:
        for i in range(8):
            temp_var = left_part
            left_part = right_part ^ self.f(left_part, subkeys[i])
            right_part = temp_var
        for i in range(24):
            temp_var = left_part
            left_part = right_part ^ self.f(left_part, subkeys[(7 - i) % 8])
            right_part = temp_var
        return (left_part << 32) | right_part  # Возвращаем блок расшифрованного сообщения.
