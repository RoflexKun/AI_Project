import tkinter as tk
from tkinter import font
import random

class Ui_main_window:
    def __init__(self, questions=None, nlp_qa=None, strategies_list=None):
        self.root = tk.Tk()
        self.root.geometry('1280x720')
        self.root.resizable(False, False)
        self.root.title('AI Quiz Maker')
        
        # Modern gradient background
        self.root.configure(bg='#0f172a')

        self.questions = questions or []
        self.nlp_qa = nlp_qa
        self.strategies_list = strategies_list or []
        self.current_question_idx = 0
        self.user_answer = tk.StringVar()
        self.feedback_var = tk.StringVar()
        self.mc_var = tk.StringVar()
        self.mc_buttons = []

        # ❗ NEW — Liste filtrate, doar MCQ
        self.display_questions = [q for q in self.questions if isinstance(q, tuple)]
        self.user_answers = [None] * len(self.display_questions)

        # Modern Fonts
        self.title_font = font.Font(family="Segoe UI", size=32, weight="bold")
        self.question_font = font.Font(family="Segoe UI", size=16)
        self.option_font = font.Font(family="Segoe UI", size=13)
        self.feedback_font = font.Font(family="Segoe UI", size=18, weight="bold")
        self.counter_font = font.Font(family="Segoe UI", size=13)

        # Header Frame
        header_frame = tk.Frame(self.root, bg='#1e293b')
        header_frame.place(relx=0, rely=0, relwidth=1, relheight=0.12)

        # Title
        title_label = tk.Label(header_frame, text='🎓 AI Quiz Maker',
                               bg='#1e293b', fg='#60a5fa', font=self.title_font)
        title_label.place(relx=0.5, rely=0.5, anchor='center')

        # Question counter
        self.counter_label = tk.Label(header_frame, text='', bg='#1e293b', 
                                     fg='#94a3b8', font=self.counter_font)
        self.counter_label.place(relx=0.92, rely=0.5, anchor='e')

        # Question Card with shadow
        self.question_card = tk.Frame(self.root, bg='#1e293b', bd=0, highlightthickness=2, 
                                     highlightbackground='#334155')
        self.question_card.place(relx=0.5, rely=0.16, anchor='n', relwidth=0.88, relheight=0.28)
        
        self.question_label = tk.Label(self.question_card, text='', bg='#1e293b', fg='#e2e8f0',
                                        font=self.question_font, wraplength=1050, justify='center')
        self.question_label.place(relx=0.5, rely=0.5, anchor='center')

        # Multiple Choice Frame
        self.mc_frame = tk.Frame(self.root, bg='#0f172a')
        self.mc_frame.place(relx=0.5, rely=0.48, anchor='n', relwidth=0.88)

        # Entry for NLP (but now skipped)
        self.answer_entry_frame = tk.Frame(self.root, bg='#1e293b', bd=0, 
                                          highlightthickness=2, highlightbackground='#334155')
        self.answer_entry = tk.Entry(self.answer_entry_frame, textvariable=self.user_answer, 
                                     font=self.option_font, bd=0, 
                                     bg='#1e293b', fg='#e2e8f0', insertbackground='#60a5fa')
        self.answer_entry.pack(padx=25, pady=18, fill='x')

        # Feedback Label (with wrap fix)
        self.feedback_label = tk.Label(
            self.root,
            textvariable=self.feedback_var,
            bg='#0f172a',
            font=self.feedback_font,
            fg='#60a5fa',
            wraplength=1000,
            justify='center'
        )
        self.feedback_label.place(relx=0.5, rely=0.77, anchor='n')

        # Buttons
        button_frame = tk.Frame(self.root, bg='#0f172a')
        button_frame.place(relx=0.5, rely=0.90, anchor='center')

        self.prev_btn = tk.Button(button_frame, text='← Previous', font=self.option_font,
                                  bg='#334155', fg='#e2e8f0', activebackground='#475569',
                                  activeforeground='white', command=self.prev_question, 
                                  bd=0, padx=25, pady=12, cursor='hand2', relief='flat')
        self.prev_btn.pack(side='left', padx=10)

        self.submit_btn = tk.Button(button_frame, text='✓ Submit', font=self.option_font,
                                    bg='#3b82f6', fg='white', activebackground='#2563eb',
                                    activeforeground='white', command=self.submit_answer, 
                                    bd=0, padx=30, pady=12, cursor='hand2', relief='flat')
        self.submit_btn.pack(side='left', padx=10)

        self.next_btn = tk.Button(button_frame, text='Next →', font=self.option_font,
                                 bg='#334155', fg='#e2e8f0', activebackground='#475569',
                                 activeforeground='white', command=self.next_question, 
                                 bd=0, padx=25, pady=12, cursor='hand2', relief='flat')
        self.next_btn.pack(side='left', padx=10)

        self.update_question()

    def update_question(self):
        self.feedback_var.set('')

        total = len(self.display_questions)
        current = self.current_question_idx + 1
        self.counter_label.config(text=f'Question {current} of {total}')

        # hide NLP entry always (since text Q skipped)
        self.answer_entry_frame.place_forget()

        # clear MCQ buttons
        for btn in self.mc_buttons:
            btn.destroy()
        self.mc_buttons = []

        if not self.display_questions:
            self.question_label.config(text='No questions available.')
            return

        q = self.display_questions[self.current_question_idx]

        question_text, correct_ans, wrong_answers = q
        options = wrong_answers + [correct_ans]
        random.shuffle(options)

        self.question_label.config(text=question_text)

        prev_ans = self.user_answers[self.current_question_idx]
        self.mc_var.set(prev_ans if prev_ans else '')

        for option in options:
            self._add_mc_button(option)

    def _add_mc_button(self, option):
        btn = tk.Radiobutton(
            self.mc_frame, text=option, variable=self.mc_var, value=option,
            font=self.option_font, bg='#1e293b', fg='#e2e8f0',
            anchor='w', justify='left', wraplength=1050,
            indicatoron=False,
            selectcolor='#3b82f6',
            activebackground='#334155',
            bd=0, relief='flat',
            padx=20, pady=12,
            cursor='hand2',
            highlightthickness=2,
            highlightbackground='#334155',
            highlightcolor='#3b82f6'
        )
        btn.pack(fill='x', pady=4, padx=5)
        self.mc_buttons.append(btn)

    def submit_answer(self):
        if not self.display_questions:
            return

        user_ans = self.mc_var.get()
        self.user_answers[self.current_question_idx] = user_ans

        _, correct_ans, _ = self.display_questions[self.current_question_idx]

        if user_ans == correct_ans:
            self.feedback_var.set('✓ Correct! Well done!')
            self.feedback_label.config(fg='#10b981')
        else:
            self.feedback_var.set(f'✗ Incorrect! Correct answer: {correct_ans}')
            self.feedback_label.config(fg='#ef4444')

    # 🔥 NEW — navighează DOAR prin întrebările MCQ
    def next_question(self):
        if self.current_question_idx < len(self.display_questions) - 1:
            self.current_question_idx += 1
            self.update_question()

    def prev_question(self):
        if self.current_question_idx > 0:
            self.current_question_idx -= 1
            self.update_question()

    def start_window(self):
        self.root.mainloop()
