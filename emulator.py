import os  # Импортируем модуль для работы с файловой системой
import tarfile  # Импортируем модуль для работы с tar-архивами
import tkinter as tk  # Импортируем tkinter для создания графического интерфейса
from tkinter import scrolledtext  # Импортируем виджет для прокручиваемого текстового поля
import xml.etree.ElementTree as ET  # Импортируем модуль для работы с XML
from datetime import datetime  # Импортируем модуль для работы с датой и временем

class CommandLineEmulator:
    def __init__(self, root, username, hostname, vfs_path, log_path, startup_script):
        self.root = root  # Сохраняем ссылку на главное окно
        self.root.title("Command Line Emulator")  # Устанавливаем заголовок окна
        
        # Создание текстового поля для отображения вывода
        self.output_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', height=20, width=50)
        self.output_area.pack(padx=10, pady=10)
        
        # Создание поля для ввода команд
        self.command_input = tk.Entry(root, width=50)
        self.command_input.pack(padx=10, pady=10)
        self.command_input.bind('<Return>', self.process_command)  # Привязываем нажатие Enter к обработке команды
        
        # Создание кнопки
        self.submit_button = tk.Button(root, text="Submit", command=self.process_command)
        self.submit_button.pack(padx=10, pady=10)

        self.username = username  # Имя пользователя
        self.hostname = hostname  # Имя компьютера
        self.vfs_path = vfs_path  # Путь к архиву виртуальной файловой системы
        self.log_path = log_path  # Путь к лог-файлу
        self.startup_script = startup_script  # Путь к стартовому скрипту
        self.current_directory = "/"  # Текущий каталог, изначально корневой
        self.load_vfs()  # Загружаем виртуальную файловую систему
        self.commands = {  # Словарь доступных команд
            'ls': self.ls,
            'cd': self.cd,
            'exit': self.exit,
            'tree': self.tree,
            'mkdir': self.mkdir,
            'wc': self.wc,
        }
        self.run_startup_script()  # Запускаем стартовый скрипт

    def load_vfs(self):
        # Метод для загрузки виртуальной файловой системы
        with tarfile.open(self.vfs_path, 'r') as tar:  # Открываем tar-архив
            tar.extractall()  # Извлекаем все файлы из архива

    def log_action(self, action):
        # Метод для логирования действий
        tree = ET.Element("log")  # Создаем корневой элемент XML
        entry = ET.SubElement(tree, "entry")  # Создаем элемент для записи лога
        ET.SubElement(entry, "timestamp").text = datetime.now().isoformat()  # Добавляем временную метку
        ET.SubElement(entry, "user").text = self.username  # Добавляем имя пользователя
        ET.SubElement(entry, "action").text = action  # Добавляем действие
        tree_str = ET.tostring(tree, encoding='utf8', method='xml').decode()  # Преобразуем дерево в строку
        with open(self.log_path, 'a') as log_file:  # Открываем лог-файл для добавления
            log_file.write(tree_str + "\n")  # Записываем строку в файл

    def process_command(self, event=None):
        # Метод для выполнения введенной команды
        command = self.command_input.get()  # Получаем текст из поля ввода
        if command:
            self.output_area.config(state='normal')  # Разрешаем редактирование
            self.output_area.insert(tk.END, f"{self.username}@{self.hostname}:{self.current_directory} $ {command}\n")  # Выводим команду
            if command in self.commands:  # Проверяем, существует ли команда
                self.commands[command]()  # Выполняем команду
                self.output_area.insert(tk.END, f"Executed command: {command}\n")  # Выводим результат выполнения
            else:
                self.output_area.insert(tk.END, f"Command not found: {command}\n")  # Если команда не найдена, выводим сообщение
            self.output_area.config(state='disabled')  # Запрещаем редактирование
            self.output_area.yview(tk.END)  # Прокручиваем вниз
            self.command_input.delete(0, tk.END)  # Очищаем поле ввода

    def ls(self):
        # Метод для реализации команды ls
        try:
            files = os.listdir(self.current_directory)  # Получаем список файлов в текущем каталоге
            self.output_area.insert(tk.END, "\n".join(files) + "\n")  # Выводим список файлов
            self.log_action("ls")  # Логируем действие
        except Exception as e:
            self.output_area.insert(tk.END, str(e) + "\n")  # В случае ошибки выводим сообщение об ошибке

    def cd(self):
        # Метод для реализации команды cd
        pass

    def exit(self):
        # Метод для выхода из эмулятора
        self.root.quit()  # Закрываем графическое окно

    def tree(self):
        # Метод для реализации команды tree
        pass

    def mkdir(self):
        # Метод для реализации команды mkdir
        pass

    def wc(self):
        # Метод для реализации команды wc
        pass

    def run_startup_script(self):
        # Метод для выполнения стартового скрипта
        if os.path.exists(self.startup_script):  # Проверяем, существует ли файл скрипта
            with open(self.startup_script, 'r') as f:  # Открываем файл скрипта
                for line in f:  # Читаем файл построчно
                    self.process_command(line.strip())  # Выполняем каждую команду

if __name__ == "__main__":
    root = tk.Tk()  # Создаем главное окно приложения
    emulator = CommandLineEmulator(
        root,
        username="user",  # Указываем имя пользователя
        hostname="localhost",  # Указываем имя компьютера
        vfs_path="C:/Users/79372/Desktop/konf/homework_1/Files.tar",  # Указываем путь к архиву виртуальной файловой системы
        log_path="C:/Users/79372/Desktop/konf/homework_1/log.xml",  # Указываем путь к лог-файлу
        startup_script="path/to/startup_script.txt"  # Указываем путь к стартовому скрипту
    )
    root.mainloop()  # Запускаем главный цикл приложения
