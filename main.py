import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os

DATA_FILE = "data.json"

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")

        self.expenses = []

        # --- Поля ввода ---
        tk.Label(root, text="Сумма").grid(row=0, column=0)
        self.amount_entry = tk.Entry(root)
        self.amount_entry.grid(row=0, column=1)

        tk.Label(root, text="Категория").grid(row=1, column=0)
        self.category_entry = tk.Entry(root)
        self.category_entry.grid(row=1, column=1)

        tk.Label(root, text="Дата (DD/MM/YYYY)").grid(row=2, column=0)
        self.date_entry = tk.Entry(root)
        self.date_entry.grid(row=2, column=1)

        tk.Button(root, text="Добавить расход", command=self.add_expense)\
            .grid(row=3, column=0, columnspan=2)

        # --- Таблица ---
        self.tree = ttk.Treeview(root, columns=("amount", "category", "date"), show="headings")
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")
        self.tree.grid(row=4, column=0, columnspan=2)

        # --- Фильтрация ---
        tk.Label(root, text="Фильтр категория").grid(row=5, column=0)
        self.filter_category = tk.Entry(root)
        self.filter_category.grid(row=5, column=1)

        tk.Label(root, text="Дата от (DD/MM/YYYY)").grid(row=6, column=0)
        self.date_from = tk.Entry(root)
        self.date_from.grid(row=6, column=1)

        tk.Label(root, text="Дата до (DD/MM/YYYY)").grid(row=7, column=0)
        self.date_to = tk.Entry(root)
        self.date_to.grid(row=7, column=1)

        tk.Button(root, text="Фильтровать", command=self.filter_expenses)\
            .grid(row=8, column=0, columnspan=2)

        tk.Button(root, text="Сумма за период", command=self.calculate_total)\
            .grid(row=9, column=0, columnspan=2)

        tk.Button(root, text="Удалить выбранный", command=self.delete_selected)\
            .grid(row=10, column=0, columnspan=2)

        # --- Автозагрузка ---
        self.load_data()

    def validate(self, amount, date):
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
            return False

        try:
            datetime.strptime(date, "%d/%m/%Y")
        except:
            messagebox.showerror("Ошибка", "Дата должна быть в формате DD/MM/YYYY")
            return False

        return True

    def add_expense(self):
        amount = self.amount_entry.get()
        category = self.category_entry.get()
        date = self.date_entry.get()

        if not self.validate(amount, date):
            return

        expense = {"amount": float(amount), "category": category, "date": date}
        self.expenses.append(expense)

        self.update_table()
        self.save_data()

        self.amount_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)

        messagebox.showinfo("Успех", "Расход добавлен")

    def update_table(self, data=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = data if data else self.expenses
        for exp in data:
            self.tree.insert("", "end", values=(exp["amount"], exp["category"], exp["date"]))

    def parse_date(self, date_str):
        return datetime.strptime(date_str, "%d/%m/%Y")

    def filter_expenses(self):
        category = self.filter_category.get()
        date_from = self.date_from.get()
        date_to = self.date_to.get()

        result = self.expenses

        if category:
            result = [e for e in result if e["category"] == category]

        try:
            if date_from:
                d_from = self.parse_date(date_from)
                result = [e for e in result if self.parse_date(e["date"]) >= d_from]

            if date_to:
                d_to = self.parse_date(date_to)
                result = [e for e in result if self.parse_date(e["date"]) <= d_to]
        except:
            messagebox.showerror("Ошибка", "Неверный формат даты в фильтре")
            return

        self.update_table(result)

    def calculate_total(self):
        total = sum(e["amount"] for e in self.expenses)
        messagebox.showinfo("Сумма", f"Общая сумма: {total}")

    def delete_selected(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning("Ошибка", "Выберите запись для удаления")
            return

        confirm = messagebox.askyesno("Подтверждение", "Удалить выбранный расход?")
        if not confirm:
            return

        for item in selected:
            values = self.tree.item(item, "values")

            for exp in self.expenses:
                if (str(exp["amount"]) == str(values[0]) and
                    exp["category"] == values[1] and
                    exp["date"] == values[2]):
                    self.expenses.remove(exp)
                    break

        self.update_table()
        self.save_data()

        messagebox.showinfo("Готово", "Запись удалена")

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.expenses, f, indent=4)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    self.expenses = json.load(f)
                    self.update_table()
            except:
                messagebox.showerror("Ошибка", "Ошибка загрузки файла")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()