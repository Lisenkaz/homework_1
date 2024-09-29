import tkinter as tk
from tkinter import scrolledtext

class CommandLineEmulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Command Line Emulator")
        
        # Создание текстового поля для отображения вывода
        self.output_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', height=20, width=50)
        self.output_area.pack(padx=10, pady=10)
        
        # Создание поля для ввода команд
        self.command_input = tk.Entry(root, width=50)
        self.command_input.pack(padx=10, pady=10)
        self.command_input.bind('<Return>', self.process_command)
        
        # Создание кнопки
        self.submit_button = tk.Button(root, text="Submit", command=self.process_command)
        self.submit_button.pack(padx=10, pady=10)

    def process_command(self, event=None):
        command = self.command_input.get()
        if command:
            self.output_area.config(state='normal')  # Разрешаем редактирование
            self.output_area.insert(tk.END, f"> {command}\n")  # Выводим введенную команду
            # Здесь можно добавить обработку команд, если необходимо
            self.output_area.insert(tk.END, f"Executed command: {command}\n")  # Пример вывода результата
            self.output_area.config(state='disabled')  # Запрещаем редактирование
            self.output_area.yview(tk.END)  # Прокручиваем вниз
            self.command_input.delete(0, tk.END)  # Очищаем поле ввода

if __name__ == "__main__":
    root = tk.Tk()
    app = CommandLineEmulator(root)
    root.mainloop()
