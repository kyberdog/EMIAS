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

# Добавляем импорт для работы с изображениями
from PIL import Image, ImageTk
import urllib.request

# Добавляем импорт Faker для генерации тестовых данных
try:
    from faker import Faker
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False

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
        
        # Если данных нет, генерируем тестовые данные
        if not self.patients and FAKER_AVAILABLE:
            self.generate_initial_data()
    
    def generate_initial_data(self):
        """Генерация начальных тестовых данных с помощью Faker"""
        fake = Faker('ru_RU')
        
        for _ in range(10):
            gender = fake.random_element(elements=('М', 'Ж'))
            if gender == 'М':
                first_name = fake.first_name_male()
                last_name = fake.last_name_male()
            else:
                first_name = fake.first_name_female()
                last_name = fake.last_name_female()
                
            full_name = f"{last_name} {first_name} {fake.middle_name()}"
            age = fake.random_int(min=18, max=80)
            height = fake.random_int(min=150, max=190)
            weight = fake.random_int(min=50, max=100)
            
            patient = Patient(full_name, age, gender, height, weight)
            self.patients.append(patient)
        
        self.save_data()
    
    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [Patient(**item) for item in data]
            except Exception as e:
                print(f"Ошибка загрузки данных: {e}")
                return []
        return []
    
    def save_data(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump([{
                    'full_name': p.full_name,
                    'age': p.age,
                    'gender': p.gender,
                    'height': p.height,
                    'weight': p.weight
                } for p in self.patients], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения данных: {e}")
    
    def add_patient(self, patient):
        self.patients.append(patient)
        self.save_data()
    
    def update_patient(self, index, patient):
        self.patients[index] = patient
        self.save_data()

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Обкуренный ЕМИАС")
        self.manager = PatientManager()
        
        # Настройка цветовой палитры в стиле фона
        self.colors = {
            'primary': '#2c3e50',      # Темно-синий
            'secondary': '#34495e',    # Средний синий - используется для текста
            'accent': '#3498db',       # Голубой
            'light': '#ecf0f1',        # Светло-серый
            'text': '#34495e',         # Темный текст - изменен на #34495e
            'success': '#27ae60',      # Зеленый
            'warning': '#f39c12',      # Оранжевый
            'danger': '#e74c3c'        # Красный
        }
        
        # Настройка стилей
        self.setup_styles()
        
        # Загружаем фоновое изображение
        self.load_background_image()
        
        self.setup_ui()
        self.update_table()
    
    def setup_styles(self):
        """Настройка цветовых стилей для виджетов"""
        style = ttk.Style()
        
        # Стиль для основного фрейма
        style.configure('Card.TFrame', 
                       background=self.colors['light'],
                       relief='raised',
                       borderwidth=2)
        
        # Стиль для кнопок - изменен цвет текста на #34495e
        style.configure('Primary.TButton',
                       background=self.colors['accent'],
                       foreground=self.colors['text'],  # #34495e
                       focuscolor='none',
                       padding=(10, 5),
                       font=('Arial', 9, 'bold'))
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['primary']),
                           ('pressed', self.colors['secondary'])],
                 foreground=[('active', self.colors['light']),  # Белый текст при наведении
                           ('pressed', self.colors['light'])])  # Белый текст при нажатии
        
        # Стиль для заголовков
        style.configure('Title.TLabel',
                      background=self.colors['light'],
                      foreground=self.colors['text'],  # #34495e
                      font=('Arial', 14, 'bold'))
        
        # Стиль для таблицы - изменен цвет текста заголовков на #34495e
        style.configure('Treeview',
                       background=self.colors['light'],
                       foreground=self.colors['text'],
                       fieldbackground=self.colors['light'],
                       font=('Arial', 9))
        
        style.configure('Treeview.Heading',
                      background=self.colors['light'],
                      foreground=self.colors['text'],  # #34495e
                      font=('Arial', 10, 'bold'))
        
        style.map('Treeview',
                 background=[('selected', self.colors['accent'])])
    
    def load_background_image(self):
        """Загрузка и настройка фонового изображения"""
        try:
            # Скачиваем изображение по URL
            url = "https://i.pinimg.com/736x/25/ae/54/25ae54efbed9fd04e426a9baccb3bdb9.jpg"
            image_path = "background.jpg"
            
            # Скачиваем файл если его нет
            if not os.path.exists(image_path):
                urllib.request.urlretrieve(url, image_path)
            
            # Открываем и обрабатываем изображение
            self.original_image = Image.open(image_path)
            self.update_background()
            
            # Привязываем изменение размера окна к обновлению фона
            self.root.bind("<Configure>", self.on_resize)
            
        except Exception as e:
            print(f"Ошибка загрузки фона: {e}")
            self.bg_image = None
    
    def update_background(self):
        """Обновление фонового изображения при изменении размера окна"""
        if hasattr(self, 'original_image'):
            # Получаем текущий размер окна
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            # Если окно еще не отрисовано, используем размер по умолчанию
            if width < 10 or height < 10:
                width = 1000
                height = 700
            
            # Масштабируем изображение под размер окна
            resized_image = self.original_image.resize((width, height), Image.Resampling.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(resized_image)
            
            # Обновляем изображение на Canvas
            if hasattr(self, 'canvas'):
                self.canvas.delete("background")
                self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw", tags="background")
                self.canvas.lower("background")
    
    def on_resize(self, event):
        """Обработчик изменения размера окна"""
        if event.widget == self.root:
            self.update_background()
    
    def setup_ui(self):
        # Создаем Canvas как основной контейнер 
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Устанавливаем фоновое изображение
        if hasattr(self, 'bg_image'):
            self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw", tags="background")
        
        # Убираем полупрозрачный оверлей для устранения белого прямоугольника
        # Вместо этого используем прозрачный фон для основного фрейма
        
        # Основной фрейм для содержимого (уменьшенный размер)
        main_frame = ttk.Frame(self.canvas, style="Card.TFrame")
        main_frame.place(relx=0.5, rely=0.5, anchor="center", width=650, height=450)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Управление пациентами", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=5, pady=(10, 15))
        
        # Таблица пациентов (уменьшенная)
        columns = ("ФИО", "Возраст", "Пол", "Рост", "Вес", "ИМТ")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=8)
        
        # Настройка столбцов (уменьшенные ширины)
        column_widths = [150, 60, 50, 60, 60, 60]
        for col, width in zip(columns, column_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")
        
        self.tree.grid(row=1, column=0, columnspan=5, padx=10, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Полоса прокрутки для таблицы
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=5, sticky=(tk.N, tk.S))
        
        # Кнопки управления с новой цветовой схемой
        button_frame = ttk.Frame(main_frame, style="Card.TFrame")
        button_frame.grid(row=2, column=0, columnspan=6, pady=15)
        
        ttk.Button(button_frame, text="Добавить пациента", 
                  command=self.add_patient, style="Primary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Редактировать", 
                  command=self.edit_patient, style="Primary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить", 
                  command=self.delete_patient, style="Primary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Статистика", 
                  command=self.show_stats, style="Primary.TButton").pack(side=tk.LEFT, padx=5)
        
        '''# Кнопка для генерации тестовых данных (только если Faker доступен)
        if FAKER_AVAILABLE:
            ttk.Button(button_frame, text="Добавить test data", 
                      command=self.generate_test_data, style="Primary.TButton").pack(side=tk.LEFT, padx=5)
        '''
        # Настройка адаптивности
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def generate_test_data(self):
        """Генерация дополнительных тестовых данных"""
        if not FAKER_AVAILABLE:
            messagebox.showwarning("Предупреждение", "Библиотека Faker не установлена")
            return
            
        fake = Faker('ru_RU')
        
        for _ in range(15):  # Добавляем 15 новых пациентов
            gender = fake.random_element(elements=('М', 'Ж'))
            if gender == 'М':
                first_name = fake.first_name_male()
                last_name = fake.last_name_male()
            else:
                first_name = fake.first_name_female()
                last_name = fake.last_name_female()
                
            full_name = f"{last_name} {first_name} {fake.middle_name()}"
            age = fake.random_int(min=18, max=80)
            height = fake.random_int(min=150, max=190)
            weight = fake.random_int(min=50, max=100)
            
            patient = Patient(full_name, age, gender, height, weight)
            self.manager.add_patient(patient)
        
        self.update_table()
        messagebox.showinfo("Юпи!", "Добавлено 5 тестовых пациентов")
    
    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for patient in self.manager.patients:
            self.tree.insert("", tk.END, values=(
                patient.full_name,
                patient.age,
                patient.gender,
                f"{patient.height} см",
                f"{patient.weight} кг",
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
        EditorWindow(self.root, self.manager, index, self.update_table, self.colors)
    
    def show_stats(self):
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showerror("Упс!", "Для отображения статистики установите matplotlib")
            return
        StatsWindow(self.root, self.manager.patients)

class EditorWindow(tk.Toplevel):
    def __init__(self, parent, manager, index, callback, colors):
        super().__init__(parent)
        self.manager = manager
        self.index = index
        self.callback = callback
        self.colors = colors
        
        self.title("Редактор пациентов" if index is not None else "Добавление пациента")
        self.geometry("300x250")
        self.resizable(False, False)
        self.configure(bg=colors['light'])
        
        self.create_widgets()
        if index is not None:
            self.load_data()
    
    def create_widgets(self):
        # Создаем стиль для этого окна
        style = ttk.Style()
        style.configure('Editor.TLabel', background=self.colors['light'], foreground=self.colors['text'])
        style.configure('Editor.TButton', 
                       background=self.colors['accent'], 
                       foreground=self.colors['text'],  # #34495e
                       font=('Arial', 9))
        
        style.map('Editor.TButton',
                 background=[('active', self.colors['primary']),
                           ('pressed', self.colors['secondary'])],
                 foreground=[('active', self.colors['light']),
                           ('pressed', self.colors['light'])])
        
        ttk.Label(self, text="ФИО", style='Editor.TLabel').grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.name_entry = ttk.Entry(self, width=25)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self, text="Возраст", style='Editor.TLabel').grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.age_entry = ttk.Entry(self, width=25)
        self.age_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self, text="Пол", style='Editor.TLabel').grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.gender_combo = ttk.Combobox(self, values=["М", "Ж"], state="readonly", width=23)
        self.gender_combo.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(self, text="Рост (см)", style='Editor.TLabel').grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.height_entry = ttk.Entry(self, width=25)
        self.height_entry.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(self, text="Вес (кг)", style='Editor.TLabel').grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.weight_entry = ttk.Entry(self, width=25)
        self.weight_entry.grid(row=4, column=1, padx=5, pady=5)
        
        btn_frame = ttk.Frame(self, style='Editor.TLabel')
        btn_frame.grid(row=5, column=0, columnspan=2, pady=15)
        
        ttk.Button(btn_frame, text="Сохранить", command=self.save, style='Editor.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.destroy, style='Editor.TButton').pack(side=tk.LEFT, padx=5)
    
    def load_data(self):
        patient = self.manager.patients[self.index]
        self.name_entry.insert(0, patient.full_name)
        self.age_entry.insert(0, str(patient.age))
        self.gender_combo.set(patient.gender)
        self.height_entry.insert(0, str(patient.height))
        self.weight_entry.insert(0, str(patient.weight))
    
    def save(self):
        try:
            # Проверяем, что все поля заполнены
            if not all([self.name_entry.get(), self.age_entry.get(), 
                       self.gender_combo.get(), self.height_entry.get(), 
                       self.weight_entry.get()]):
                messagebox.showerror("Упс!", "Все поля должны быть заполнены")
                return
                
            patient = Patient(
                self.name_entry.get(),
                int(self.age_entry.get()),
                self.gender_combo.get(),
                float(self.height_entry.get()),
                float(self.weight_entry.get())
            )
        except ValueError as e:
            messagebox.showerror("Упс!", "Некорректные данные. Проверьте возраст, рост и вес")
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
        colors = ['#3498db', '#e74c3c']  # Синий и красный
        ax.pie([male_count, female_count], labels=['Мужчины', 'Женщины'], autopct='%1.1f%%', colors=colors)
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
        ax.hist(ages, bins=10, edgecolor='black', color='#3498db')
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
        colors = ['#3498db', '#e74c3c']
        
        box_plot = ax.boxplot(data, labels=labels, patch_artist=True)
        for patch, color in zip(box_plot['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
            
        ax.set_ylabel('ИМТ')
        ax.set_title('Распределение ИМТ по полу')
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_bmi_age_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="ИМТ vs Возраст")
        
        ages = [p.age for p in self.patients]
        bmis = [p.bmi for p in self.patients]
        genders = [p.gender for p in self.patients]
        
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Разделяем точки по полу для разного цвета
        male_ages = [age for age, gender in zip(ages, genders) if gender == 'М']
        male_bmis = [bmi for bmi, gender in zip(bmis, genders) if gender == 'М']
        female_ages = [age for age, gender in zip(ages, genders) if gender == 'Ж']
        female_bmis = [bmi for bmi, gender in zip(bmis, genders) if gender == 'Ж']
        
        ax.scatter(male_ages, male_bmis, alpha=0.7, color='#3498db', label='Мужчины')
        ax.scatter(female_ages, female_bmis, alpha=0.7, color='#e74c3c', label='Женщины')
        ax.set_xlabel('Возраст')
        ax.set_ylabel('ИМТ')
        ax.set_title('Зависимость ИМТ от возраста')
        ax.legend()
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1000x700")
    root.title("Обкуренный ЕМИАС")
    app = MainApp(root)
    root.mainloop()
