import json
import os
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk


class IQTestApp:
    age_groups = {
        (6, 8): {'mean': 25, 'std_dev': 6},
        (9, 12): {'mean': 40, 'std_dev': 8},
        (13, 16): {'mean': 55, 'std_dev': 10},
        (17, 25): {'mean': 65, 'std_dev': 12},
        (26, 40): {'mean': 60, 'std_dev': 11},
        (40, 100): {'mean': 50, 'std_dev': 10}
    }

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("IQ тест")
        self.root.geometry("1100x685")

        self.selected_age = None
        self.current_question = 0
        self.score = 0
        self.time_left = 1200
        self.timer_running = False
        self.questions = []
        self.option_buttons = []
        self.question_frame = None
        self.options_frame = None
        self.timer_label = None

        self.load_questions()
        self.create_main_menu()

    def load_questions(self):
        try:
            questions_path = os.path.join(os.path.dirname(__file__), "questions.json")
            print(f"Путь к файлу вопросов: {questions_path}")

            if os.path.exists(questions_path):
                with open(questions_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.questions = data.get("questions", [])
                    print(f"Загружено вопросов: {len(self.questions)}")
            else:
                print("")
                self.questions = []
        except Exception as e:
            print(f"Ошибка загрузки вопросов: {e}")
            print(f"Тип ошибки: {type(e)}")
            print(f"Полное сообщение: {str(e)}")
            self.questions = []
        except Exception as e:
            print(f"Ошибка загрузки вопросов: {e}")
            self.questions = []

    def create_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = tk.Frame(self.root, bg="white")
        main_frame.place(relx=0.5, rely=0.5, anchor="center", width=800, height=500)

        title = tk.Label(main_frame, text="IQ тест", font=("Arial", 48, "bold"), bg="white")
        title.pack(pady=40)

        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(pady=20)

        start_btn = tk.Button(
            button_frame,
            text="Начать тест",
            font=("Arial", 24),
            bg="#4CAF50",
            fg="white",
            relief="flat",
            command=self.start_test
        )
        start_btn.pack(pady=15, fill="x")

        info_btn = tk.Button(
            button_frame,
            text="Информация",
            font=("Arial", 24),
            bg="#2196F3",
            fg="white",
            relief="flat",
            command=self.show_info
        )
        info_btn.pack(pady=15, fill="x")

        exit_btn = tk.Button(
            button_frame,
            text="Выход",
            font=("Arial", 24),
            bg="#f44336",
            fg="white",
            relief="flat",
            command=self.root.quit
        )
        exit_btn.pack(pady=15, fill="x")

    def create_quiz_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        timer_frame = tk.Frame(main_frame, bg="white")
        timer_frame.place(relx=0.5, y=20, anchor="n")

        self.timer_label = tk.Label(
            timer_frame,
            text="Осталось времени: 20:00",
            font=("Arial", 16),
            bg="white"
        )
        self.timer_label.pack()

        self.question_frame = tk.Frame(main_frame, bg="white")
        self.question_frame.place(relx=0.25, rely=0.5, anchor="center")

        self.options_frame = tk.Frame(main_frame, bg="white")
        self.options_frame.place(relx=0.75, rely=0.5, anchor="center")

        self.main_frame = main_frame

    def start_test(self):
        self.show_age_selection()

    def show_age_selection(self):
        age_dialog = tk.Toplevel(self.root)
        age_dialog.title("Выберите возраст")
        age_dialog.geometry("400x200")
        age_dialog.resizable(False, False)
        age_dialog.grab_set()

        container = tk.Frame(age_dialog, bg="white", padx=20, pady=20)
        container.pack(fill="both", expand=True)

        tk.Label(
            container,
            text="Введите ваш возраст (6-100):",
            font=("Arial", 16),
            bg="white"
        ).pack(pady=10)

        self.age_entry = tk.Entry(
            container,
            font=("Arial", 20),
            justify="center",
            validate="key"
        )
        self.age_entry['validatecommand'] = (
            self.age_entry.register(self.validate_age_input),
            '%P'
        )
        self.age_entry.pack(pady=10)

        button_frame = tk.Frame(container, bg="white")
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="OK",
            font=("Arial", 16),
            bg="#4CAF50",
            fg="white",
            relief="flat",
            command=lambda: self.process_age_selection(age_dialog)
        ).pack(side="left", padx=10)

        tk.Button(
            button_frame,
            text="Отмена",
            font=("Arial", 16),
            bg="#f44336",
            fg="white",
            relief="flat",
            command=age_dialog.destroy
        ).pack(side="left", padx=10)

    def validate_age_input(self, new_value):
        if new_value == "":
            return True
        try:
            int(new_value)
            return True
        except ValueError:
            return False

    def process_age_selection(self, dialog):
        age_text = self.age_entry.get()
        if not age_text:
            messagebox.showerror("Ошибка", "Пожалуйста, введите возраст")
            return

        try:
            age = int(age_text)
            if 6 <= age <= 101:
                self.selected_age = age
                dialog.destroy()
                self.start_quiz()
            else:
                messagebox.showerror("Ошибка", "Возраст должен быть от 6 до 100 лет")
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите число")

    def start_quiz(self):
        self.current_question = 0
        self.score = 0
        self.time_left = 1200
        self.timer_running = True
        

        for widget in self.root.winfo_children():
            widget.destroy()
        

        self.create_quiz_ui()

        self.update_timer()

        self.show_question()

    def update_timer(self):
        if not self.timer_running:
            return

        if self.time_left > 0:
            mins, secs = divmod(self.time_left, 60)
            time_str = f"{mins:02d}:{secs:02d}"
            
            if hasattr(self, 'timer_label'):
                try:
                    self.timer_label.config(text=f"Осталось времени: {time_str}")
                except:
                    self.create_timer_label()
            
            self.time_left -= 1
            self.root.after(1000, self.update_timer)
        else:
            self.timer_running = False
            self.show_results()
            return

    def create_timer_label(self):
        if not hasattr(self, 'timer_label'):
            self.timer_label = tk.Label(
                self.timer_frame,
                text="Осталось времени: 20:00",
                font=("Arial", 16),
                bg="white"
            )
            self.timer_label.pack()
        elif self.time_left <= 0:
            self.timer_running = False
            self.show_results()

    def show_question(self):
        if self.current_question < len(self.questions):
            current_question = self.questions[self.current_question]

            for widget in self.question_frame.winfo_children():
                widget.destroy()
            for widget in self.options_frame.winfo_children():
                widget.destroy()

            tk.Label(
                self.question_frame,
                text=f"Вопрос {self.current_question + 1}",
                font=("Arial", 16),
                bg="white"
            ).pack(pady=20)

            if 'image' in current_question:
                try:
                    img_path = os.path.join(os.path.dirname(__file__), current_question['image'])
                    if os.path.exists(img_path):
                        img = Image.open(img_path)
                        img = img.resize((300, 225), Image.Resampling.LANCZOS)
                        self.question_img = ImageTk.PhotoImage(img)

                        img_label = tk.Label(self.question_frame, image=self.question_img, bg="white")
                        img_label.pack(pady=20)
                except Exception as e:
                    print(f"Ошибка загрузки изображения: {e}")
                    tk.Label(
                        self.question_frame,
                        text="Изображение не найдено",
                        font=("Arial", 16),
                        bg="white",
                        fg="red"
                    ).pack(pady=20)

            self.option_buttons = []
            for i, option in enumerate(current_question['options']):
                btn = tk.Button(
                    self.options_frame,
                    text=option,
                    font=("Arial", 14),
                    bg="#e0e0e0",
                    relief="flat",
                    width=30,
                    anchor="w",
                    command=lambda i=i: self.check_answer(i)
                )
                btn.pack(pady=5)
                self.option_buttons.append(btn)



            nav_frame = tk.Frame(self.question_frame, bg="white")
            nav_frame.pack(fill="x", pady=20)

            if self.current_question > 0:
                tk.Button(
                    nav_frame,
                    text="Назад",
                    font=("Arial", 16),
                    relief="flat",
                    bg="#2196F3",
                    fg="white",
                    command=self.prev_question
                ).pack(side="left", padx=10)

            tk.Button(
                nav_frame,
                text="Далее",
                font=("Arial", 16),
                relief="flat",
                bg="#4CAF50",
                fg="white",
                command=self.next_question
            ).pack(side="right", padx=10)
        else:
            self.show_results()

    def prev_question(self):
        self.current_question -= 1
        self.show_question()

    def next_question(self):
        self.current_question += 1
        self.show_question()

    def check_answer(self, selected_option):
        question = self.questions[self.current_question]

        for btn in self.option_buttons:
            btn.config(state="disabled")

        correct_idx = question["correct"]

        if selected_option == correct_idx:
            self.score += 1

        self.next_question()

    def calculate_iq(self):
        if not self.selected_age:
            return None

        for (min_age, max_age), stats in self.age_groups.items():
            if min_age <= self.selected_age <= max_age:
                mean = stats['mean']
                std_dev = stats['std_dev']
                break
        else:
            return None

        iq = 100 + ((self.score - mean) / std_dev) * 15
        return max(50, min(150, round(iq)))

    def show_results(self):
        self.timer_running = False

        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            main_frame,
            text="Результаты теста",
            font=("Arial", 28, "bold"),
            bg="white"
        ).pack(pady=20)

        iq_score = self.calculate_iq()

        result_text = ""
        if iq_score is not None:
            result_text = f"Ваш IQ: {iq_score}"

        tk.Label(
            main_frame,
            text=result_text,
            font=("Arial", 20),
            bg="white"
        ).pack(pady=10)

        interpretation = self.get_interpretation(iq_score)
        tk.Label(
            main_frame,
            text=interpretation,
            font=("Arial", 16),
            bg="white",
            wraplength=600,
            justify="center"
        ).pack(pady=20)

        tk.Button(
            main_frame,
            text="В главное меню",
            font=("Arial", 16),
            relief="flat",
            bg="#2196F3",
            fg="white",
            command=self.create_main_menu
        ).pack(pady=20)

    def get_interpretation(self, iq):
        if iq is None:
            return "Не удалось определить уровень IQ"

        if iq >= 130:
            return ("Гениальный уровень интеллекта\n"
                    "Вы находитесь в верхних 2% населения")
        elif iq >= 120:
            return ("Очень высокий интеллект\n"
                    "Вы находитесь в верхних 10% населения")
        elif iq >= 110:
            return ("Выше среднего\n"
                    "Вы находитесь в верхних 25% населения")
        elif iq >= 90:
            return ("Средний уровень интеллекта\n"
                    "Вы находитесь в середине распределения")
        elif iq >= 80:
            return ("Ниже среднего\n"
                    "Вы находитесь в нижних 25% населения")
        else:
            return ("Низкий уровень интеллекта\n"
                    "Вы находитесь в нижних 10% населения")

    def show_info(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            main_frame,
            text="О тесте",
            font=("Arial", 28, "bold"),
            bg="white"
        ).pack(pady=20)

        info_text = """
Понятие коэффициента интеллекта ввёл немецкий учёный Уильям Штерн в 1912 году. Он обратил внимание на серьёзные недостатки умственного возраста как показателя в шкалах Бине. Штерн предложил использовать в роли показателя интеллекта частное от деления умственного возраста на хронологический. IQ впервые был использован в шкале интеллекта Стенфорд - Бине в 1916 году.

В нынешнее время интерес к тестам IQ многократно возрос, ввиду чего появилось множество разнообразных необоснованных шкал. Поэтому сравнивать результаты разных тестов чрезвычайно затруднительно и само число IQ утратило информативную ценность.

Данный тест состоит из 35 вопросов разной сложности. Тест ограничен по времени (20 минут). После тестирования вы сможете ознакомиться с результатом теста. Результатом теста является: баллы, сравнение с средним показателем и словесная оценка результатов.
        """

        tk.Label(
            main_frame,
            text=info_text,
            font=("Arial", 13),
            bg="white",
            justify="left",
            wraplength=600
        ).pack(pady=20)

        tk.Button(
            main_frame,
            text="Назад",
            font=("Arial", 16),
            relief="flat",
            bg="#2196F3",
            fg="white",
            command=self.create_main_menu
        ).pack(pady=20)


if __name__ == "__main__":
    app = IQTestApp()
    app.root.mainloop()