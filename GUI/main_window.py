import tkinter as tk


class Ui_main_window():
    def __init__(self, questions=None, nlp_qa=None, parsed_data=None):
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
        self.parsed_data = parsed_data or []

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

        self.submit_btn = tk.Button(self.root, text='Submit Answer', font=('Arial', 14), command=self.submit_answer)
        self.submit_btn.place(relx=0.5, rely=0.45, anchor='n')

        self.feedback_label = tk.Label(self.root, textvariable=self.feedback_var, bg='light blue', fg='green', font=('Arial', 14))
        self.feedback_label.place(relx=0.5, rely=0.5, anchor='n')

        self.prev_btn = tk.Button(self.root, text='Previous', font=('Arial', 12), command=self.prev_question)
        self.prev_btn.place(relx=0.4, rely=0.6, anchor='n')

        self.next_btn = tk.Button(self.root, text='Next', font=('Arial', 12), command=self.next_question)
        self.next_btn.place(relx=0.6, rely=0.6, anchor='n')

        self.update_question()

    def update_question(self):
        if self.questions:
            self.question_label.config(text=self.questions[self.current_question_idx])
            self.user_answer.set('')
            self.feedback_var.set('')
        else:
            self.question_label.config(text='No questions available.')

    def submit_answer(self):
        if not self.questions or not self.nlp_qa or not self.parsed_data:
            self.feedback_var.set('No NLP or questions loaded.')
            return
        user_ans = self.user_answer.get()
        idx = self.current_question_idx
        # Use the parsed_data content as reference answer for similarity
        reference_answer = self.parsed_data[idx][1][:300]  # Use first 300 chars as reference (or improve)
        question = self.questions[idx]
        score = self.nlp_qa.verify_answer(question, user_ans, reference_answer)
        self.feedback_var.set(f'Similarity score: {score:.2f}')

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


