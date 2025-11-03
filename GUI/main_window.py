import tkinter as tk

class Ui_main_window():

    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry('1280x720')
        self.root.resizable(False, False)
        self.root.title('AI Quiz Maker')
        self.root.configure(bg='light blue')

        title_label = tk.Label(self.root,
                               text='AI Quiz Maker',
                               bg='light blue',
                               fg='gray',
                               font=('Arial', 25))
        title_label.place(relx=0.5, rely=0.05, anchor='n')


    def start_window(self):
        self.root.mainloop()


