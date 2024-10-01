<h1>Задание №1</h1>

**Вариант №6**

Разработать эмулятор для языка оболочки ОС. Необходимо сделать работу эмулятора как можно более похожей на сеанс shell в UNIX-подобной ОС. Эмулятор должен запускаться из реальной командной строки, а файл с виртуальной файловой системой не нужно распаковывать у пользователя. Эмулятор принимает образ виртуальной файловой системы в виде файла формата tar. Эмулятор должен работать в режиме GUI.
Ключами командной строки задаются:

•Имя пользователя для показа в приглашении к вводу.

•Имя компьютера для показа в приглашении к вводу.

•Путь к архиву виртуальной файловой системы.

•Путь к лог-файлу.

•Путь к стартовому скрипту.

Лог-файл имеет формат xml и содержит все действия во время последнего сеанса работы с эмулятором. Для каждого действия указаны дата и время. Для каждого действия указан пользователь.
Стартовый скрипт служит для начального выполнения заданного списка команд из файла.

Необходимо поддержать в эмуляторе команды ls, cd и exit, а также следующие команды:

1.tree.

2.mkdir.

3.wc.

Все функции эмулятора должны быть покрыты тестами, а для каждой из поддерживаемых команд необходимо написать 2 теста.

<h2>Описание функций</h2>

•**__init__(self, root, username, hostname, vfs_path, log_path, startup_script)** - создание открывающегося окна

•**load_vfs(self)** - загрузка виртуальной файловой системы

•**log_action(self, action)** - логирование действий

•**process_command(self, event=None)** - выполнение введённой команды

•**ls(self)** - получение и вывод списка файлов в текущем каталоге

•**cd(self)** - изменение директории

•**exit(self)** - выход из эмулятора

•**tree(self)** - отображение структуры каталогов и файлов, а также их количество

•**mkdir(self)** - создание новых директорий

•**wc(self)** - подсчёт числа строк, слов и символов в указанном файле

•**run_startup_script(self)** - выполнение стартового скрипта
