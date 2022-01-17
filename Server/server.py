from socket import socket
from threading import Thread


def thread(this_client, other_client) -> None:
    """
    Эта функция запускается фоновыми потоками (на одного пользователя - один поток).
    :param this_client: Объект подключения пользователя, от которого будут получены данные.
    :param other_client: Объект подключения пользователя, которому будут пересланы полученные данные.
    :return: None
    """
    print("new thread")
    while True:
        data = this_client[0].recv(1024)
        if not data:
            break
        other_client[0].send(data)


def main() -> None:
    """Биндит сокет, запускает сервер, принимает пользовательские подключения и запускает фоновые потоки."""
    sock = socket()
    sock.bind(("", 9191))
    sock.listen(2)

    while True:
        conn1 = sock.accept()
        print("Client_1 connected")
        conn2 = sock.accept()
        print("Client_2 connected")
        first_thread = Thread(target=thread, args=(conn1, conn2))
        second_thread = Thread(target=thread, args=(conn2, conn1))

        first_thread.start()
        second_thread.start()


if __name__ == "__main__":
    main()
