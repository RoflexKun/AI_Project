import tkinter as tk
from tkinter import font, messagebox
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
        self.mc_var = tk.StringVar()
        self.mc_buttons = []

        # Filter and normalize questions
        raw_questions = [q for q in self.questions if isinstance(q, tuple)]
        self.display_questions = []
        
        # Ensure every question has 4 elements: (text, correct, wrong_list, explanation)
        for q in raw_questions:
            if len(q) == 4:
                self.display_questions.append(q)
            elif len(q) == 3:
                # Add a default explanation if missing
                self.display_questions.append((q[0], q[1], q[2], "No detailed explanation available for this question."))
        
        self.user_answers = [None] * len(self.display_questions)
        # Store the shuffled order of options for each question so it remains persistent
        self.shuffled_options = [None] * len(self.display_questions)

        # Modern Fonts
        self.title_font = font.Font(family="Segoe UI", size=32, weight="bold")
        self.question_font = font.Font(family="Segoe UI", size=16)
        self.option_font = font.Font(family="Segoe UI", size=13)
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
        self.question_card.place(relx=0.5, rely=0.14, anchor='n', relwidth=0.88, relheight=0.45)
        
        self.question_label = tk.Label(self.question_card, text='', bg='#1e293b', fg='#e2e8f0',
                                        font=self.question_font, wraplength=1050, justify='center')
        self.question_label.place(relx=0.5, rely=0.5, anchor='center')

        # Multiple Choice Frame
        self.mc_frame = tk.Frame(self.root, bg='#0f172a')
        self.mc_frame.place(relx=0.5, rely=0.61, anchor='n', relwidth=0.88)

        # Entry for NLP (but now skipped)
        self.answer_entry_frame = tk.Frame(self.root, bg='#1e293b', bd=0, 
                                          highlightthickness=2, highlightbackground='#334155')
        self.answer_entry = tk.Entry(self.answer_entry_frame, textvariable=self.user_answer, 
                                     font=self.option_font, bd=0, 
                                     bg='#1e293b', fg='#e2e8f0', insertbackground='#60a5fa')
        self.answer_entry.pack(padx=25, pady=18, fill='x')

        # Buttons
        button_frame = tk.Frame(self.root, bg='#0f172a')
        button_frame.place(relx=0.5, rely=0.97, anchor='s')

        nav_btn_font = ("Segoe UI", 10, "bold")

        self.prev_btn = tk.Button(button_frame, text='← Previous', font=nav_btn_font,
                                  bg='#334155', fg='#e2e8f0', activebackground='#475569',
                                  activeforeground='white', command=self.prev_question, 
                                  bd=0, padx=15, pady=6, cursor='hand2', relief='flat')
        self.prev_btn.pack(side='left', padx=10)

        self.submit_btn = tk.Button(button_frame, text='✓ Submit', font=nav_btn_font,
                                    bg='#3b82f6', fg='white', activebackground='#2563eb',
                                    activeforeground='white', command=self.submit_answer, 
                                    bd=0, padx=20, pady=6, cursor='hand2', relief='flat')
        self.submit_btn.pack(side='left', padx=10)

        # Explain Button (Hidden initially)
        self.explain_btn = tk.Button(button_frame, text='? Explain', font=nav_btn_font,
                                     bg='#8b5cf6', fg='white', activebackground='#7c3aed',
                                     activeforeground='white', command=self.show_explanation,
                                     bd=0, padx=15, pady=6, cursor='hand2', relief='flat')

        self.next_btn = tk.Button(button_frame, text='Next →', font=nav_btn_font,
                                 bg='#334155', fg='#e2e8f0', activebackground='#475569',
                                 activeforeground='white', command=self.next_question, 
                                 bd=0, padx=15, pady=6, cursor='hand2', relief='flat')
        self.next_btn.pack(side='left', padx=10)

        self.update_question()

    def update_question(self):
        self.explain_btn.pack_forget()

        # Re-pack buttons in order: Prev, Submit, Next (Explain is hidden)
        self.prev_btn.pack_forget()
        self.submit_btn.pack_forget()
        self.next_btn.pack_forget()
        
        self.prev_btn.pack(side='left', padx=10)
        self.submit_btn.pack(side='left', padx=10)
        self.next_btn.pack(side='left', padx=10)

        self.submit_btn.config(state='normal', bg='#3b82f6')
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

        # Unpack 4 values
        q = self.display_questions[self.current_question_idx]
        question_text, correct_ans, wrong_answers, explanation = q

        # Check if we have already generated/shuffled options for this question
        if self.shuffled_options[self.current_question_idx] is None:
            # First time visiting this question: generate and shuffle
            options = wrong_answers + [correct_ans]
            random.shuffle(options)
            self.shuffled_options[self.current_question_idx] = options
        else:
            # Revisiting: use the stored order
            options = self.shuffled_options[self.current_question_idx]

        q_len = len(question_text)
        q_size = 15
        if q_len > 400:
            q_size = 11
        elif q_len > 200:
            q_size = 13

        self.question_label.config(text=question_text, font=("Segoe UI", q_size))

        prev_ans = self.user_answers[self.current_question_idx]
        self.mc_var.set(prev_ans if prev_ans else '')

        for option in options:
            self._add_mc_button(option)
            
        # If question already answered, show explain, disable submit, and apply colors
        if prev_ans:
            # Inject Explain button between Submit and Next
            self.next_btn.pack_forget()
            self.explain_btn.pack(side='left', padx=10)
            self.next_btn.pack(side='left', padx=10)
            
            # Apply visual feedback (colors + disabled state)
            self.apply_visual_feedback(prev_ans, correct_ans)

    def _add_mc_button(self, option):
        opt_len = len(option)
        opt_size = 13
        if opt_len > 150:
            opt_size = 10
        elif opt_len > 80:
            opt_size = 11

        btn = tk.Radiobutton(
            self.mc_frame, text=option, variable=self.mc_var, value=option,
            font=("Segoe UI", opt_size),
            bg='#1e293b', fg='#e2e8f0',
            anchor='w', justify='left', wraplength=1050,
            indicatoron=False,
            selectcolor='#3b82f6',
            activebackground='#334155',
            bd=0, relief='flat',
            padx=20, pady=8,
            cursor='hand2',
            highlightthickness=2,
            highlightbackground='#334155',
            highlightcolor='#3b82f6'
        )
        btn.pack(fill='x', pady=2, padx=5)
        self.mc_buttons.append(btn)

    def submit_answer(self):
        if not self.display_questions:
            return

        user_ans = self.mc_var.get()
        if not user_ans:
            return

        self.user_answers[self.current_question_idx] = user_ans

        q = self.display_questions[self.current_question_idx]
        _, correct_ans, _, _ = q

        # Show Explain Button and ensure it is before Next
        self.next_btn.pack_forget()
        self.explain_btn.pack(side='left', padx=10)
        self.next_btn.pack(side='left', padx=10)
        
        # Disable buttons and highlight answers
        self.apply_visual_feedback(user_ans, correct_ans)

    def apply_visual_feedback(self, user_ans, correct_ans):
        """Disables controls and highlights correct/wrong answers"""
        self.submit_btn.config(state='disabled', bg='#94a3b8')
        
        for btn in self.mc_buttons:
            val = btn.cget('value')
            btn.config(state='disabled')
            
            # Logic for coloring
            if val == correct_ans:
                # Correct answer: Green
                btn.config(
                    bg='#059669',             # Green background
                    selectcolor='#059669',    # Green when selected
                    disabledforeground='white'
                )
            elif val == user_ans and user_ans != correct_ans:
                # User's wrong answer: Red
                btn.config(
                    bg='#dc2626',             # Red background
                    selectcolor='#dc2626',    # Red when selected
                    disabledforeground='white'
                )
            else:
                # Other options: Standard disabled look
                btn.config(disabledforeground='#94a3b8')

    def show_explanation(self):
        if not self.display_questions:
            return
        
        # Retrieve the explanation string from the tuple
        q = self.display_questions[self.current_question_idx]
        _, _, _, explanation = q
        
        messagebox.showinfo("Explanation", explanation)

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