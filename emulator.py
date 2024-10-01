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
        self.command_input = tk.Entry(self.frame, width=50, bg='black', fg='white')  # Поле ввода с черным фоном и белым текстом
        self.command_input.pack(padx=10, pady=10, fill=tk.X)  # Упаковываем поле ввода, чтобы оно занимало всю ширину
        self.command_input.bind('<Return>', self.process_command)  # Привязываем нажатие Enter к обработке команды
        
        # Создание кнопки
        self.submit_button = tk.Button(root, text="Submit", command=self.process_command, bg='black', fg='white')  # Кнопка с черным фоном и белым текстом
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
        command = self.command_input.get().strip()  # Получаем текст из поля ввода
        if command:
            self.output_area.config(state='normal')  # Разрешаем редактирование
            self.output_area.insert(tk.END, f"{self.username}@{self.hostname}:{self.current_directory} $ {command}\n")  # Выводим команду
            
            # Проверяем, какая команда была введена
            if command.startswith('cd '):
                self.cd()  # Вызов метода cd
            elif command == 'ls':
                self.ls()  # Вызов метода ls
            elif command == 'exit':
                self.exit()  # Вызов метода exit
            elif command == 'tree':
                self.tree()  # Вызов метода tree
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
        # Метод для реализации команды ls
        try:
            files = os.listdir(self.current_directory)  # Получаем список файлов в текущем каталоге
            self.output_area.insert(tk.END, "\n".join(files) + "\n")  # Выводим список файлов
            self.log_action("ls")  # Логируем действие
        except Exception as e:
            self.output_area.insert(tk.END, str(e) + "\n")  # В случае ошибки выводим сообщение об ошибке

    def cd(self):
        # Метод для реализации команды cd
        command_parts = self.command_input.get().strip().split(' ', 1)  # Разделяем ввод на команду и аргумент
        if len(command_parts) > 1:  # Проверяем, был ли указан новый путь
            new_directory = command_parts[1]  # Получаем путь к директории
            try:
                # Проверяем, является ли новый путь абсолютным или относительным
                if os.path.isabs(new_directory):
                    new_path = new_directory  # Если абсолютный путь, используем его
                else:
                    # Получаем абсолютный путь, комбинируя текущую директорию и новую
                    new_path = os.path.abspath(os.path.join(self.current_directory, new_directory))
                
                if os.path.isdir(new_path):  # Проверяем, существует ли директория
                    self.current_directory = new_path  # Обновляем текущую директорию
                    self.output_area.insert(tk.END, f"Changed directory to: {self.current_directory}\n")
                else:
                    self.output_area.insert(tk.END, f"cd: no such file or directory: {new_directory}\n")
            except Exception as e:
                self.output_area.insert(tk.END, f"cd: error: {str(e)}\n")
        else:
            self.output_area.insert(tk.END, "cd: missing argument\n")

    def exit(self):
        # Метод для выхода из эмулятора
        self.root.destroy()  # Закрываем графическое окно
        
    def tree(self):
        # Метод для реализации команды tree (отображение структуры каталогов и файлов)
        try:
            # Получаем список файлов и подкаталогов в текущей директории
            entries = os.listdir(self.current_directory)
        except PermissionError:
            # Обрабатываем ошибку доступа
            self.output_area.insert(tk.END, f"Permission denied: {self.current_directory}\n")
            return
        except Exception as e:
            # Обрабатываем другие ошибки
            self.output_area.insert(tk.END, f"Error accessing directory: {str(e)}\n")
            return

        total_files = 0  # Счетчик для общего количества файлов
        total_dirs = 0   # Счетчик для общего количества подкаталогов

        # Выводим содержимое текущей директории
        for entry in entries:
            entry_path = os.path.join(self.current_directory, entry)  # Формируем полный путь к элементу
            if os.path.isdir(entry_path):  # Если элемент является директорией
                self.output_area.insert(tk.END, f"[{entry}]\n")  # Выводим имя директории
                total_dirs += 1  # Увеличиваем счетчик подкаталогов
            else:  # Если элемент является файлом
                self.output_area.insert(tk.END, f"{entry}\n")  # Выводим имя файла
                total_files += 1  # Увеличиваем счетчик файлов

        # Выводим сводку
        self.output_area.insert(tk.END, f"\nTotal directories: {total_dirs}\n")  # Общее количество подкаталогов
        self.output_area.insert(tk.END, f"Total files: {total_files}\n")  # Общее количество файлов

    def mkdir(self):
        # Метод для реализации команды mkdir
        command_parts = self.command_input.get().strip().split(' ', 1)  # Разделяем ввод на команду и аргумент
        if len(command_parts) > 1:  # Проверяем, был ли указан новый путь
            new_directory = command_parts[1]  # Получаем имя новой директории
            try:
                # Формируем полный путь к новой директории
                new_path = os.path.join(self.current_directory, new_directory)
                os.makedirs(new_path)  # Создаем новую директорию
                self.output_area.insert(tk.END, f"Directory '{new_directory}' created.\n")  # Подтверждаем создание
            except FileExistsError:
                # Если директория уже существует, выводим сообщение об ошибке
                self.output_area.insert(tk.END, f"mkdir: cannot create directory '{new_directory}': File exists\n")
            except PermissionError:
                # Если возникает ошибка доступа, выводим сообщение об ошибке
                self.output_area.insert(tk.END, f"mkdir: cannot create directory '{new_directory}': Permission denied\n")
            except Exception as e:
                # Обработка других ошибок
                self.output_area.insert(tk.END, f"mkdir: error: {str(e)}\n")
        else:
            # Если аргумент не был указан, выводим сообщение о необходимости указания имени директории
            self.output_area.insert(tk.END, "mkdir: missing argument\n")

    def wc(self):
        # Метод для реализации команды wc
        command_parts = self.command_input.get().strip().split(' ', 1)  # Разделяем ввод на команду и аргумент
        if len(command_parts) > 1:  # Проверяем, был ли указан файл
            file_name = command_parts[1]  # Получаем имя файла
            try:
                # Формируем полный путь к файлу
                file_path = os.path.join(self.current_directory, file_name)
                with open(file_path, 'r', encoding='utf-8') as f:  # Открываем файл для чтения с указанием кодировки
                    content = f.read()  # Читаем содержимое файла
                    lines = content.splitlines()  # Разбиваем содержимое на строки
                    word_count = len(content.split())  # Подсчитываем количество слов
                    char_count = len(content)  # Подсчитываем количество символов
                    
                    # Выводим результаты в текстовое поле
                    self.output_area.insert(tk.END, f"{len(lines)} lines, {word_count} words, {char_count} characters in '{file_name}'\n")
            except FileNotFoundError:
                # Если файл не найден, выводим сообщение об ошибке
                self.output_area.insert(tk.END, f"wc: {file_name}: No such file or directory\n")
            except PermissionError:
                # Если нет прав доступа к файлу, выводим сообщение об ошибке
                self.output_area.insert(tk.END, f"wc: {file_name}: Permission denied\n")
            except Exception as e:
                # Обработка других ошибок, которые могут возникнуть
                self.output_area.insert(tk.END, f"wc: error: {str(e)}\n")
        else:
            # Если аргумент не был указан, выводим сообщение о необходимости указания имени файла
            self.output_area.insert(tk.END, "wc: missing argument\n")

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
