import os
import random
from threading import Timer


class EventHandler:
    def __init__(self, send_message_func):

        self.send_message_func = send_message_func
        self.events = {}
        self.read_simple_commands("cmd.txt")
        self.events["!rng"] = Randomizer(self.send_message_func)
        self.events["!v"] = Vote(self.send_message_func)

    def read_simple_commands(self, filename: str):
        """
        Считывает простые (с заданым текстовым ответом) из файла
        :param filename: имя файла с коммандами
        :return:
        """
        # Проверка наличия файла
        if not os.path.exists(filename):
            open(filename, 'w').close()
            return

        cmd_data = []

        with open(filename, "r", -1, "UTF-8") as f:
            for line in f:
                print(line)
                if line.count("|") != 2:
                    print("Неверное написание комманды")
                    continue
                cmd_data.append(line.split("|"))

        for command in cmd_data:
            trigger = command[0].replace("\ufeff", "")
            addressed = command[1]
            text = command[2]

            if not (addressed == "No" or addressed == "Yes"):
                print("Неверное написание комманды")
                continue

            addressed = True if addressed == "Yes" else False
            self.events[trigger] = SimpleMessage(text, addressed, self.send_message_func)

    def message_handler(self, message: str, author: str):
        words = message.split()
        first_word = words[0]

        if first_word in self.events.keys():
            self.events[first_word].process_message(message, author)


class SimpleMessage:
    """
    Класс для обоботки сообщений вида комманда -> текстовый ответ
    """

    def __init__(self, response_text: str, addressed: bool, send_message_func):
        """

        :param response_text: текст с ответом на комманду
        :param addressed: указывать ли в ответе автора сообщения
        """
        self.send_message_func = send_message_func
        self.response_text = response_text
        self.addressed = addressed

    def process_message(self, message: str, author: str):
        """
        Функция обработки входящего сообщения
        :param author:
        :param message:
        :return:
        """
        if self.addressed:
            response = "@" + author + ", " + self.response_text
        else:
            response = self.response_text

        self.send_message_func(response)


class Randomizer:
    """
    Класс генерирующий случаное значение. Если имеется два параметра, то в диапазоне между ними, если без параметров
     то значение от 0 до 100.
    """

    def __init__(self, send_message_func):
        self.name = "Randomizer"
        self.trigger = "!rng"
        self.send_message_func = send_message_func

    def process_message(self, message: str, author: str):
        tokens = message.split()
        response = f"@{author}, некорректный ввод"
        if len(tokens) == 3:
            try:
                start = int(tokens[1])
                finish = int(tokens[2])
                response = random.randint(start, finish)
            except:
                pass
        if len(tokens) == 1:
            response = random.randint(0, 100)
        self.send_message_func(response)


class Vote:

    def __init__(self, send_message_func):
        self.send_message_func = send_message_func
        self.name = "Vote"
        self.trigger = "!v"
        self.timer = -1
        self.votes = {}
        self.title = ""
        self.timer_checker()

    def timer_checker(self):
        if self.timer != -1:
            self.timer -= 1
        if self.timer == 0:
            self.end_of_vote()
        timer = Timer(1, self.timer_checker)
        timer.start()

    def end_of_vote(self):
        winner = ["НИКТО НЕ ГОЛОСУЕТ(((((", 0]
        for key, votes_list in self.votes.items():
            if len(votes_list) > winner[1]:
                winner = [key, len(votes_list)]

        self.send_message_func(f"Победителем голосвания {self.title} является {winner[0]} с результатом {winner[1]}")
        self.timer = -1
        self.votes = {}
        self.title = ""

    def process_message(self, message: str, author: str):
        tokens = message.split()
        if len(tokens) > 4 and author == "bandar_ban":
            self.title = tokens[1]
            self.timer = int(tokens[2])
            votes = tokens[3:]
            for vote in votes:
                self.votes[vote] = []
            self.send_message_func(
                f"Начинается голосование: {self.title}. Варианты: {', '.join(i for i in list(self.votes.keys()))}")

        if len(tokens) == 2:
            vote = tokens[1]
            if vote in self.votes.keys():
                for index, item in self.votes.items():
                    if author in item:
                        item.remove(author)
                self.votes[vote].append(author)
