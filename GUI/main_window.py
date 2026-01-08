import tkinter as tk
from tkinter import font, messagebox
import random

class Ui_main_window:
    def __init__(self, questions=None, nlp_qa=None, strategies_list=None):
        self.root = tk.Tk()
        self.root.geometry('1280x720')
        self.root.resizable(False, False)
        self.root.title('AI Quiz Maker')
        
        # Modern Color Palette
        self.bg_dark = '#0f172a'      # Main background
        self.bg_card = '#1e293b'      # Cards/Header background
        self.accent_blue = '#3b82f6'  # Buttons/Highlights
        self.text_main = '#e2e8f0'    # Main text
        self.text_muted = '#94a3b8'   # Secondary text
        self.correct_green = '#059669'
        self.wrong_red = '#dc2626'

        self.root.configure(bg=self.bg_dark)

        # Raw Data
        self.questions = questions or []
        self.nlp_qa = nlp_qa
        self.strategies_list = strategies_list or []
        
        # State Variables
        self.display_questions = []
        self.current_question_idx = 0
        self.user_answers = []
        self.shuffled_options = []
        self.mc_var = tk.StringVar()
        self.mc_buttons = []

        # Fonts
        self.title_font = font.Font(family="Segoe UI", size=32, weight="bold")
        self.question_font = font.Font(family="Segoe UI", size=16)
        self.option_font = font.Font(family="Segoe UI", size=13)
        self.counter_font = font.Font(family="Segoe UI", size=13)
        self.nav_btn_font = ("Segoe UI", 10, "bold")

        # Main Container
        self.main_container = tk.Frame(self.root, bg=self.bg_dark)
        self.main_container.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_home_screen()

    def clear_screen(self):
        """Clears the main container for the next view."""
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def show_home_screen(self):
        """Displays the main menu."""
        self.clear_screen()
        
        home_frame = tk.Frame(self.main_container, bg=self.bg_dark)
        home_frame.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(home_frame, text='🎓 AI Quiz Maker', font=self.title_font, 
                 bg=self.bg_dark, fg='#60a5fa').pack(pady=20)
        
        tk.Label(home_frame, text="Ready for your test?\nWe will select 10 random questions for you.", 
                 font=self.question_font, bg=self.bg_dark, fg=self.text_muted, justify='center').pack(pady=10)

        tk.Button(home_frame, text='START QUIZ (10 Q)', font=("Segoe UI", 14, "bold"),
                  bg=self.accent_blue, fg='white', padx=40, pady=15, 
                  activebackground='#2563eb', activeforeground='white',
                  command=self.start_quiz, cursor='hand2', bd=0).pack(pady=30)

    def start_quiz(self):
        """Validates and generates the question set, then starts the UI."""
        
        # 1. Filter and validate all possible questions first
        all_valid = []
        for q in self.questions:
            if isinstance(q, tuple) and len(q) >= 3:
                # Normalize to 4 elements (text, correct, wrong_list, explanation)
                if len(q) == 3:
                    all_valid.append((q[0], q[1], q[2], "No explanation provided."))
                else:
                    all_valid.append(q)

        # 2. Select exactly 10 (or all if less than 10)
        num_to_select = min(10, len(all_valid))
        self.display_questions = random.sample(all_valid, num_to_select)

        # 3. Reset session variables
        self.current_question_idx = 0
        self.user_answers = [None] * len(self.display_questions)
        self.shuffled_options = [None] * len(self.display_questions)
        
        self.setup_quiz_ui()
        self.update_question()

    def setup_quiz_ui(self):
        """Creates the quiz layout."""
        self.clear_screen()
        
        header_frame = tk.Frame(self.main_container, bg=self.bg_card)
        header_frame.place(relx=0, rely=0, relwidth=1, relheight=0.12)

        tk.Label(header_frame, text='🎓 AI Quiz Maker', bg=self.bg_card, 
                 fg='#60a5fa', font=self.title_font).place(relx=0.5, rely=0.5, anchor='center')

        self.counter_label = tk.Label(header_frame, text='', bg=self.bg_card, 
                                     fg=self.text_muted, font=self.counter_font)
        self.counter_label.place(relx=0.95, rely=0.5, anchor='e')

        self.question_card = tk.Frame(self.main_container, bg=self.bg_card, bd=0, 
                                     highlightthickness=2, highlightbackground='#334155')
        self.question_card.place(relx=0.5, rely=0.14, anchor='n', relwidth=0.88, relheight=0.45)
        
        self.question_label = tk.Label(self.question_card, text='', bg=self.bg_card, fg=self.text_main,
                                        font=self.question_font, wraplength=1050, justify='center')
        self.question_label.place(relx=0.5, rely=0.5, anchor='center')

        self.mc_frame = tk.Frame(self.main_container, bg=self.bg_dark)
        self.mc_frame.place(relx=0.5, rely=0.61, anchor='n', relwidth=0.88)

        self.button_frame = tk.Frame(self.main_container, bg=self.bg_dark)
        self.button_frame.place(relx=0.5, rely=0.97, anchor='s')

        self.prev_btn = tk.Button(self.button_frame, text='← Previous', font=self.nav_btn_font,
                                  bg='#334155', fg=self.text_main, command=self.prev_question, 
                                  bd=0, padx=15, pady=6, cursor='hand2')
        self.prev_btn.pack(side='left', padx=10)

        self.submit_btn = tk.Button(self.button_frame, text='✓ Submit', font=self.nav_btn_font,
                                    bg=self.accent_blue, fg='white', command=self.submit_answer, 
                                    bd=0, padx=20, pady=6, cursor='hand2')
        self.submit_btn.pack(side='left', padx=10)

        self.explain_btn = tk.Button(self.button_frame, text='? Explain', font=self.nav_btn_font,
                                     bg='#8b5cf6', fg='white', command=self.show_explanation,
                                     bd=0, padx=15, pady=6, cursor='hand2')

        self.next_btn = tk.Button(self.button_frame, text='Next →', font=self.nav_btn_font,
                                 bg='#334155', fg=self.text_main, command=self.next_question, 
                                 bd=0, padx=15, pady=6, cursor='hand2')
        self.next_btn.pack(side='left', padx=10)

    def update_question(self):
        """Updates UI with current question data."""
        if self.current_question_idx == len(self.display_questions) - 1:
            self.next_btn.config(text="Finish & Score 🏆", bg=self.correct_green, command=self.finish_quiz)
        else:
            self.next_btn.config(text="Next →", bg='#334155', command=self.next_question)

        self.explain_btn.pack_forget()
        self.submit_btn.config(state='normal', bg=self.accent_blue)
        
        current = self.current_question_idx + 1
        total = len(self.display_questions)
        self.counter_label.config(text=f'Question {current} of {total}')

        for btn in self.mc_buttons: btn.destroy()
        self.mc_buttons = []

        q = self.display_questions[self.current_question_idx]
        question_text, correct_ans, wrong_answers, _ = q

        if self.shuffled_options[self.current_question_idx] is None:
            options = wrong_answers + [correct_ans]
            random.shuffle(options)
            self.shuffled_options[self.current_question_idx] = options
        else:
            options = self.shuffled_options[self.current_question_idx]

        self.question_label.config(text=question_text)
        prev_ans = self.user_answers[self.current_question_idx]
        self.mc_var.set(prev_ans if prev_ans else '')

        for option in options:
            self._add_mc_button(option)
            
        if prev_ans:
            self.apply_visual_feedback(prev_ans, correct_ans)

    def _add_mc_button(self, option):
        btn = tk.Radiobutton(self.mc_frame, text=option, variable=self.mc_var, value=option,
                             font=self.option_font, bg=self.bg_card, fg=self.text_main,
                             indicatoron=False, selectcolor=self.accent_blue, bd=0, 
                             padx=20, pady=8, anchor='w', justify='left', wraplength=1000)
        btn.pack(fill='x', pady=2, padx=5)
        self.mc_buttons.append(btn)

    def submit_answer(self):
        user_ans = self.mc_var.get()
        if not user_ans: return
        
        self.user_answers[self.current_question_idx] = user_ans
        correct_ans = self.display_questions[self.current_question_idx][1]
        self.apply_visual_feedback(user_ans, correct_ans)

    def apply_visual_feedback(self, user_ans, correct_ans):
        self.submit_btn.config(state='disabled', bg='#475569')
        self.explain_btn.pack(side='left', after=self.submit_btn, padx=10)
        
        for btn in self.mc_buttons:
            val = btn.cget('value')
            btn.config(state='disabled')
            if val == correct_ans:
                btn.config(bg=self.correct_green, selectcolor=self.correct_green, disabledforeground='white')
            elif val == user_ans:
                btn.config(bg=self.wrong_red, selectcolor=self.wrong_red, disabledforeground='white')

    def show_explanation(self):
        explanation = self.display_questions[self.current_question_idx][3]
        messagebox.showinfo("Explanation", explanation)

    def next_question(self):
        if self.current_question_idx < len(self.display_questions) - 1:
            self.current_question_idx += 1
            self.update_question()

    def prev_question(self):
        if self.current_question_idx > 0:
            self.current_question_idx -= 1
            self.update_question()

    def finish_quiz(self):
        """Calculates final score and opens modern popup."""
        score = 0
        for i, q in enumerate(self.display_questions):
            if self.user_answers[i] == q[1]:
                score += 1
        self.show_custom_score_popup(score, len(self.display_questions))

    def show_custom_score_popup(self, score, total):
        """Modern result popup in English."""
        popup = tk.Toplevel(self.root)
        popup.title("Quiz Result")
        popup.geometry("450x380")
        popup.configure(bg=self.bg_card)
        popup.resizable(False, False)
        
        popup.transient(self.root)
        popup.grab_set()

        # Center logic
        x = self.root.winfo_x() + (1280 // 2) - 225
        y = self.root.winfo_y() + (720 // 2) - 190
        popup.geometry(f"+{x}+{y}")

        tk.Label(popup, text="🎉 Quiz Completed!", font=("Segoe UI", 22, "bold"), 
                 bg=self.bg_card, fg='#60a5fa').pack(pady=(40, 10))

        score_text = f"{score} / {total}"
        tk.Label(popup, text=score_text, font=("Segoe UI", 48, "bold"), 
                 bg=self.bg_card, fg=self.text_main).pack(pady=10)

        procentaj = (score / total) * 100
        if procentaj >= 80: status = "Excellent! You're a genius! ⭐"
        elif procentaj >= 50: status = "Great job! Well done! 👍"
        else: status = "Keep studying! 📚"
        
        tk.Label(popup, text=status, font=("Segoe UI", 14), 
                 bg=self.bg_card, fg=self.text_muted).pack(pady=5)

        tk.Button(popup, text="BACK TO MENU", font=("Segoe UI", 11, "bold"),
                  bg=self.accent_blue, fg='white', bd=0, padx=30, pady=12, 
                  activebackground='#2563eb', activeforeground='white',
                  cursor='hand2', command=lambda: [popup.destroy(), self.show_home_screen()]).pack(pady=35)

    def start_window(self):
        self.root.mainloop()