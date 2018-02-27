import socket
import json.decoder
import json
import time
import threading
import requests


class TestLog:
    def __init__(self):
        with open("private.txt", 'r', -1, "UTF-8") as file:
            private_data = []
            for line in file:
                private_data.append(line)
        self.username = private_data[0]
        self.client_id = private_data[1]
        self.token = private_data[2]
        self.channel = private_data[3]


def read_from_file(filename):
    try:
        commands = []
        with open(filename, "r", -1, "UTF-8") as f:
            for line in f:
                commands.append(line.split("|"))
            commands[0][0] = "!info"
            for i in commands:
                i[0] = i[0].upper()
                print(i[0])
        answ = {commands[j][0]: (commands[j][1], commands[j][2]) for j in range(len(commands))}

        return answ
    except FileNotFoundError:
        print("no file")


def send_chat_msg(message):
    string = "PRIVMSG #bandar_ban :" + message  # + "\n"
    connection.send(bytes(string, "UTF-8"))


def create_connection():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('irc.chat.twitch.tv', 6667))
    passw = "PASS " + TestLog.token + "\n"
    channel = "NICK " + TestLog.channel + "\n"
    sock.send(bytes(passw, "UTF-8"))
    sock.send(bytes(channel, "UTF-8"))
    sock.send(bytes("JOIN #bandar_ban\n", "UTF-8"))
    return sock


def income_message():
    while True:
        data = connection.recv(2024)
        datalist = list(
            str(data, "UTF-8").replace("\\r\\n", '\n').replace("b'", "").replace("'", "").split("\n"))  # govnocod
        for i in datalist:
            print(i)
            if "PING :tmi.twitch.tv" in i:
                connection.send(bytes("PONG :tmi.twitch.tv\n", "UTF-8"))
            if "PRIVMSG" in i:
                username = "@" + i[1:i.index("!")]
                useless, msg = i.split("#bandar_ban :")
                msg = msg[0:-1]
                msg = msg.upper()
                if msg in cmd:
                    if cmd[msg][0] == "No":
                        username = ""
                    send_chat_msg(username + " " + cmd[msg][1])


def announcer():
    while True:
        time.sleep(3000)
        send_chat_msg(cmd["!INFO"][1])


def events():
    with open("cursor.txt", 'r') as f:
        cursor = f.read()
    while True:
        time.sleep(1)
        r = requests.get(
            "https://api.twitch.tv/kraken/channels/bandar_ban/follows?client_id=" + TestLog.client_id + "&limit=1&direction=asc&cursor=" + str(
                cursor))
        r = (r.text)
        a = json.JSONDecoder().decode(r)
        # print(a)
        if a["_total"] != 0:
            cursor = a["_cursor"]
            with open("cursor.txt", 'w') as f:
                f.write(cursor)
            name = a["follows"][0]["user"]["display_name"]
            send_chat_msg("@Bandar_ban, " + name + " подписался!\n")


TestLog = TestLog()
connection = create_connection()
cmd = read_from_file("cmd.txt")

announce = threading.Thread(target=announcer, name="My time thread", args=(), daemon=True)
announce.start()

message_reader = threading.Thread(target=income_message, name="Msg reader", args=(), daemon=True)
message_reader.start()

#events = threading.Thread(target=events, name="What happend?", args=(), daemon=True)
#events.start()

while True:
    pass
