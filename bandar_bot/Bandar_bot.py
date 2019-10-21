# coding=utf-8
import os
import socket
import json.decoder
import json
import time
import threading
import requests
from animations.subs import create_subscription_gif
import pickle
import chat_events

# todo Слово "Подписался" при подписке


FONT = "../fonts/VastShadow-Regular.ttf"


def get_private_data(filename: str) -> dict:
    """
    Загружает информацию для авторизации из pikle dump'a
    :param filename: путь до дампа данных
    :return: словарь с ключами username, client_id, token, channel
    """
    if not os.path.exists(filename):
        private_data = {}
        print("Введите имя пользователя бота: ")
        private_data["username"] = input()

        print("Введите client id: ")
        private_data["client_id"] = input()

        print("Введите токен пользователя: ")
        private_data["token"] = input()

        print("Введите название канала: ")
        private_data["channel"] = input()

        with open(filename, "wb") as f:
            pickle.dump(private_data, f)

    with open(filename, "rb") as f:
        return pickle.load(f)


def send_chat_msg(message):
    """
    Отправка сообщения в чат
    :param message: текст сообщения
    :return:
    """
    string = f"PRIVMSG #{USER_DATA['channel']} : {message} \n"
    connection.send(bytes(string, "UTF-8"))


def create_connection() -> socket.socket:
    """
    Функция присоединения к чату
    :return: сокет
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('irc.chat.twitch.tv', 6667))
    passw = "PASS " + USER_DATA["token"] + "\n"
    channel = "NICK " + USER_DATA["channel"] + "\n"
    sock.send(bytes(passw, "UTF-8"))
    sock.send(bytes(channel, "UTF-8"))
    sock.send(bytes(f"JOIN #{USER_DATA['channel']}\n", "UTF-8"))
    return sock


def income_message():
    """
        TODO разбить на классы ивентов и сделать общий обаботчик
    """
    event_handler = chat_events.EventHandler(send_chat_msg)
    while True:
        data = connection.recv(2024)
        datalist = list(
            str(data, "UTF-8").replace("\\r\\n", '\n').replace("b'", "").replace("'", "").split("\n"))  # govnocod
        for i in datalist:
            print(i)
            if "PING :tmi.twitch.tv" in i:
                connection.send(bytes("PONG :tmi.twitch.tv\n", "UTF-8"))
            if "PRIVMSG" in i:
                username = i[1:i.index("!")]
                useless, msg = i.split("#bandar_ban :")
                event_handler.message_handler(message=msg, author=username)


def announcer():
    event_handler = chat_events.EventHandler(send_chat_msg)
    while True:
        time.sleep(3000)
        event_handler.message_handler("!info", "")


def events():
    """
    TODO Фолловер парсер
    :return:
    """
    with open("cursor.txt", 'r') as f:
        last_follower_name = f.readline().replace("\n", "")
    while True:

        response = requests.get(url=f"https://api.twitch.tv/helix/users/follows?to_id=132946765",
                                headers={"Client-ID": USER_DATA["client_id"]})
        response = response.text

        followers_json = json.JSONDecoder().decode(response)
        print(followers_json)

        if len(followers_json["data"]) != 0:
            if followers_json["data"][0]["from_name"] == last_follower_name:
                time.sleep(180)
                continue
            else:
                for follower_data in followers_json["data"]:
                    name = follower_data["from_name"]
                    if name == last_follower_name:
                        break
                    create_subscription_gif(text=name, font_path=FONT, image_size=(800, 255))
                    send_chat_msg(message="@Bandar_ban, " + name + " подписался!\n")

            last_follower_name = followers_json["data"][0]["from_name"]

            with open("cursor.txt", 'w') as f:
                f.write(last_follower_name)
            time.sleep(120)


USER_DATA = get_private_data("private_data.pickle")
connection = create_connection()


def run_bot():
    announce = threading.Thread(target=announcer, name="My time thread", args=(), daemon=True)
    announce.start()

    message_reader = threading.Thread(target=income_message, name="Msg reader", args=(), daemon=True)
    message_reader.start()

    event_handler = threading.Thread(target=events, name="Event parser", daemon=True)
    event_handler.start()


if __name__ == '__main__':
    run_bot()
