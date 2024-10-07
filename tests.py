import unittest  # Импортируем модуль для написания тестов
from unittest.mock import patch, MagicMock  # Импортируем инструменты для создания моков
import os  # Импортируем модуль для работы с файловой системой
from emulator import CommandLineEmulator  # Импортируем класс эмулятора командной строки
import tkinter as tk  # Импортируем tkinter для создания графического интерфейса
from tkinter import scrolledtext  # Импортируем виджет для прокручиваемого текстового поля

class TestCommandLineEmulator(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()  # Создаем главное окно Tkinter
        self.output_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='normal', height=20, width=50)  # Создаем текстовое поле для вывода
        self.output_area.pack(padx=10, pady=10)  # Упаковываем текстовое поле

        # Параметры для эмулятора
        self.username = "user"  
        self.hostname = "localhost"  
        self.vfs_path = "Files.tar"  # Путь к архиву виртуальной файловой системы
        self.log_path = "log.xml"  # Путь к лог-файлу
        self.startup_script = "startup_script.txt"  # Путь к стартовому скрипту

        # Создаем экземпляр эмулятора командной строки
        self.emulator = CommandLineEmulator(self.root, self.username, self.hostname, self.vfs_path, self.log_path, self.startup_script)
        self.emulator.output_area = self.output_area  # Присваиваем область вывода эмулятору
        self.emulator.current_directory = 'Files'  # Устанавливаем текущую директорию на папку Files

        # Убедимся, что файл Files.tar существует и содержит директории/файлы
        if not os.path.exists(self.vfs_path):
            raise FileNotFoundError(f"{self.vfs_path} does not exist.")

    @patch('os.listdir')  
    def test_ls(self, mock_listdir):
        mock_listdir.return_value = ['1', '2', '3']  # Задаем возвращаемые значения для ls
        self.emulator.ls()  # Вызываем метод ls
        output = self.emulator.output_area.get("1.0", "end-1c")  # Получаем текст из области вывода
        # Проверяем, что вывод содержит ожидаемые файлы и папки
        self.assertIn("1", output)
        self.assertIn("2", output)  
        self.assertIn("3", output)  

    @patch('os.listdir')   
    def test_ls_with_argument(self, mock_listdir):
        # Устанавливаем текущую директорию на виртуальный путь в эмуляторе
        self.emulator.current_directory = 'Files/1'  # Устанавливаем текущую директорию в виртуальной файловой системе
        mock_listdir.return_value = ['1.1', '1.2']  # Задаем возвращаемые значения для ls
        self.emulator.ls()  # Вызываем метод ls без аргумента
        output = self.emulator.output_area.get("1.0", "end-1c")  # Получаем текст из области вывода
        # Проверяем, что вывод содержит ожидаемые папки
        self.assertIn("1.1", output)
        self.assertIn("1.2", output)    

    def test_cd_valid_directory(self):
        self.emulator.current_directory = os.getcwd()  # Устанавливаем текущую директорию
        self.emulator.command_input.insert(0, 'cd Files/1')  # Вводим команду cd
        self.emulator.cd()  # Вызываем метод cd
        # Проверяем, что текущая директория изменилась на относительный путь
        self.assertEqual(self.emulator.current_directory, 'Files/1')

    def test_cd_invalid_directory(self):
        self.emulator.command_input.insert(0, 'cd NonExistentDir')  # Вводим несуществующую директорию
        self.emulator.cd()  # Вызываем метод cd
        output = self.emulator.output_area.get("1.0", "end-1c")  # Получаем текст из области вывода
        # Проверяем сообщение об ошибке
        self.assertIn("cd: no such directory: NonExistentDir", output)

    def test_exit(self):
        with patch('tkinter.Tk.destroy') as mock_destroy:  # Мокаем метод destroy
            self.emulator.exit()  # Вызываем метод exit
            mock_destroy.assert_called_once()  # Проверяем, что метод destroy был вызван один раз

    @patch('os.makedirs')  
    def test_mkdir_valid_directory(self, mock_makedirs):
        self.emulator.command_input.insert(0, 'mkdir NewFolder')  # Вводим команду mkdir
        self.emulator.mkdir()  # Вызываем метод mkdir
        # Проверяем, что функция os.makedirs была вызвана с правильным путем
        mock_makedirs.assert_called_once_with(os.path.join(self.emulator.current_directory, 'NewFolder'))

    @patch('os.makedirs') 
    def test_mkdir_directory_exists(self, mock_makedirs):
        mock_makedirs.side_effect = FileExistsError  # Задаем ошибку, если директория существует
        self.emulator.command_input.insert(0, 'mkdir 1')  # Вводим команду mkdir
        self.emulator.mkdir()  # Вызываем метод mkdir
        output = self.emulator.output_area.get("1.0", "end-1c")  # Получаем текст из области вывода
        # Проверяем сообщение об ошибке
        self.assertIn("mkdir: cannot create directory '1': File exists", output)  # Проверяем, что сообщение об ошибке присутствует

    @patch('os.path.isdir') 
    @patch('tarfile.open') 
    def test_wc_valid_file(self, mock_open, mock_isdir):
        mock_isdir.return_value = False  # Указываем, что это файл
        mock_file = MagicMock()  # Создаем мок для файла
        mock_file.read.return_value = "жль44мт аз1о3к зо1"  # Задаем содержимое файла
        mock_open.return_value.__enter__.return_value.extractfile.return_value = mock_file  # Настраиваем возврат файла
        
        self.emulator.command_input.insert(0, 'wc Files/3/3.1.txt')  # Вводим команду wc
        self.emulator.wc()  # Вызываем метод wc
        output = self.emulator.output_area.get("1.0", "end-1c")  # Получаем текст из области вывода

        # Подсчитываем строки, слова и символы
        lines = mock_file.read.return_value.splitlines()  # Разбиваем содержимое на строки
        word_count = len(mock_file.read.return_value.split())  # Подсчитываем количество слов
        char_count = len(mock_file.read.return_value)  # Подсчитываем количество символов

        # Проверяем, что вывод содержит ожидаемые результаты
        self.assertIn(f"{len(lines)} lines, {word_count} words, {char_count} characters in 'Files/3/3.1.txt'", output)

    @patch('os.path.isdir')  
    @patch('tarfile.open')  
    def test_wc_file_not_found(self, mock_open, mock_isdir):
        mock_isdir.return_value = False  # Указываем, что это не файл
        self.emulator.command_input.insert(0, 'wc non_existent_file.txt')  # Вводим команду wc
        self.emulator.wc()  # Вызываем метод wc
        output = self.emulator.output_area.get("1.0", "end-1c")  # Получаем текст из области вывода
        # Проверяем сообщение об ошибке
        self.assertIn("wc: non_existent_file.txt: No such file or directory", output)

    @patch('os.path.isdir')  
    @patch('tarfile.open')  
    def test_tree_valid_directory(self, mock_open, mock_isdir):
        mock_isdir.return_value = True  # Указываем, что это директория
        mock_open.return_value.__enter__.return_value.getmembers.return_value = [
            MagicMock(name='3', isdir=lambda: True),  # Мок для директории
            MagicMock(name='3.1.txt', isdir=lambda: False)  # Мок для файла
        ]  # Создаем моки для элементов директории

        self.emulator.command_input.insert(0, 'tree')  # Вводим команду tree
        self.emulator.tree()  # Вызываем метод tree
        output = self.emulator.output_area.get("1.0", "end-1c")  # Получаем текст из области вывода
        # Проверяем, что вывод содержит ожидаемые элементы
        self.assertIn("3", output)
        self.assertIn("3.1.txt", output)

    @patch('os.path.isdir')  
    @patch('tarfile.open') 
    def test_tree_invalid_directory(self, mock_open, mock_isdir):
        mock_isdir.return_value = False  # Указываем, что это не директория
        self.emulator.command_input.insert(0, 'tree NonExistentDir')  # Вводим команду tree с несуществующей директорией
        self.emulator.tree('NonExistentDir')  # Вызываем метод tree
        output = self.emulator.output_area.get("1.0", "end-1c")  # Получаем текст из области вывода
        # Проверяем сообщение об ошибке
        self.assertIn("tree: no such directory: NonExistentDir", output)

if __name__ == '__main__':
    unittest.main()  # Запускаем тесты

