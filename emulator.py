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
        self.root.geometry("800x600")  # Устанавливаем фиксированный размер окна

         # Создаем контейнер для текстового поля и поля ввода
        self.frame = tk.Frame(root, bg='black')  # Создаем рамку с черным фоном
        self.frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)  # Упаковываем рамку, чтобы она занимала все доступное пространство
    
        # Создание текстового поля для отображения вывода
        self.output_area = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD, state='normal', height=20, width=50, bg='black', fg='white', insertbackground='white')  # Устанавливаем черный фон и белый текст
        self.output_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)  # Упаковываем текстовое поле, чтобы оно занимало все доступное пространство
        
        # Создание поля для ввода команд
        self.command_input = tk.Entry(self.frame, width=50, bg='black', fg='white', insertbackground='white')   # Поле ввода с черным фоном и белым текстом
        self.command_input.pack(padx=10, pady=10, fill=tk.X)  # Упаковываем поле ввода, чтобы оно занимало всю ширину
        self.command_input.bind('<Return>', self.process_command)  # Привязываем нажатие Enter к обработке команды
        
        # Устанавливаем фокус на поле ввода команд
        self.command_input.focus_set()  
        
        # Создание кнопки
        self.submit_button = tk.Button(root, text="Submit", command=self.process_command, bg='black', fg='white')  # Кнопка с черным фоном и белым текстом
        self.submit_button.pack(padx=10, pady=10)

        self.username = username  # Имя пользователя
        self.hostname = hostname  # Имя компьютера
        self.vfs_path = vfs_path  # Путь к архиву виртуальной файловой системы
        self.log_path = log_path  # Путь к лог-файлу
        self.startup_script = startup_script  # Путь к стартовому скрипту
        self.current_directory = "Files"  # Текущий каталог, изначально корневой
        # Создаем структуру для хранения содержимого tar файла
        self.files_in_vfs = {}  # Словарь для хранения файлов из tar
        self.load_files_from_tar()  # Загружаем файлы из tar
        self.commands = {  # Словарь доступных команд
            'ls': self.ls,
            'cd': self.cd,
            'exit': self.exit,
            'tree': self.tree,
            'mkdir': self.mkdir,
            'wc': self.wc,
        }
        self.run_startup_script()  # Запускаем стартовый скрипт

    def load_files_from_tar(self):
        # Загружаем файлы из tar архива в словарь
        with tarfile.open(self.vfs_path, 'r') as tar:  # Открываем tar файл
            for member in tar.getmembers():  # Для каждого члена архива
                self.files_in_vfs[member.name] = member  # Добавляем его в словарь
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
        command = self.command_input.get().strip()  # Получаем текст из поля ввода
        if command:
            self.output_area.config(state='normal')  # Разрешаем редактирование
            self.output_area.insert(tk.END, f"{self.username}@{self.hostname}:{self.current_directory} $ {command}\n")  # Выводим команду
            
            # Проверяем, какая команда была введена
            command_parts = command.split(' ', 1)  # Разделяем команду на первую часть (команда) и вторую (аргумент)
            cmd = command_parts[0]  # Первая часть - это команда
            arg = command_parts[1] if len(command_parts) > 1 else None  # Вторая часть - это аргумент, если он есть

            if command.startswith('cd '):
                self.cd()  # Вызов метода cd
            elif command.startswith('ls'):
                self.ls()                       
            elif command == 'exit':
                self.exit()  # Вызов метода exit
            elif cmd == 'tree':
                if arg:  # Если аргумент указан, передаем его в метод tree
                    self.tree(arg)
                else:
                    self.tree()  # Вызов метода tree без аргументов
            elif command.startswith('mkdir '):
                self.mkdir()  # Вызов метода mkdir
            elif command.startswith('wc '):
                self.wc()  # Вызов метода wc
            else:
                self.output_area.insert(tk.END, f"Command not found: {command}\n")  # Если команда не найдена

            self.output_area.config(state='disabled')  # Запрещаем редактирование
            self.output_area.yview(tk.END)  # Прокручиваем вниз
            self.command_input.delete(0, tk.END)  # Очищаем поле ввода

    def ls(self):
        # Метод для отображения содержимого текущей директории или указанной директории
        command_parts = self.command_input.get().strip().split(' ', 1)  # Разделяем команду на части
        target_directory = self.current_directory  # По умолчанию используем текущую директорию

        if len(command_parts) > 1:  # Если указана директория
            target_directory = command_parts[1]  # Сохраняем указанную директорию

        # Проверяем, существует ли указанная директория в виртуальной файловой системе
        if target_directory in self.files_in_vfs and self.files_in_vfs[target_directory].isdir():
            entries = [name for name in self.files_in_vfs.keys() if os.path.dirname(name) == target_directory]  # Получаем файлы в указанной директории
            if not entries:
                self.output_area.insert(tk.END, "No files found.\n")  # Если не найдено файлов
            else:
                self.output_area.insert(tk.END, "\n".join(entries) + "\n")  # Выводим файлы в области вывода
        else:
            self.output_area.insert(tk.END, f"ls: no such directory: {target_directory}\n")  # Сообщаем об ошибке

        self.log_action("ls")  # Логируем действие
            


    def cd(self):
        # Метод для смены директории
        command_parts = self.command_input.get().strip().split(' ', 1)  # Разделяем команду на части
        if len(command_parts) > 1:  # Если указана новая директория
            new_directory = command_parts[1]  # Сохраняем новую директорию
            if new_directory in self.files_in_vfs and self.files_in_vfs[new_directory].isdir():  # Проверяем, существует ли директория
                self.current_directory = new_directory  # Меняем текущую директорию
                self.output_area.insert(tk.END, f"Changed directory to: {self.current_directory}\n")  # Выводим сообщение
            else:
                self.output_area.insert(tk.END, f"cd: no such directory: {new_directory}\n")  # Сообщаем об ошибке
        else:
            self.output_area.insert(tk.END, "cd: missing argument\n")  # Сообщаем о недостатке аргументов

    def exit(self):
        # Метод для выхода из эмулятора
        self.root.destroy()  # Закрываем графическое окно
        
        
    def tree(self, directory=None, level=0):
        # Метод для реализации команды tree (отображение структуры каталогов и файлов)
        # Если директория не указана, используем текущую директорию
        if directory is None:
            directory = self.current_directory

        # Проверяем, что указанная директория существует в виртуальной файловой системе
        if directory in self.files_in_vfs and self.files_in_vfs[directory].isdir():
            # Получаем элементы в указанной директории
            entries = [name for name in self.files_in_vfs.keys() if os.path.dirname(name) == directory]
            if not entries:
                self.output_area.insert(tk.END, "No files found.\n")  # Если не найдено файлов
                return
            
            for entry in entries:
                # Отображаем элемент с отступом в зависимости от уровня вложенности
                self.output_area.insert(tk.END, " " * (level * 4) + f"{entry}\n")
                # Если элемент является директорией, рекурсивно вызываем tree для нее
                if self.files_in_vfs[entry].isdir():
                    self.tree(entry, level + 1)  # Увеличиваем уровень для вложенных директорий
        else:
            self.output_area.insert(tk.END, f"tree: no such directory: {directory}\n")  # Сообщаем об ошибке

    def mkdir(self):
        command_parts = self.command_input.get().strip().split(' ', 1)  # Разделяем ввод на команду и аргумент
        if len(command_parts) > 1:  # Проверяем, был ли указан новый путь
            new_directory = command_parts[1]  # Получаем имя новой директории
            new_path = os.path.join(self.current_directory, new_directory)  # Формируем полный путь

            # Проверяем, существует ли директория
            if new_path in self.files_in_vfs:
                self.output_area.insert(tk.END, f"mkdir: cannot create directory '{new_directory}': File exists\n")
                return

            try:
                os.makedirs(new_path)  # Создаем директорию на диске
                # Обновляем виртуальную файловую систему
                self.files_in_vfs[new_path] = tarfile.TarInfo(name=new_path)  # Добавляем новую директорию в словарь
                self.output_area.insert(tk.END, f"Directory '{new_directory}' created.\n")  # Подтверждаем создание
                self.log_action(f"mkdir: {new_directory}")  # Логируем действие
            except FileExistsError:
                self.output_area.insert(tk.END, f"mkdir: cannot create directory '{new_directory}': File exists\n")  # Сообщаем об ошибке
            except Exception as e:
                self.output_area.insert(tk.END, f"mkdir: error: {str(e)}\n")  # Обработка других ошибок
        else:
            self.output_area.insert(tk.END, "mkdir: missing argument\n")  # Если аргумент не был указан, выводим сообщение

    def wc(self):
        # Метод для подсчета строк, слов и символов в файле
        command_parts = self.command_input.get().strip().split(' ', 1)  # Разделяем ввод на команду и аргумент
        if len(command_parts) > 1:  # Проверяем, был ли указан файл
            file_name = command_parts[1]  # Получаем имя файла
            if file_name in self.files_in_vfs and not self.files_in_vfs[file_name].isdir():  # Проверяем, существует ли файл
                with tarfile.open(self.vfs_path, 'r') as tar:  # Открываем tar файл
                    file = tar.extractfile(file_name)  # Извлекаем файл
                    content = file.read()  # Читаем содержимое файла (это уже строка)
                    lines = content.splitlines()  # Разделяем содержимое на строки
                    word_count = len(content.split())  # Подсчитываем количество слов
                    char_count = len(content)  # Подсчитываем количество символов
                    
                    # Выводим результаты в текстовое поле
                    self.output_area.insert(tk.END, f"{len(lines)} lines, {word_count} words, {char_count} characters in '{file_name}'\n")
            else:
                self.output_area.insert(tk.END, f"wc: {file_name}: No such file or directory\n")  # Сообщаем об ошибке
        else:
            self.output_area.insert(tk.END, "wc: missing argument\n")  # Сообщаем о недостатке аргументов

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
        vfs_path="Files.tar",  # Указываем путь к архиву виртуальной файловой системы
        log_path="log.xml",  # Указываем путь к лог-файлу
        startup_script="startup_script.txt"  # Указываем путь к стартовому скрипту
    )
    root.mainloop()  # Запускаем главный цикл приложения
