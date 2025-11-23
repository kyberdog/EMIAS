import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class Patient:
    def __init__(self, full_name, age, gender, height, weight):
        self.full_name = full_name
        self.age = age
        self.gender = gender
        self.height = height
        self.weight = weight
    
    @property
    def bmi(self):
        return round(self.weight / ((self.height / 100) ** 2), 2)

class PatientManager:
    def __init__(self, filename='patients.json'):
        self.filename = filename
        self.patients = self.load_data()
    
    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [Patient(**item) for item in data]
            except (UnicodeDecodeError, json.JSONDecodeError):
                # Если UTF-8 не сработал, пробуем другие кодировки
                with open(self.filename, 'r', encoding='cp1251') as f:
                    data = json.load(f)
                    return [Patient(**item) for item in data]
        return []
    
    def save_data(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump([{
                'full_name': p.full_name,
                'age': p.age,
                'gender': p.gender,
                'height': p.height,
                'weight': p.weight
            } for p in self.patients], f, indent=2, ensure_ascii=False)
    
    def add_patient(self, patient):
        self.patients.append(patient)
        self.save_data()
    
    def update_patient(self, index, patient):
        self.patients[index] = patient
        self.save_data()

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Управление пациентами")
        self.manager = PatientManager()
        
        self.setup_ui()
        self.update_table()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Таблица пациентов
        columns = ("ФИО", "Возраст", "Пол", "Рост", "Вес", "ИМТ")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.grid(row=0, column=0, columnspan=4, pady=5, sticky=(tk.W, tk.E))
        
        # Кнопки управления
        ttk.Button(main_frame, text="Добавить", command=self.add_patient).grid(row=1, column=0, pady=5)
        ttk.Button(main_frame, text="Редактировать", command=self.edit_patient).grid(row=1, column=1, pady=5)
        ttk.Button(main_frame, text="Удалить", command=self.delete_patient).grid(row=1, column=2, pady=5)
        ttk.Button(main_frame, text="Статистика", command=self.show_stats).grid(row=1, column=3, pady=5)
        
        # Полоса прокрутки для таблицы
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=4, sticky=(tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
    
    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for patient in self.manager.patients:
            self.tree.insert("", tk.END, values=(
                patient.full_name,
                patient.age,
                patient.gender,
                patient.height,
                patient.weight,
                patient.bmi
            ))
    
    def add_patient(self):
        self.open_editor()
    
    def edit_patient(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пациента для редактирования")
            return
        index = self.tree.index(selected[0])
        self.open_editor(index)
    
    def delete_patient(self):
        selected = self.tree.selection()
        if not selected:
            return
        if messagebox.askyesno("Подтверждение", "Удалить выбранного пациента?"):
            index = self.tree.index(selected[0])
            del self.manager.patients[index]
            self.manager.save_data()
            self.update_table()
    
    def open_editor(self, index=None):
        EditorWindow(self.root, self.manager, index, self.update_table)
    
    def show_stats(self):
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showerror("Ошибка", "Для отображения статистики установите matplotlib")
            return
        StatsWindow(self.root, self.manager.patients)

class EditorWindow(tk.Toplevel):
    def __init__(self, parent, manager, index, callback):
        super().__init__(parent)
        self.manager = manager
        self.index = index
        self.callback = callback
        
        self.title("Редактор пациентов" if index is not None else "Добавление пациента")
        self.geometry("300x200")
        self.resizable(False, False)
        
        self.create_widgets()
        if index is not None:
            self.load_data()
    
    def create_widgets(self):
        ttk.Label(self, text="ФИО").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.name_entry = ttk.Entry(self, width=20)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self, text="Возраст").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.age_entry = ttk.Entry(self, width=20)
        self.age_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self, text="Пол").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.gender_combo = ttk.Combobox(self, values=["М", "Ж"], state="readonly", width=18)
        self.gender_combo.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(self, text="Рост (см)").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.height_entry = ttk.Entry(self, width=20)
        self.height_entry.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(self, text="Вес (кг)").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.weight_entry = ttk.Entry(self, width=20)
        self.weight_entry.grid(row=4, column=1, padx=5, pady=5)
        
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def load_data(self):
        patient = self.manager.patients[self.index]
        self.name_entry.insert(0, patient.full_name)
        self.age_entry.insert(0, str(patient.age))
        self.gender_combo.set(patient.gender)
        self.height_entry.insert(0, str(patient.height))
        self.weight_entry.insert(0, str(patient.weight))
    
    def save(self):
        try:
            patient = Patient(
                self.name_entry.get(),
                int(self.age_entry.get()),
                self.gender_combo.get(),
                float(self.height_entry.get()),
                float(self.weight_entry.get())
            )
        except ValueError as e:
            messagebox.showerror("Ошибка", "Некорректные данные")
            return
        
        if self.index is None:
            self.manager.add_patient(patient)
        else:
            self.manager.update_patient(self.index, patient)
        
        self.callback()
        self.destroy()

class StatsWindow(tk.Toplevel):
    def __init__(self, parent, patients):
        super().__init__(parent)
        self.patients = patients
        self.title("Медицинская статистика")
        self.geometry("800x600")
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_gender_tab()
        self.create_age_tab()
        self.create_bmi_gender_tab()
        self.create_bmi_age_tab()
    
    def create_gender_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Распределение по полу")
        
        genders = [p.gender for p in self.patients]
        male_count = genders.count('М')
        female_count = genders.count('Ж')
        
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.pie([male_count, female_count], labels=['Мужчины', 'Женщины'], autopct='%1.1f%%')
        ax.set_title('Распределение пациентов по полу')
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_age_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Распределение по возрасту")
        
        ages = [p.age for p in self.patients]
        
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.hist(ages, bins=10, edgecolor='black')
        ax.set_xlabel('Возраст')
        ax.set_ylabel('Количество пациентов')
        ax.set_title('Распределение пациентов по возрасту')
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_bmi_gender_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="ИМТ по полу")
        
        male_bmi = [p.bmi for p in self.patients if p.gender == 'М']
        female_bmi = [p.bmi for p in self.patients if p.gender == 'Ж']
        
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        data = [male_bmi, female_bmi]
        labels = ['Мужчины', 'Женщины']
        ax.boxplot(data, labels=labels)
        ax.set_ylabel('ИМТ')
        ax.set_title('Распределение ИМТ по полу')
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOND, expand=True)
    
    def create_bmi_age_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="ИМТ vs Возраст")
        
        ages = [p.age for p in self.patients]
        bmis = [p.bmi for p in self.patients]
        
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.scatter(ages, bmis, alpha=0.5)
        ax.set_xlabel('Возраст')
        ax.set_ylabel('ИМТ')
        ax.set_title('Зависимость ИМТ от возраста')
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()