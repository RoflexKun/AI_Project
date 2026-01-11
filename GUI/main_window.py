import tkinter as tk
from tkinter import font, messagebox
import random
import json
import os
import datetime

import multiprocessing
import queue
from tools.question_generator import QuestionGenerator

# --- FUNCȚIE WORKER PENTRU PROCES SEPARAT ---
def generation_process_worker(result_queue, resources_path, category):
    try:
        gen = QuestionGenerator(resources_path)
        res = gen.generate_random_question(specific_category=category)
        result_queue.put(res)
    except Exception as e:
        result_queue.put(f"ERROR: {str(e)}")
# ---------------------------------------------

class Ui_main_window:
    def __init__(self, generator=None, nlp_qa=None):
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
        self.generator = generator
        self.nlp_qa = nlp_qa

        # Variables for test history
        self.resources_path = os.path.join(os.getcwd(), 'resources')
        self.history_file = os.path.join(self.resources_path, 'history.json')

        #Variables for configuring test
        self.num_questions_var = tk.IntVar(value=10)
        self.cat_strategy = tk.BooleanVar(value=True)
        self.cat_nash = tk.BooleanVar(value=True)
        self.cat_csp = tk.BooleanVar(value=True)
        self.cat_minmax = tk.BooleanVar(value=True)
        
        # State Variables
        self.display_questions = []
        self.user_answers = []
        self.shuffled_options = []
        self.seen_texts = set()

        self.mc_var = tk.StringVar()
        self.mc_buttons = []

        self.current_question_idx = 0
        self.target_total_questions = 10
        self.active_categories = []

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

    def _load_history(self):
        if not os.path.exists(self.history_file):
            return []
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except:
            return []

    def _save_history(self, score, total):
        history = self._load_history()
        entry = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "score": score,
            "total": total,
            "percentage": int((score / total) * 100)
        }
        history.append(entry)
        history = history[-20:]

        if not os.path.exists(self.resources_path):
            os.makedirs(self.resources_path)

        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=4)

    def _detect_category(self, question_text):
        txt = question_text.lower()
        if "nash" in txt: return "nash"
        if "csp" in txt or "forward checking" in txt or "mrv" in txt or "domains" in txt: return "csp"
        if "minmax" in txt or "alpha-beta" in txt or "tree" in txt: return "minmax"
        return "strategy"

    def clear_screen(self):
        """Clears the main container for the next view."""
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def show_home_screen(self):
        self.clear_screen()

        home_frame = tk.Frame(self.main_container, bg=self.bg_dark)
        home_frame.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.9, relheight=0.8)

        tk.Label(home_frame, text='🎓 AI Quiz Maker', font=self.title_font,
                 bg=self.bg_dark, fg='#60a5fa').pack(pady=(0, 30))

        content_frame = tk.Frame(home_frame, bg=self.bg_dark)
        content_frame.pack(fill='both', expand=True)

        left_frame = tk.Frame(content_frame, bg=self.bg_card, padx=20, pady=20)
        left_frame.place(relx=0, rely=0, relwidth=0.35, relheight=1)

        tk.Label(left_frame, text="📜 Past Results", font=("Segoe UI", 16, "bold"),
                 bg=self.bg_card, fg=self.text_main).pack(anchor='w', pady=(0, 10))

        history_data = self._load_history()
        if not history_data:
            tk.Label(left_frame, text="No tests taken yet.", font=("Segoe UI", 12),
                     bg=self.bg_card, fg=self.text_muted).pack(anchor='w')
        else:
            for item in reversed(history_data):
                txt = f"{item['date']} - Score: {item['score']}/{item['total']} ({item['percentage']}%)"
                col = self.correct_green if item['percentage'] >= 50 else self.wrong_red
                tk.Label(left_frame, text=txt, font=("Segoe UI", 11),
                         bg=self.bg_card, fg=col).pack(anchor='w', pady=2)

        right_frame = tk.Frame(content_frame, bg=self.bg_dark, padx=40)
        right_frame.place(relx=0.35, rely=0, relwidth=0.65, relheight=1)

        tk.Label(right_frame, text="⚙️ Quiz Settings", font=("Segoe UI", 16, "bold"),
                 bg=self.bg_dark, fg=self.text_main).pack(anchor='w', pady=(20, 10))

        tk.Label(right_frame, text="Number of questions:", font=("Segoe UI", 12),
                 bg=self.bg_dark, fg=self.text_main).pack(anchor='w')

        spin = tk.Spinbox(right_frame, from_=1, to=50, textvariable=self.num_questions_var,
                          font=("Segoe UI", 12), width=5, bg='#334155', fg='white', bd=0)
        spin.pack(anchor='w', pady=(5, 20))

        tk.Label(right_frame, text="Include Topics:", font=("Segoe UI", 12),
                 bg=self.bg_dark, fg=self.text_main).pack(anchor='w', pady=(0, 5))

        def create_chk(txt, var):
            tk.Checkbutton(right_frame, text=txt, variable=var, font=("Segoe UI", 12),
                           bg=self.bg_dark, fg=self.text_muted, selectcolor=self.bg_dark,
                           activebackground=self.bg_dark, activeforeground=self.text_main).pack(anchor='w')

        create_chk("Search Strategies (N-Queens, A*, etc.)", self.cat_strategy)
        create_chk("Nash Equilibrium", self.cat_nash)
        create_chk("CSP (Logic, Forward Checking)", self.cat_csp)
        create_chk("MinMax & Alpha-Beta", self.cat_minmax)

        tk.Button(right_frame, text='START QUIZ ►', font=("Segoe UI", 14, "bold"),
                  bg=self.accent_blue, fg='white', padx=40, pady=15,
                  activebackground='#2563eb', activeforeground='white',
                  command=self.start_quiz, cursor='hand2', bd=0).pack(pady=40, anchor='w')

    def _generate_with_timeout(self, category, timeout=1.0):  # Timeout mic (ex: 1.0 sec)
        """
        Lansează un PROCES separat. Dacă expiră timpul, îl OMORÂM (terminate).
        """
        # Folosim Queue din multiprocessing
        result_queue = multiprocessing.Queue()

        # Creăm procesul
        # Îi trimitem calea către resurse ca să își facă propriul generator
        p = multiprocessing.Process(
            target=generation_process_worker,
            args=(result_queue, self.resources_path, category)
        )

        p.start()

        # Așteptăm să termine timp de 'timeout' secunde
        p.join(timeout)

        if p.is_alive():
            # AICI E CHEIA: Dacă încă trăiește după 1 secundă, îl omorâm forțat!
            # Asta eliberează instant procesorul.
            p.terminate()
            p.join()  # Curățăm resursele după el
            print(f"💀 Process killed for category '{category}' (Timeout)")
            return None

        # Verificăm dacă a pus ceva în coadă
        if not result_queue.empty():
            res = result_queue.get()
            # Verificăm dacă a returnat o eroare
            if isinstance(res, str) and res.startswith("ERROR:"):
                print(res)
                return None
            return res

        return None

    def _generate_next_question(self):
        attempts = 0
        max_attempts = 15

        while attempts < max_attempts:
            attempts += 1
            if not self.active_categories: break

            chosen_cat = random.choice(self.active_categories)

            try:
                q_data = self._generate_with_timeout(chosen_cat, timeout=1.0)

                if q_data is None:
                    continue

                if len(q_data) == 3:
                    final_q = (q_data[0], q_data[1], q_data[2], "No explanation provided.")
                else:
                    final_q = q_data

                if final_q[0] not in self.seen_texts:
                    self.seen_texts.add(final_q[0])

                    self.display_questions.append(final_q)
                    self.user_answers.append(None)
                    self.shuffled_options.append(None)
                    return True

            except Exception as e:
                print(f"Gen Error in loop: {e}")
                continue

        return False

    def start_quiz(self):
        self.active_categories = []
        if self.cat_strategy.get(): self.active_categories.append('strategy_simulation')
        if self.cat_nash.get(): self.active_categories.append('nash_equilibrium')
        if self.cat_csp.get(): self.active_categories.append('csp_evaluation')
        if self.cat_minmax.get(): self.active_categories.append('minmax_evaluation')

        if not self.active_categories:
            messagebox.showerror("Error", "Please select at least one topic!")
            return

        try:
            self.target_total_questions = int(self.num_questions_var.get())
        except:
            self.target_total_questions = 10

        self.display_questions = []
        self.user_answers = []
        self.shuffled_options = []
        self.seen_texts = set()
        self.current_question_idx = 0

        success = self._generate_next_question()
        if not success:
             messagebox.showerror("Error", "Could not generate initial question.")
             return

        self.setup_quiz_ui()
        self.update_question()

    def setup_quiz_ui(self):
        """Layout fix, spațios, fără suprapuneri cu footer-ul."""
        self.clear_screen()

        # --- Header (10%) ---
        header_frame = tk.Frame(self.main_container, bg=self.bg_card)
        header_frame.place(relx=0, rely=0, relwidth=1, relheight=0.10)

        tk.Label(header_frame, text='🎓 AI Quiz Maker', bg=self.bg_card,
                 fg='#60a5fa', font=self.title_font).place(relx=0.5, rely=0.5, anchor='center')

        self.counter_label = tk.Label(header_frame, text='', bg=self.bg_card,
                                      fg=self.text_muted, font=self.counter_font)
        self.counter_label.place(relx=0.95, rely=0.5, anchor='e')

        # --- Question Card (35%) ---
        # rely=0.12, înălțime 35% -> se termină la 0.47
        self.question_card = tk.Frame(self.main_container, bg=self.bg_card, bd=0)
        self.question_card.place(relx=0.5, rely=0.12, anchor='n', relwidth=0.88, relheight=0.35)

        self.question_text_widget = tk.Text(self.question_card, bg=self.bg_card, fg=self.text_main,
                                            font=self.question_font, wrap='word', bd=0,
                                            highlightthickness=0, padx=15, pady=15)
        self.question_text_widget.place(relx=0, rely=0, relwidth=0.98, relheight=1)

        # Scrollbar vertical pentru întrebare (rămâne, e util)
        qs_scroll = tk.Scrollbar(self.question_card, command=self.question_text_widget.yview,
                                 bg=self.bg_card, troughcolor=self.bg_card, bd=0)
        qs_scroll.place(relx=0.98, rely=0, relheight=1, width=15)
        self.question_text_widget.config(yscrollcommand=qs_scroll.set)

        # --- Answer Area (40%) ---
        # Mutat mai sus: rely=0.49. Înălțime 40% -> se termină la 0.89.
        # Footer-ul e la 0.96, deci avem 7% spațiu liber (siguranță maximă).
        self.mc_container = tk.Frame(self.main_container, bg=self.bg_dark)
        self.mc_container.place(relx=0.5, rely=0.49, anchor='n', relwidth=0.88, relheight=0.40)

        # --- Footer / Buttons (8%) ---
        self.button_frame = tk.Frame(self.main_container, bg=self.bg_dark)
        # Plasat la 0.96 (jos de tot)
        self.button_frame.place(relx=0.5, rely=0.96, anchor='s')

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
        """Actualizează interfața. Optimizat pentru viteză."""
        if self.current_question_idx == self.target_total_questions - 1:
            self.next_btn.config(text="Finish & Score 🏆", bg=self.correct_green, command=self.finish_quiz)
        else:
            self.next_btn.config(text="Next →", bg='#334155', command=self.next_question)

        self.explain_btn.pack_forget()
        self.submit_btn.config(state='normal', bg=self.accent_blue)

        current = self.current_question_idx + 1
        total = self.target_total_questions
        self.counter_label.config(text=f'Question {current} of {total}')

        # Distrugem widget-urile vechi
        for item in self.mc_buttons:
            item['frame'].destroy()
        self.mc_buttons = []

        q = self.display_questions[self.current_question_idx]
        question_text, correct_ans, wrong_answers, _ = q

        if self.shuffled_options[self.current_question_idx] is None:
            options = wrong_answers + [correct_ans]
            random.shuffle(options)
            self.shuffled_options[self.current_question_idx] = options
        else:
            options = self.shuffled_options[self.current_question_idx]

        # Scriem întrebarea
        self.question_text_widget.config(state='normal')
        self.question_text_widget.delete('1.0', tk.END)
        self.question_text_widget.tag_configure("center", justify='center')
        self.question_text_widget.insert(tk.END, question_text, "center")
        self.question_text_widget.config(state='disabled')

        prev_ans = self.user_answers[self.current_question_idx]
        self.mc_var.set(prev_ans if prev_ans else '')

        # Adăugăm butoanele
        for option in options:
            self._add_mc_button(option)

        # Refacem highlight-ul
        if prev_ans:
            self.apply_visual_feedback(prev_ans, correct_ans)
        else:
            self._update_selection_visuals()

    def _add_mc_button(self, option):
        """
        Răspuns compact, FĂRĂ scrollbar vizibil (controlat din mouse), highlight albastru.
        """

        # 1. Container (Row)
        row_frame = tk.Frame(self.mc_container, bg=self.bg_card, bd=0)
        row_frame.pack(fill='both', expand=True, pady=3)

        # 2. Text Widget (Fără Scrollbar fizic)
        # height=1 -> ține rândul compact
        text_widget = tk.Text(row_frame, wrap='none', height=1,
                              bg=self.bg_card, fg=self.text_main, font=self.option_font,
                              bd=0, highlightthickness=0, cursor="hand2")

        clean_text = str(option).replace('\n', '   |   ')
        text_widget.insert('1.0', clean_text)
        text_widget.config(state='disabled')  # Read-only

        # Pack simplu
        text_widget.pack(side='left', fill='both', expand=True, padx=15, pady=10)

        # --- LOGICĂ SCROLL ORIZONTAL CU MOUSE-UL ---
        def on_mouse_wheel(event):
            # Windows: event.delta, Linux: Button-4/5
            # Shift+Scroll sau doar Scroll pentru orizontală (fiind o singură linie)
            if event.delta:
                text_widget.xview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"  # Oprește propagarea

        # Bind pe MouseWheel pentru scroll orizontal
        text_widget.bind("<MouseWheel>", on_mouse_wheel)
        text_widget.bind("<Shift-MouseWheel>", on_mouse_wheel)

        # 3. Logica de Selecție
        def select_this(event=None):
            self.mc_var.set(option)
            self._update_selection_visuals()

        # Bind click pe tot
        text_widget.bind("<Button-1>", select_this)
        row_frame.bind("<Button-1>", select_this)

        # Salvăm
        self.mc_buttons.append({
            'frame': row_frame,
            'text': text_widget,
            'value': option
        })

    def _update_selection_visuals(self):
        """Highlight albastru puternic pe răspunsul selectat."""
        selected_val = self.mc_var.get()

        # Culoarea de selecție (Albastru stil GitHub/VSCode)
        highlight_bg = '#1d4ed8'

        for item in self.mc_buttons:
            val = item['value']
            frame = item['frame']
            txt = item['text']

            if val == selected_val:
                frame.config(bg=highlight_bg)
                txt.config(bg=highlight_bg)
            else:
                # Reset la culoarea cardului
                frame.config(bg=self.bg_card)
                txt.config(bg=self.bg_card)

    def submit_answer(self):
        user_ans = self.mc_var.get()
        if not user_ans: return
        
        self.user_answers[self.current_question_idx] = user_ans
        correct_ans = self.display_questions[self.current_question_idx][1]
        self.apply_visual_feedback(user_ans, correct_ans)

    def apply_visual_feedback(self, user_ans, correct_ans):
        self.submit_btn.config(state='disabled', bg='#475569')
        self.explain_btn.pack(side='left', after=self.submit_btn, padx=10)

        for item in self.mc_buttons:
            val = item['value']
            frame = item['frame']
            txt = item['text']

            # Dezactivăm interacțiunea (unbind)
            txt.unbind("<Button-1>")
            frame.unbind("<Button-1>")

            if val == correct_ans:
                frame.config(bg=self.correct_green)
                txt.config(bg=self.correct_green)
            elif val == user_ans:
                frame.config(bg=self.wrong_red)
                txt.config(bg=self.wrong_red)
            else:
                frame.config(bg=self.bg_card)
                txt.config(bg=self.bg_card)

    def show_explanation(self):
        explanation = self.display_questions[self.current_question_idx][3]
        messagebox.showinfo("Explanation", explanation)

    def next_question(self):
        next_idx = self.current_question_idx + 1

        # Dacă vrem să mergem la o întrebare care nu există încă, o generăm ACUM.
        if next_idx >= len(self.display_questions):
            # Opțional: Cursor "busy"
            self.root.config(cursor="watch")
            self.root.update()

            success = self._generate_next_question()

            self.root.config(cursor="")  # Cursor normal

            if not success:
                messagebox.showerror("Error", "Could not generate next question.")
                return

        # Avansăm
        self.current_question_idx += 1
        self.update_question()

    def prev_question(self):
        if self.current_question_idx > 0:
            self.current_question_idx -= 1
            self.update_question()

    def finish_quiz(self):
        score = 0
        for i, q in enumerate(self.display_questions):
            # Verificăm să nu fie None (caz extrem)
            if self.user_answers[i] == q[1]:
                score += 1

        self._save_history(score, len(self.display_questions))
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