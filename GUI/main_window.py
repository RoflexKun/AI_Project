import tkinter as tk


class Ui_main_window():
    def __init__(self, questions=None, nlp_qa=None, strategies_list=None):
        self.root = tk.Tk()
        self.root.geometry('1280x720')
        self.root.resizable(False, False)
        self.root.title('AI Quiz Maker')
        self.root.configure(bg='light blue')

        self.questions = questions or []
        self.current_question_idx = 0
        self.user_answer = tk.StringVar()
        self.feedback_var = tk.StringVar()
        self.nlp_qa = nlp_qa
        self.strategies_list = strategies_list or []

        title_label = tk.Label(self.root,
                              text='AI Quiz Maker',
                              bg='light blue',
                              fg='gray',
                              font=('Arial', 25))
        title_label.place(relx=0.5, rely=0.05, anchor='n')

        self.question_label = tk.Label(self.root, text='', bg='light blue', fg='black', font=('Arial', 18), wraplength=1000, justify='center')
        self.question_label.place(relx=0.5, rely=0.2, anchor='n')

        self.answer_entry = tk.Entry(self.root, textvariable=self.user_answer, font=('Arial', 16), width=80)
        self.answer_entry.place(relx=0.5, rely=0.4, anchor='n')

        # Navigation and submit buttons on the same line
        self.prev_btn = tk.Button(self.root, text='Previous', font=('Arial', 12), command=self.prev_question)
        self.prev_btn.place(relx=0.32, rely=0.45, anchor='n')

        self.submit_btn = tk.Button(self.root, text='Submit Answer', font=('Arial', 14), command=self.submit_answer)
        self.submit_btn.place(relx=0.5, rely=0.45, anchor='n')

        self.next_btn = tk.Button(self.root, text='Next', font=('Arial', 12), command=self.next_question)
        self.next_btn.place(relx=0.68, rely=0.45, anchor='n')

        self.feedback_label = tk.Label(self.root, textvariable=self.feedback_var, bg='light blue', fg='green', font=('Arial', 14))
        self.feedback_label.place(relx=0.5, rely=0.5, anchor='n')

        # Scrollable text widget for correct answer
        self.answer_frame = tk.Frame(self.root, bg='light blue')
        self.answer_frame.place(relx=0.5, rely=0.6, anchor='n', relwidth=0.8, relheight=0.25)
        self.answer_scrollbar = tk.Scrollbar(self.answer_frame)
        self.answer_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.correct_answer_text = tk.Text(self.answer_frame, wrap=tk.WORD, font=('Arial', 13), height=6, width=100, yscrollcommand=self.answer_scrollbar.set)
        self.correct_answer_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.answer_scrollbar.config(command=self.correct_answer_text.yview)
        self.correct_answer_text.config(state=tk.DISABLED)

        self.update_question()

    def update_question(self):
        if self.questions:
            self.question_label.config(text=self.questions[self.current_question_idx])
            self.user_answer.set('')
            self.feedback_var.set('')
            self.correct_answer_text.config(state=tk.NORMAL)
            self.correct_answer_text.delete('1.0', tk.END)
            self.correct_answer_text.config(state=tk.DISABLED)
        else:
            self.question_label.config(text='No questions available.')
            self.correct_answer_text.config(state=tk.NORMAL)
            self.correct_answer_text.delete('1.0', tk.END)
            self.correct_answer_text.config(state=tk.DISABLED)

    def submit_answer(self):
        if not self.questions or not self.strategies_list:
            self.feedback_var.set('No questions or strategies loaded.')
            return
        idx = self.current_question_idx
        user_ans = self.user_answer.get().strip().lower()
        strategies = [s.lower() for s in self.strategies_list[idx]]
        got_point = user_ans in strategies
        if got_point:
            self.feedback_var.set('Correct! You get a point.')
        else:
            self.feedback_var.set('Incorrect. Possible strategies are:')
        self.correct_answer_text.config(state=tk.NORMAL)
        self.correct_answer_text.delete('1.0', tk.END)
        self.correct_answer_text.insert(tk.END, '\n'.join(self.strategies_list[idx]))
        self.correct_answer_text.config(state=tk.DISABLED)

    def prev_question(self):
        if self.questions and self.current_question_idx > 0:
            self.current_question_idx -= 1
            self.update_question()

    def next_question(self):
        if self.questions and self.current_question_idx < len(self.questions) - 1:
            self.current_question_idx += 1
            self.update_question()

    def start_window(self):
        self.root.mainloop()


