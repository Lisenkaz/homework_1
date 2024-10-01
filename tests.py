import unittest  # Импортируем модуль для написания и выполнения тестов
from unittest.mock import patch, MagicMock  # Импортируем необходимые инструменты для создания моков
import os  # Импортируем модуль для работы с файловой системой
from emulator import CommandLineEmulator  # Импортируем класс эмулятора командной строки
import tkinter as tk  # Импортируем tkinter для создания графического интерфейса
from tkinter import scrolledtext  # Импортируем виджет для прокручиваемого текстового поля

class TestCommandLineEmulator(unittest.TestCase):
    def setUp(self):
        # Метод, который выполняется перед каждым тестом
        self.root = tk.Tk()  # Создаем главное окно Tkinter
        self.output_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='normal', height=20, width=50)
        # Создаем прокручиваемое текстовое поле для отображения вывода
        self.output_area.pack(padx=10, pady=10)  # Упаковываем текстовое поле в окно

        # Устанавливаем параметры для эмулятора
        self.username = "user"  # Имя пользователя
        self.hostname = "localhost"  # Имя компьютера
        self.vfs_path = "Files.tar"  # Путь к архиву виртуальной файловой системы
        self.log_path = "log.xml"  # Путь к лог-файлу
        self.startup_script = "startup_script.txt"  # Путь к стартовому скрипту

        # Создаем экземпляр эмулятора с необходимыми параметрами
        self.emulator = CommandLineEmulator(self.root, self.username, self.hostname, self.vfs_path, self.log_path, self.startup_script)
        self.emulator.output_area = self.output_area  # Присваиваем output_area реальный объект
        self.emulator.current_directory = os.getcwd()  # Устанавливаем текущую директорию

        # Создаем тестовую директорию для тестов
        os.makedirs(os.path.join(self.emulator.current_directory, 'Documents'), exist_ok=True)

    @patch('os.listdir')
    def test_ls(self, mock_listdir):
        mock_listdir.return_value = ['file1.txt', 'file2.txt', 'folder1']  # Устанавливаем возвращаемое значение для ls
        self.emulator.ls()  # Выполняем команду ls
        output = self.emulator.output_area.get("1.0", "end-1c")  # Получаем вывод из текстового поля
        self.assertIn("file1.txt", output)  # Проверяем, что файл присутствует в выводе
        self.assertIn("file2.txt", output)  # Проверяем, что файл присутствует в выводе
        self.assertIn("folder1", output)  # Проверяем, что папка присутствует в выводе

    @patch('os.listdir')
    def test_ls_empty_directory(self, mock_listdir):
        mock_listdir.return_value = []  # Устанавливаем возвращаемое значение для пустой директории
        self.emulator.ls()  # Выполняем команду ls
        output = self.emulator.output_area.get("1.0", "end-1c")  # Получаем вывод из текстового поля
        self.assertEqual(output.strip(), "")  # Ожидаем пустой вывод

    def test_cd_valid_directory(self):
        self.emulator.current_directory = os.getcwd()  # Устанавливаем текущую директорию
        self.emulator.command_input.insert(0, 'cd Documents')  # Имитация ввода команды
        self.emulator.cd()  # Выполняем команду cd
        # Проверяем, что текущая директория изменилась на Documents
        self.assertEqual(self.emulator.current_directory, os.path.join(os.getcwd(), 'Documents'))

    def test_cd_invalid_directory(self):
        self.emulator.command_input.insert(0, 'cd NonExistentDir')  # Имитация ввода команды
        self.emulator.cd()  # Выполняем команду
        output = self.emulator.output_area.get("1.0", "end-1c")  # Получаем вывод из текстового поля
        # Проверяем, что сообщение об ошибке присутствует
        self.assertIn("cd: no such file or directory: NonExistentDir", output)

    def test_exit(self):
        with patch('tkinter.Tk.destroy') as mock_destroy:  # Патчим метод destroy
            self.emulator.exit()  # Вызываем метод exit
            mock_destroy.assert_called_once()  # Проверяем, что метод destroy был вызван один раз

    @patch('os.makedirs')
    def test_mkdir_valid_directory(self, mock_makedirs):
        self.emulator.command_input.insert(0, 'mkdir NewFolder')  # Имитация ввода команды
        self.emulator.mkdir()  # Выполняем команду mkdir
        # Проверяем, что makedirs был вызван с правильным путем
        mock_makedirs.assert_called_once_with(os.path.join(self.emulator.current_directory, 'NewFolder'))

    @patch('os.makedirs')
    def test_mkdir_directory_exists(self, mock_makedirs):
        mock_makedirs.side_effect = FileExistsError  # Устанавливаем исключение для существующей директории
        self.emulator.command_input.insert(0, 'mkdir ExistingFolder')  # Имитация ввода команды
        self.emulator.mkdir()  # Выполняем команду
        output = self.emulator.output_area.get("1.0", "end-1c")  # Получаем вывод из текстового поля
        # Проверяем, что сообщение об ошибке присутствует
        self.assertIn("mkdir: cannot create directory 'ExistingFolder': File exists", output)

    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='line1\nline2\nline3')
    def test_wc(self, mock_file):
        self.emulator.command_input.insert(0, 'wc testfile.txt')  # Имитация ввода команды
        self.emulator.wc()  # Выполняем команду wc
        output = self.emulator.output_area.get("1.0", "end-1c")  # Получаем вывод из текстового поля
        # Проверяем, что вывод соответствует ожиданиям
        self.assertIn("3 lines, 3 words, 17 characters", output)

    @patch('builtins.open')  
    def test_wc_file_not_found(self, mock_file):
        mock_file.side_effect = FileNotFoundError  # Устанавливаем исключение для несуществующего файла
        self.emulator.command_input.insert(0, 'wc non_existing_file.txt')  # Имитация ввода команды
        self.emulator.wc()  # Выполняем команду wc
        output = self.emulator.output_area.get("1.0", "end-1c")  # Получаем вывод из текстового поля
        # Проверяем, что сообщение об ошибке присутствует
        self.assertIn("wc: non_existing_file.txt: No such file or directory", output)

if __name__ == "__main__":
    unittest.main()  # Запускаем тесты
