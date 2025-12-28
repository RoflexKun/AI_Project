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

        # Liste filtrate, doar MCQ
        self.display_questions = [q for q in self.questions if isinstance(q, tuple)]
        self.user_answers = [None] * len(self.display_questions)
        
        # Initialize AI model for explanations
        self.explanation_model = None
        self._init_explanation_model()

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

        # 🆕 EXPLANATION BUTTON - Placed between Submit and Next
        self.explain_btn = tk.Button(button_frame, text='💡 Explain Answer', font=nav_btn_font,
                                     bg='#8b5cf6', fg='white', activebackground='#7c3aed',
                                     activeforeground='white', command=self.show_explanation, 
                                     bd=0, padx=15, pady=6, cursor='hand2', relief='flat')
        self.explain_btn.pack(side='left', padx=10)

        self.next_btn = tk.Button(button_frame, text='Next →', font=nav_btn_font,
                                 bg='#334155', fg='#e2e8f0', activebackground='#475569',
                                 activeforeground='white', command=self.next_question, 
                                 bd=0, padx=15, pady=6, cursor='hand2', relief='flat')
        self.next_btn.pack(side='left', padx=10)

        self.update_question()

    def _init_explanation_model(self):
        """Initialize the AI model for generating explanations"""
        try:
            from transformers import pipeline
            print("Loading explanation model... This may take a moment.")
            # Using a lightweight model for text generation
            self.explanation_model = pipeline(
                "text2text-generation",
                model="google/flan-t5-base",
                max_length=200
            )
            print("Explanation model loaded successfully!")
        except ImportError:
            print("Warning: transformers library not installed. Install with: pip install transformers torch")
            self.explanation_model = None
        except Exception as e:
            print(f"Warning: Could not load explanation model: {e}")
            self.explanation_model = None

    def update_question(self):
        self.feedback_label.place_forget()
        self.feedback_var.set('')

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

        q = self.display_questions[self.current_question_idx]

        question_text, correct_ans, wrong_answers = q
        options = wrong_answers + [correct_ans]
        random.shuffle(options)

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
        self.user_answers[self.current_question_idx] = user_ans

        _, correct_ans, _ = self.display_questions[self.current_question_idx]

        self.feedback_label.place(relx=0.5, rely=0.88, anchor='s')
        if user_ans == correct_ans:
            self.feedback_var.set('✓ Correct! Well done!')
            self.feedback_label.config(fg='#10b981')
        else:
            self.feedback_var.set(f'✗ Incorrect! Correct answer: {correct_ans}')
            self.feedback_label.config(fg='#ef4444')

    # 🆕 SHOW EXPLANATION POPUP
    def show_explanation(self):
        if not self.display_questions:
            return

        question_text, correct_ans, _ = self.display_questions[self.current_question_idx]

        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title('Answer Explanation')
        popup.geometry('800x500')
        popup.configure(bg='#0f172a')
        popup.resizable(False, False)
        
        # Center the popup
        popup.transient(self.root)
        popup.grab_set()

        # Header
        header = tk.Frame(popup, bg='#1e293b')
        header.pack(fill='x', pady=(0, 20))
        
        header_label = tk.Label(header, text='💡 Answer Explanation', 
                               bg='#1e293b', fg='#60a5fa',
                               font=("Segoe UI", 20, "bold"))
        header_label.pack(pady=15)

        # Correct Answer Display
        answer_frame = tk.Frame(popup, bg='#1e293b', highlightthickness=2, 
                               highlightbackground='#10b981')
        answer_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        tk.Label(answer_frame, text='✓ Correct Answer:', 
                bg='#1e293b', fg='#10b981',
                font=("Segoe UI", 12, "bold")).pack(anchor='w', padx=15, pady=(10, 5))
        
        tk.Label(answer_frame, text=correct_ans, 
                bg='#1e293b', fg='#e2e8f0',
                font=("Segoe UI", 13), wraplength=700, justify='left').pack(anchor='w', padx=15, pady=(0, 10))

        # Explanation Section
        explain_frame = tk.Frame(popup, bg='#1e293b', highlightthickness=2, 
                                highlightbackground='#334155')
        explain_frame.pack(fill='both', expand=True, padx=30, pady=(0, 20))

        tk.Label(explain_frame, text='📚 Explanation:', 
                bg='#1e293b', fg='#60a5fa',
                font=("Segoe UI", 12, "bold")).pack(anchor='w', padx=15, pady=(10, 5))

        # Scrollable text widget for explanation
        text_frame = tk.Frame(explain_frame, bg='#1e293b')
        text_frame.pack(fill='both', expand=True, padx=15, pady=(0, 10))

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')

        explanation_text = tk.Text(text_frame, wrap='word', 
                                  bg='#1e293b', fg='#e2e8f0',
                                  font=("Segoe UI", 11), 
                                  yscrollcommand=scrollbar.set,
                                  bd=0, padx=10, pady=10)
        explanation_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=explanation_text.yview)

        # Generate explanation using NLP model
        explanation_text.insert('1.0', "Generating explanation...")
        explanation_text.update()
        
        explanation = self._generate_explanation(question_text, correct_ans)
        
        explanation_text.delete('1.0', 'end')
        explanation_text.insert('1.0', explanation)
        explanation_text.config(state='disabled')

        # Back Button
        back_btn = tk.Button(popup, text='← Back to Quiz', 
                           font=("Segoe UI", 11, "bold"),
                           bg='#3b82f6', fg='white', 
                           activebackground='#2563eb',
                           command=popup.destroy, 
                           bd=0, padx=25, pady=10, 
                           cursor='hand2', relief='flat')
        back_btn.pack(pady=(0, 20))

    def _generate_explanation(self, question: str, correct_answer: str) -> str:
        """Generate an explanation for why the answer is correct"""
        
        question_lower = question.lower()
        
        # 1. Strategy Simulation (Problem + Algorithm)
        if any(prob in question_lower for prob in ['n-queens', 'hanoi', 'graph coloring', "knight's tour"]):
            return self._explain_strategy_simulation(question, correct_answer)
        
        # 2. Nash Equilibrium
        elif 'nash' in question_lower or 'equilibrium' in question_lower:
            return self._explain_nash_equilibrium(question, correct_answer)
        
        # 3. Forward Checking
        elif 'forward checking' in question_lower:
            return self._explain_forward_checking(question, correct_answer)
        
        # 4. MRV
        elif 'mrv' in question_lower or 'minimum remaining values' in question_lower or 'smallest domain' in question_lower:
            return self._explain_mrv(question, correct_answer)
        
        return self._get_fallback_explanation(question, correct_answer)
    
    def _explain_strategy_simulation(self, question: str, correct_answer: str) -> str:
        """Template simplu: Pentru problema X folosim algoritmul Y"""
        explanation = f"✓ RĂSPUNS CORECT: {correct_answer}\n\n"
        explanation += "=" * 70 + "\n"
        
        question_lower = question.lower()
        
        # Detectează problema
        if 'n-queens' in question_lower:
            problem = "N-Queens"
            explanation += "PROBLEMA: N-Queens\n"
            explanation += "=" * 70 + "\n"
            explanation += "Plasează N regine pe o tablă N×N astfel încât nicio regină\n"
            explanation += "să nu atace altă regină (linie, coloană, diagonală).\n\n"
            
            if 'Min-Conflicts' in correct_answer:
                explanation += f"ALGORITMUL SELECTAT: {correct_answer}\n\n"
                explanation += "DE CE MIN-CONFLICTS?\n"
                explanation += "-" * 70 + "\n"
                explanation += "Pe această instanță, Min-Conflicts este superior față de:\n"
                explanation += "   • Random Search (căutare aleatoare)\n"
                explanation += "   • Standard Backtracking\n\n"
                
                explanation += "ALGORITM:\n"
                explanation += "1. Pornește de la configurația dată\n"
                explanation += "2. Numără conflictele pentru fiecare regină\n"
                explanation += "3. Selectează o regină cu conflicte\n"
                explanation += "4. Mută regina pe linia cu MINIM conflicte din coloana ei\n"
                explanation += "5. Repetă până când nu mai sunt conflicte\n\n"
                
                explanation += "CALCUL CONFLICTE:\n"
                explanation += "Pentru o regină la (col, row):\n"
                explanation += "   conflicts = 0\n"
                explanation += "   pentru fiecare altă regină la (c, r):\n"
                explanation += "       dacă r == row SAU |r - row| == |c - col|:\n"
                explanation += "           conflicts += 1\n\n"
                
                explanation += "AVANTAJE:\n"
                explanation += "• Găsește rapid soluții (chiar pentru N=1000+)\n"
                explanation += "• Folosește heuristică inteligentă\n"
                explanation += "• Mai eficient decât backtracking pentru N mare\n"
                
            elif 'Standard Backtracking' in correct_answer:
                explanation += f"ALGORITMUL SELECTAT: {correct_answer}\n\n"
                explanation += "DE CE BACKTRACKING?\n"
                explanation += "-" * 70 + "\n"
                explanation += "Pe această instanță, nici Min-Conflicts nici Random Search\n"
                explanation += "nu au reușit să îmbunătățească configurația inițială.\n"
                explanation += "Backtracking este alegerea standard pentru explorare sistematică.\n"
                
        elif 'hanoi' in question_lower:
            problem = "Hanoi Towers"
            explanation += "PROBLEMA: Turnurile din Hanoi\n"
            explanation += "=" * 70 + "\n"
            explanation += "Mută toate discurile de pe tija 1 pe tija 3.\n"
            explanation += "Restricție: Disc mare nu poate fi peste disc mic.\n\n"
            
            if 'A*' in correct_answer:
                explanation += f"ALGORITMUL SELECTAT: {correct_answer}\n\n"
                explanation += "DE CE A* SEARCH?\n"
                explanation += "-" * 70 + "\n"
                explanation += "Pe această instanță, A* găsește soluția OPTIMALĂ.\n"
                explanation += "A* este superior față de Greedy Best-First.\n\n"
                
                explanation += "HEURISTICA:\n"
                explanation += "   h(state) = număr de discuri care NU sunt pe tija finală\n\n"
                
                explanation += "FUNCȚIA DE EVALUARE:\n"
                explanation += "   f(n) = g(n) + h(n)\n"
                explanation += "   unde:\n"
                explanation += "      g(n) = număr de mutări făcute până acum\n"
                explanation += "      h(n) = estimare până la soluție\n\n"
                
                explanation += "SOLUȚIA OPTIMĂ:\n"
                # Extract n_disks
                import re
                disks_match = re.search(r'(\d+) disks', question)
                if disks_match:
                    n = int(disks_match.group(1))
                    optimal = 2**n - 1
                    explanation += f"   Pentru {n} discuri: {optimal} mutări (2^{n} - 1)\n\n"
                
                explanation += "A* găsește această soluție optimală datorită heuristicii admisibile.\n"
                
            elif 'Greedy' in correct_answer:
                explanation += f"ALGORITMUL SELECTAT: {correct_answer}\n\n"
                explanation += "DE CE GREEDY?\n"
                explanation += "-" * 70 + "\n"
                explanation += "Pe această instanță, Greedy a fost mai rapid,\n"
                explanation += "deși nu garantează soluție optimală.\n"
                
        elif 'graph coloring' in question_lower:
            problem = "Graph Coloring"
            explanation += "PROBLEMA: Colorarea Grafului\n"
            explanation += "=" * 70 + "\n"
            explanation += "Atribuie culori nodurilor astfel încât noduri adiacente\n"
            explanation += "să aibă culori diferite.\n\n"
            
            # Extract edges
            edges_match = re.search(r'Edges: ([^\n\.]+)', question)
            if edges_match:
                explanation += f"Graf: {edges_match.group(1)}\n\n"
            
            if 'Forward Checking' in correct_answer:
                explanation += f"ALGORITMUL SELECTAT: {correct_answer}\n\n"
                explanation += "DE CE BACKTRACKING WITH FORWARD CHECKING?\n"
                explanation += "-" * 70 + "\n"
                explanation += "Pe această instanță, heuristica de grad (degree heuristic)\n"
                explanation += "a identificat un nod cu grad mare care trebuie colorat prioritar.\n\n"
                
                explanation += "STRATEGIE:\n"
                explanation += "1. Ordonează nodurile după grad (descrescător)\n"
                explanation += "2. Atribuie culoare nodului cu cel mai mare grad\n"
                explanation += "3. Aplică forward checking: elimină culoarea din vecinii necolorati\n"
                explanation += "4. Repetă până când toate nodurile sunt colorate\n"
                
            else:
                explanation += f"ALGORITMUL SELECTAT: {correct_answer}\n\n"
                explanation += "Standard Backtracking este suficient pentru această instanță.\n"
                
        elif 'knight' in question_lower:
            problem = "Knight's Tour"
            explanation += "PROBLEMA: Turul Calului\n"
            explanation += "=" * 70 + "\n"
            explanation += "Mută calul pe toată tabla de șah astfel încât să viziteze\n"
            explanation += "fiecare pătrat exact o dată.\n\n"
            
            # Extract starting position
            pos_match = re.search(r'Knight at ([A-H]\d)', question)
            if pos_match:
                explanation += f"Poziție inițială: {pos_match.group(1)}\n\n"
            
            if 'Greedy' in correct_answer:
                explanation += f"ALGORITMUL SELECTAT: {correct_answer}\n\n"
                explanation += "DE CE GREEDY BEST-FIRST (Warnsdorff's Rule)?\n"
                explanation += "-" * 70 + "\n"
                explanation += "Pe această instanță, regula Warnsdorff a ales mutarea optimă.\n\n"
                
                explanation += "REGULA WARNSDORFF:\n"
                explanation += "Întotdeauna mută calul pe pătratul cu CELE MAI PUȚINE\n"
                explanation += "mutări ulterioare posibile (accessibility heuristic).\n\n"
                
                explanation += "ALGORITM:\n"
                explanation += "1. Din poziția curentă, găsește toate mutările valide\n"
                explanation += "2. Pentru fiecare mutare, numără câte mutări sunt posibile DUPĂ\n"
                explanation += "3. Alege mutarea cu număr MINIM de mutări ulterioare\n"
                explanation += "4. Aceasta evită blocarea calului în colțuri\n\n"
                
                explanation += "În acest caz, Warnsdorff a avut grad minimal mai mic decât\n"
                explanation += "alegerea aleatoare, deci este superior.\n"
                
            else:
                explanation += f"ALGORITMUL SELECTAT: {correct_answer}\n\n"
                explanation += "Random Search este suficient pentru această instanță.\n"
        
        return explanation
    
    def _explain_nash_equilibrium(self, question: str, correct_answer: str) -> str:
        """Detailed explanation for Nash equilibrium problems with calculations"""
        explanation = f"✓ CORRECT ANSWER: {correct_answer}\n\n"
        explanation += "=" * 70 + "\n"
        explanation += "📊 NASH EQUILIBRIUM - COMPLETE MATHEMATICAL ANALYSIS\n"
        explanation += "=" * 70 + "\n\n"
        
        # Extract payoff matrix from question
        import re
        matrix_lines = []
        payoffs = []
        for line in question.split('\n'):
            if '(' in line and ')' in line:
                matrix_lines.append(line)
                # Extract all tuples like (3, 5)
                tuples = re.findall(r'\((-?\d+),\s*(-?\d+)\)', line)
                if tuples:
                    payoffs.extend([(int(a), int(b)) for a, b in tuples])
        
        explanation += "THEORETICAL FOUNDATION\n"
        explanation += "-" * 70 + "\n"
        explanation += "DEFINITION (Nash, 1950):\n"
        explanation += "A strategy profile s* = (s₁*, s₂*, ..., sₙ*) is a Nash Equilibrium if\n"
        explanation += "and only if, for every player i:\n\n"
        explanation += "   uᵢ(s₁*, s₂*, ..., sₙ*) ≥ uᵢ(s₁*, ..., sᵢ, ..., sₙ*)  ∀sᵢ ∈ Sᵢ\n\n"
        explanation += "Where:\n"
        explanation += "   • uᵢ: Player i's utility/payoff function\n"
        explanation += "   • Sᵢ: Player i's pure strategy space\n"
        explanation += "   • sᵢ*: Player i's equilibrium strategy\n\n"
        
        explanation += "In words: No player can unilaterally deviate from s* and achieve\n"
        explanation += "a strictly higher payoff. Each player's strategy is a BEST RESPONSE\n"
        explanation += "to the strategies chosen by all other players.\n\n"
        
        explanation += "GAME STRUCTURE\n"
        explanation += "-" * 70 + "\n"
        explanation += "Players: {Player A, Player B}\n"
        explanation += "Strategy Spaces:\n"
        explanation += "   • S_A = {Up, Down}\n"
        explanation += "   • S_B = {Left, Right}\n\n"
        
        explanation += "PAYOFF MATRIX (Bimatrix Game):\n"
        for line in matrix_lines:
            explanation += "   " + line + "\n"
        explanation += "\nNotation: (u_A(s_A, s_B), u_B(s_A, s_B))\n\n"
        
        # Reconstruct matrix for analysis
        if len(payoffs) >= 4:
            matrix = [[payoffs[0], payoffs[1]], [payoffs[2], payoffs[3]]]
            
            explanation += "COMPLETE EQUILIBRIUM ANALYSIS\n"
            explanation += "-" * 70 + "\n"
            explanation += "We apply the BEST RESPONSE METHOD to find all pure Nash equilibria.\n\n"
            
            explanation += "STEP 1: Player A's Best Responses\n"
            explanation += "For each of Player B's strategies, find Player A's optimal choice:\n\n"
            
            # Column 1 (Left)
            up_left_a = matrix[0][0][0]
            down_left_a = matrix[1][0][0]
            explanation += f"   If B plays Left:\n"
            explanation += f"      • A plays Up   → u_A = {up_left_a}\n"
            explanation += f"      • A plays Down → u_A = {down_left_a}\n"
            if up_left_a > down_left_a:
                explanation += f"      ⇒ BR_A(Left) = Up  (since {up_left_a} > {down_left_a})\n\n"
                br_a_left = "Up"
            elif down_left_a > up_left_a:
                explanation += f"      ⇒ BR_A(Left) = Down  (since {down_left_a} > {up_left_a})\n\n"
                br_a_left = "Down"
            else:
                explanation += f"      ⇒ BR_A(Left) = {{Up, Down}}  (indifferent)\n\n"
                br_a_left = "Both"
            
            # Column 2 (Right)
            up_right_a = matrix[0][1][0]
            down_right_a = matrix[1][1][0]
            explanation += f"   If B plays Right:\n"
            explanation += f"      • A plays Up   → u_A = {up_right_a}\n"
            explanation += f"      • A plays Down → u_A = {down_right_a}\n"
            if up_right_a > down_right_a:
                explanation += f"      ⇒ BR_A(Right) = Up  (since {up_right_a} > {down_right_a})\n\n"
                br_a_right = "Up"
            elif down_right_a > up_right_a:
                explanation += f"      ⇒ BR_A(Right) = Down  (since {down_right_a} > {up_right_a})\n\n"
                br_a_right = "Down"
            else:
                explanation += f"      ⇒ BR_A(Right) = {{Up, Down}}  (indifferent)\n\n"
                br_a_right = "Both"
            
            explanation += "STEP 2: Player B's Best Responses\n"
            explanation += "For each of Player A's strategies, find Player B's optimal choice:\n\n"
            
            # Row 1 (Up)
            up_left_b = matrix[0][0][1]
            up_right_b = matrix[0][1][1]
            explanation += f"   If A plays Up:\n"
            explanation += f"      • B plays Left  → u_B = {up_left_b}\n"
            explanation += f"      • B plays Right → u_B = {up_right_b}\n"
            if up_left_b > up_right_b:
                explanation += f"      ⇒ BR_B(Up) = Left  (since {up_left_b} > {up_right_b})\n\n"
                br_b_up = "Left"
            elif up_right_b > up_left_b:
                explanation += f"      ⇒ BR_B(Up) = Right  (since {up_right_b} > {up_left_b})\n\n"
                br_b_up = "Right"
            else:
                explanation += f"      ⇒ BR_B(Up) = {{Left, Right}}  (indifferent)\n\n"
                br_b_up = "Both"
            
            # Row 2 (Down)
            down_left_b = matrix[1][0][1]
            down_right_b = matrix[1][1][1]
            explanation += f"   If A plays Down:\n"
            explanation += f"      • B plays Left  → u_B = {down_left_b}\n"
            explanation += f"      • B plays Right → u_B = {down_right_b}\n"
            if down_left_b > down_right_b:
                explanation += f"      ⇒ BR_B(Down) = Left  (since {down_left_b} > {down_right_b})\n\n"
                br_b_down = "Left"
            elif down_right_b > down_left_b:
                explanation += f"      ⇒ BR_B(Down) = Right  (since {down_right_b} > {down_left_b})\n\n"
                br_b_down = "Right"
            else:
                explanation += f"      ⇒ BR_B(Down) = {{Left, Right}}  (indifferent)\n\n"
                br_b_down = "Both"
            
            explanation += "STEP 3: Finding Nash Equilibria (Mutual Best Responses)\n"
            explanation += "-" * 70 + "\n"
            explanation += "A strategy profile (s_A, s_B) is a Nash Equilibrium if and only if:\n"
            explanation += "   s_A ∈ BR_A(s_B)  AND  s_B ∈ BR_B(s_A)\n\n"
            
            explanation += "Checking all four strategy profiles:\n\n"
            
            equilibria = []
            
            # (Up, Left)
            explanation += "   (Up, Left):\n"
            check_a = (br_a_left == "Up" or br_a_left == "Both")
            check_b = (br_b_up == "Left" or br_b_up == "Both")
            explanation += f"      • Is Up ∈ BR_A(Left)?   {'YES ✓' if check_a else 'NO ✗'}\n"
            explanation += f"      • Is Left ∈ BR_B(Up)?   {'YES ✓' if check_b else 'NO ✗'}\n"
            if check_a and check_b:
                explanation += f"      ⇒ NASH EQUILIBRIUM with payoffs ({matrix[0][0][0]}, {matrix[0][0][1]})\n\n"
                equilibria.append("(A:Up, B:Left)")
            else:
                explanation += "      ⇒ NOT a Nash Equilibrium\n\n"
            
            # (Up, Right)
            explanation += "   (Up, Right):\n"
            check_a = (br_a_right == "Up" or br_a_right == "Both")
            check_b = (br_b_up == "Right" or br_b_up == "Both")
            explanation += f"      • Is Up ∈ BR_A(Right)?  {'YES ✓' if check_a else 'NO ✗'}\n"
            explanation += f"      • Is Right ∈ BR_B(Up)?  {'YES ✓' if check_b else 'NO ✗'}\n"
            if check_a and check_b:
                explanation += f"      ⇒ NASH EQUILIBRIUM with payoffs ({matrix[0][1][0]}, {matrix[0][1][1]})\n\n"
                equilibria.append("(A:Up, B:Right)")
            else:
                explanation += "      ⇒ NOT a Nash Equilibrium\n\n"
            
            # (Down, Left)
            explanation += "   (Down, Left):\n"
            check_a = (br_a_left == "Down" or br_a_left == "Both")
            check_b = (br_b_down == "Left" or br_b_down == "Both")
            explanation += f"      • Is Down ∈ BR_A(Left)?  {'YES ✓' if check_a else 'NO ✗'}\n"
            explanation += f"      • Is Left ∈ BR_B(Down)?  {'YES ✓' if check_b else 'NO ✗'}\n"
            if check_a and check_b:
                explanation += f"      ⇒ NASH EQUILIBRIUM with payoffs ({matrix[1][0][0]}, {matrix[1][0][1]})\n\n"
                equilibria.append("(A:Down, B:Left)")
            else:
                explanation += "      ⇒ NOT a Nash Equilibrium\n\n"
            
            # (Down, Right)
            explanation += "   (Down, Right):\n"
            check_a = (br_a_right == "Down" or br_a_right == "Both")
            check_b = (br_b_down == "Right" or br_b_down == "Both")
            explanation += f"      • Is Down ∈ BR_A(Right)? {'YES ✓' if check_a else 'NO ✗'}\n"
            explanation += f"      • Is Right ∈ BR_B(Down)? {'YES ✓' if check_b else 'NO ✗'}\n"
            if check_a and check_b:
                explanation += f"      ⇒ NASH EQUILIBRIUM with payoffs ({matrix[1][1][0]}, {matrix[1][1][1]})\n\n"
                equilibria.append("(A:Down, B:Right)")
            else:
                explanation += "      ⇒ NOT a Nash Equilibrium\n\n"
            
            explanation += "CONCLUSION\n"
            explanation += "-" * 70 + "\n"
            if equilibria:
                explanation += f"Pure Nash Equilibria: {', '.join(equilibria)}\n\n"
                explanation += "INTERPRETATION:\n"
                explanation += "At these strategy profiles, both players are playing mutual best\n"
                explanation += "responses. Neither player has an incentive to unilaterally deviate,\n"
                explanation += "making these stable outcomes of the game.\n\n"
                
                if len(equilibria) > 1:
                    explanation += "NOTE: Multiple equilibria exist. Game theory doesn't predict which\n"
                    explanation += "equilibrium will be played without additional refinements (such as\n"
                    explanation += "payoff dominance, risk dominance, or focal point reasoning).\n"
            else:
                explanation += "No Pure Nash Equilibrium exists.\n\n"
                explanation += "INTERPRETATION:\n"
                explanation += "No strategy profile satisfies the mutual best response condition.\n"
                explanation += "This game has no stable pure strategy outcome. Players will cycle\n"
                explanation += "through different strategy profiles, each trying to exploit the other.\n\n"
                explanation += "SOLUTION:\n"
                explanation += "By Nash's Existence Theorem (1950), every finite game has at least\n"
                explanation += "one Nash Equilibrium in MIXED STRATEGIES. To find it, we would solve:\n\n"
                explanation += "   Player A: maxₚ minq u_A(p, q)  where p ∈ Δ(S_A)\n"
                explanation += "   Player B: maxq minₚ u_B(p, q)  where q ∈ Δ(S_B)\n\n"
                explanation += "Using indifference conditions to find mixed strategy probabilities.\n"
        
        return explanation
    
    def _explain_forward_checking(self, question: str, correct_answer: str) -> str:
        """Explain Forward Checking in CSP"""
        explanation = f"✓ CORRECT ANSWER:\n{correct_answer}\n\n"
        explanation += "=" * 70 + "\n"
        explanation += "🔍 FORWARD CHECKING - CONSTRAINT PROPAGATION ANALYSIS\n"
        explanation += "=" * 70 + "\n\n"
        
        explanation += "THEORETICAL FOUNDATION\n"
        explanation += "-" * 70 + "\n"
        explanation += "Forward Checking is a LOOKAHEAD technique in backtracking search for\n"
        explanation += "Constraint Satisfaction Problems (CSP). It maintains Arc Consistency\n"
        explanation += "for future variables with respect to the current assignment.\n\n"
        
        explanation += "CSP FORMALIZATION:\n"
        explanation += "A CSP is defined as a triple (X, D, C) where:\n"
        explanation += "   • X = {X₁, X₂, ..., Xₙ} is a set of variables\n"
        explanation += "   • D = {D₁, D₂, ..., Dₙ} is a set of domains\n"
        explanation += "   • C = {C₁, C₂, ..., Cₘ} is a set of constraints\n\n"
        
        explanation += "FORWARD CHECKING ALGORITHM:\n"
        explanation += "-" * 70 + "\n"
        explanation += "Upon assigning variable Xᵢ = v:\n\n"
        explanation += "   FOR each unassigned variable Xⱼ:\n"
        explanation += "      IF constraint(Xᵢ, Xⱼ) exists:\n"
        explanation += "         Dⱼ ← Dⱼ \\ {v}    // Remove conflicting value\n"
        explanation += "         IF Dⱼ = ∅:\n"
        explanation += "            RETURN FAILURE  // Dead-end detected\n\n"
        
        explanation += "INFERENCE RULE:\n"
        explanation += "Forward Checking enforces ARC CONSISTENCY for all arcs (Xⱼ, Xᵢ) where\n"
        explanation += "Xⱼ is unassigned and Xᵢ is the newly assigned variable.\n\n"
        
        explanation += "Arc Consistency: An arc (Xⱼ, Xᵢ) is consistent if:\n"
        explanation += "   ∀d ∈ Dⱼ, ∃d' ∈ Dᵢ such that constraint(d, d') is satisfied\n\n"
        
        # Extract assignment details
        import re
        assignment_match = re.search(r'assigned (\w+) = (\w+)', question)
        
        explanation += "PROBLEM INSTANCE ANALYSIS\n"
        explanation += "-" * 70 + "\n"
        
        if assignment_match:
            var_assigned = assignment_match.group(1)
            color_assigned = assignment_match.group(2)
            
            explanation += f"Recent Assignment: {var_assigned} ← {color_assigned}\n\n"
            
            # Extract graph structure
            edges_match = re.search(r'Constraints \(Edges\): ([^\n]+)', question)
            if edges_match:
                edges_str = edges_match.group(1)
                explanation += f"Graph Structure (Adjacency Constraints):\n"
                explanation += f"   {edges_str}\n\n"
            
            # Extract domains
            domains_match = re.search(r'Initial Domains: \{([^}]+)\}', question)
            if domains_match:
                domain_str = domains_match.group(1)
                explanation += f"Original Domain: D = {{{domain_str}}}\n\n"
            
            explanation += "PROPAGATION STEPS:\n"
            explanation += "-" * 70 + "\n"
            explanation += f"1. Variable {var_assigned} is bound to value '{color_assigned}'\n\n"
            
            explanation += "2. Identify all constraints involving " + var_assigned + ":\n"
            explanation += "   Let N(" + var_assigned + ") = { neighbors of " + var_assigned + " in constraint graph }\n\n"
            
            explanation += "3. For each Xⱼ ∈ N(" + var_assigned + ") AND Xⱼ unassigned:\n"
            explanation += f"   • Remove '{color_assigned}' from Dⱼ\n"
            explanation += "   • This enforces the binary constraint: Xⱼ ≠ " + var_assigned + "\n\n"
            
            explanation += "4. For each Xₖ ∉ N(" + var_assigned + "):\n"
            explanation += "   • Domain Dₖ remains unchanged\n"
            explanation += "   • No constraint between Xₖ and " + var_assigned + "\n\n"
            
            explanation += "DOMAIN UPDATE LOGIC:\n"
            explanation += "-" * 70 + "\n"
            explanation += "Updated domain for variable X:\n\n"
            explanation += "              ⎧ D(X) \\ {" + color_assigned + "}     if X ∈ N(" + var_assigned + ")\n"
            explanation += "   D'(X) =   ⎨\n"
            explanation += "              ⎩ D(X)                if X ∉ N(" + var_assigned + ")\n\n"
            
            explanation += "PRUNING POWER:\n"
            explanation += "-" * 70 + "\n"
            explanation += "Forward Checking provides EARLY FAILURE DETECTION:\n\n"
            explanation += "   • If any D'(X) = ∅ → Backtrack immediately\n"
            explanation += "   • Saves exploring entire subtrees\n"
            explanation += "   • Reduces search space exponentially\n\n"
            
            explanation += "FORMAL CORRECTNESS:\n"
            explanation += "If forward checking produces empty domain:\n"
            explanation += "   ⇒ No complete assignment extending current partial assignment\n"
            explanation += "   ⇒ Must backtrack and try alternative value\n\n"
            
        explanation += "COMPLEXITY ANALYSIS:\n"
        explanation += "-" * 70 + "\n"
        explanation += "Per assignment:\n"
        explanation += "   • Check all neighbors: O(|E|) where E = edges\n"
        explanation += "   • Domain updates: O(d) where d = domain size\n"
        explanation += "   • Total: O(|E| × d) per variable assignment\n\n"
        
        explanation += "COMPARISON WITH OTHER TECHNIQUES:\n"
        explanation += "-" * 70 + "\n"
        explanation += "• Naive Backtracking: No lookahead, discovers conflicts late\n"
        explanation += "• Forward Checking: Checks direct neighbors only\n"
        explanation += "• MAC (Maintaining Arc Consistency): Propagates to all variables\n"
        explanation += "• PC (Path Consistency): Considers paths of length 2\n\n"
        
        explanation += "Forward Checking strikes a balance between inference overhead and\n"
        explanation += "pruning effectiveness, making it practical for most CSPs.\n"
        
        return explanation
    
    def _explain_mrv(self, question: str, correct_answer: str) -> str:
        """Explain Minimum Remaining Values (MRV) heuristic"""
        explanation = f"✓ CORRECT ANSWER: {correct_answer}\n\n"
        explanation += "=" * 70 + "\n"
        explanation += "🎯 MINIMUM REMAINING VALUES (MRV) - VARIABLE ORDERING HEURISTIC\n"
        explanation += "=" * 70 + "\n\n"
        
        explanation += "THEORETICAL FOUNDATION\n"
        explanation += "-" * 70 + "\n"
        explanation += "MRV is a dynamic variable ordering heuristic for CSP backtracking search.\n"
        explanation += "Also known as:\n"
        explanation += "   • 'Most Constrained Variable' heuristic\n"
        explanation += "   • 'Fail-First' principle\n"
        explanation += "   • 'Minimum Width' ordering (in some contexts)\n\n"
        
        explanation += "FORMAL DEFINITION:\n"
        explanation += "Given current domains D = {D₁, D₂, ..., Dₙ} for unassigned variables,\n"
        explanation += "select variable Xᵢ such that:\n\n"
        explanation += "   Xᵢ = argmin { |Dⱼ| : Xⱼ ∈ X_{unassigned} }\n\n"
        explanation += "In case of ties (multiple variables with |Dᵢ| = min):\n"
        explanation += "   • Use DEGREE HEURISTIC: choose variable with most constraints\n"
        explanation += "   • Or lexicographic ordering (alphabetical)\n\n"
        
        explanation += "RATIONALE: THE FAIL-FIRST PRINCIPLE\n"
        explanation += "-" * 70 + "\n"
        explanation += "INTUITION:\n"
        explanation += "   \"Choose the variable most likely to cause a failure soon\"\n\n"
        explanation += "WHY THIS WORKS:\n"
        explanation += "1. Variables with small domains are heavily constrained\n"
        explanation += "2. If current path leads to contradiction, detect it EARLY\n"
        explanation += "3. Failing early prevents wasting time on doomed subtrees\n"
        explanation += "4. Early backtracking = exponential savings in search\n\n"
        
        explanation += "MATHEMATICAL JUSTIFICATION:\n"
        explanation += "Let T(n, d, k) = search tree size with:\n"
        explanation += "   • n variables, d domain size, k constraint tightness\n\n"
        explanation += "Bad ordering: T ≈ d^n (explore full depth before detecting failure)\n"
        explanation += "MRV ordering: T ≈ d^(n/2) (detect failures at shallower depths)\n\n"
        explanation += "The exponential reduction in search space makes MRV highly effective.\n\n"
        
        # Extract and analyze domains
        import re
        domain_matches = re.findall(r'Variable (\w+): \{([^}]+)\}', question)
        
        if domain_matches:
            explanation += "INSTANCE ANALYSIS\n"
            explanation += "-" * 70 + "\n"
            explanation += "Current Domain State (after constraint propagation):\n\n"
            
            domain_info = []
            for var, domain_str in domain_matches:
                domain_values = [v.strip() for v in domain_str.split(',')]
                domain_size = len(domain_values)
                domain_info.append((var, domain_size, domain_values))
                explanation += f"   D({var}) = {{{domain_str}}}    |D({var})| = {domain_size}\n"
            
            explanation += "\n"
            
            # Calculate statistics
            min_size = min(size for _, size, _ in domain_info)
            max_size = max(size for _, size, _ in domain_info)
            avg_size = sum(size for _, size, _ in domain_info) / len(domain_info)
            
            explanation += "DOMAIN SIZE STATISTICS:\n"
            explanation += f"   • Minimum: {min_size}\n"
            explanation += f"   • Maximum: {max_size}\n"
            explanation += f"   • Average: {avg_size:.2f}\n\n"
            
            explanation += "MRV COMPUTATION:\n"
            explanation += "-" * 70 + "\n"
            explanation += "Step 1: Find minimum domain size\n"
            explanation += f"   min_size = min{{ |D(X)| : X ∈ X_unassigned }} = {min_size}\n\n"
            
            explanation += "Step 2: Identify all variables with minimum size\n"
            mrv_candidates = [var for var, size, _ in domain_info if size == min_size]
            explanation += f"   MRV_candidates = {{ {', '.join(mrv_candidates)} }}\n\n"
            
            if len(mrv_candidates) > 1:
                explanation += "Step 3: TIE-BREAKING\n"
                explanation += f"   Multiple variables have |D| = {min_size}\n"
                explanation += "   Apply secondary criterion: Alphabetical order\n"
                explanation += f"   Selected: {mrv_candidates[0]}\n\n"
            else:
                explanation += "Step 3: UNIQUE MINIMUM\n"
                explanation += f"   Only {mrv_candidates[0]} has minimum domain size\n"
                explanation += f"   Selected: {mrv_candidates[0]}\n\n"
            
            explanation += "DECISION TREE ANALYSIS:\n"
            explanation += "-" * 70 + "\n"
            selected_var = mrv_candidates[0]
            selected_size = min_size
            
            explanation += f"If we choose {selected_var} (|D| = {selected_size}):\n"
            explanation += f"   • Branching factor: {selected_size}\n"
            explanation += f"   • Subtrees to explore: {selected_size}\n"
            explanation += f"   • If unsatisfiable: Detect after trying {selected_size} values\n\n"
            
            # Show alternative for comparison
            other_vars = [var for var, size, _ in domain_info if size == max_size]
            if other_vars and max_size > min_size:
                explanation += f"If we choose {other_vars[0]} (|D| = {max_size}) instead:\n"
                explanation += f"   • Branching factor: {max_size}\n"
                explanation += f"   • Subtrees to explore: {max_size}\n"
                explanation += f"   • Wasted work: Up to {max_size - min_size} additional branches\n\n"
            
            explanation += "MRV minimizes branching factor → minimizes wasted search.\n\n"
        
        explanation += "FORMAL PROPERTIES\n"
        explanation += "-" * 70 + "\n"
        explanation += "THEOREM (Haralick & Elliott, 1980):\n"
        explanation += "MRV minimizes the expected depth to the first failure in the search tree.\n\n"
        explanation += "PROOF SKETCH:\n"
        explanation += "Let P(X) = probability that variable X leads to unsatisfiable subtree\n"
        explanation += "Variables with smaller domains have:\n"
        explanation += "   • Higher P(X) (more likely to be over-constrained)\n"
        explanation += "   • Fewer branches to explore before detecting failure\n"
        explanation += "Therefore, selecting min |D(X)| optimizes expected search efficiency.\n\n"
        
        explanation += "RELATIONSHIP TO OTHER HEURISTICS\n"
        explanation += "-" * 70 + "\n"
        explanation += "VARIABLE ORDERING HEURISTICS:\n"
        explanation += "1. MRV (this): Choose most constrained variable\n"
        explanation += "   • Dynamic: changes as domains shrink\n"
        explanation += "   • Works well with forward checking\n\n"
        
        explanation += "2. DEGREE HEURISTIC: Choose variable with most constraints\n"
        explanation += "   • Static: computed once at start\n"
        explanation += "   • Used for tie-breaking in MRV\n\n"
        
        explanation += "3. MIN-CONFLICTS: For value ordering (orthogonal to MRV)\n"
        explanation += "   • Once variable chosen, pick value minimizing conflicts\n\n"
        
        explanation += "VALUE ORDERING VS VARIABLE ORDERING:\n"
        explanation += "   • Variable ordering (MRV): WHICH variable to assign next\n"
        explanation += "   • Value ordering: WHAT value to try first for that variable\n"
        explanation += "   • Both are crucial for efficient search\n\n"
        
        explanation += "EMPIRICAL EFFECTIVENESS\n"
        explanation += "-" * 70 + "\n"
        explanation += "On standard CSP benchmarks:\n"
        explanation += "   • Random CSPs: 10-100× speedup vs. static ordering\n"
        explanation += "   • Graph coloring: 5-50× speedup\n"
        explanation += "   • N-Queens: Less impact (uniform domain sizes)\n\n"
        
        explanation += "MRV is most effective when:\n"
        explanation += "   ✓ Domains vary significantly in size\n"
        explanation += "   ✓ Used with constraint propagation (FC, MAC)\n"
        explanation += "   ✓ Problem has high constraint density\n\n"
        
        explanation += "ALGORITHMIC IMPLEMENTATION\n"
        explanation += "-" * 70 + "\n"
        explanation += "PSEUDOCODE:\n"
        explanation += "```\n"
        explanation += "function SELECT-UNASSIGNED-VARIABLE(csp):\n"
        explanation += "    unassigned = {X : X not in assignment}\n"
        explanation += "    \n"
        explanation += "    min_domain_size = ∞\n"
        explanation += "    best_var = null\n"
        explanation += "    \n"
        explanation += "    for X in unassigned:\n"
        explanation += "        domain_size = |DOMAIN[X]|\n"
        explanation += "        \n"
        explanation += "        if domain_size < min_domain_size:\n"
        explanation += "            min_domain_size = domain_size\n"
        explanation += "            best_var = X\n"
        explanation += "        \n"
        explanation += "        elif domain_size == min_domain_size:\n"
        explanation += "            // Tie-breaking: use degree heuristic\n"
        explanation += "            if DEGREE(X) > DEGREE(best_var):\n"
        explanation += "                best_var = X\n"
        explanation += "    \n"
        explanation += "    return best_var\n"
        explanation += "```\n\n"
        
        explanation += "This simple O(n) scan provides enormous search space reduction.\n"
        
        return explanation
    
    def _explain_problem_strategy(self, question: str, correct_answer: str) -> str:
        """Explain why a specific algorithm is best for a problem"""
        explanation = f"✓ CORRECT ANSWER: {correct_answer}\n\n"
        explanation += "=" * 70 + "\n"
        explanation += "🎮 PROBLEM-SPECIFIC ALGORITHM SELECTION\n"
        explanation += "=" * 70 + "\n\n"
        
        # Detect problem type
        question_lower = question.lower()
        
        if 'n-queens' in question_lower:
            explanation += "PROBLEM: N-Queens\n"
            explanation += "-" * 70 + "\n"
            explanation += "Goal: Place N queens on N×N board with no conflicts\n"
            explanation += "Constraint: No two queens attack each other\n\n"
            
            if 'Min-Conflicts' in correct_answer:
                explanation += "WHY MIN-CONFLICTS HEURISTIC?\n"
                explanation += "-" * 70 + "\n"
                explanation += "ALGORITHM:\n"
                explanation += "1. Start with random complete assignment\n"
                explanation += "2. Count conflicts for each queen\n"
                explanation += "3. Select queen with conflicts\n"
                explanation += "4. Move queen to row that minimizes conflicts\n"
                explanation += "5. Repeat until no conflicts\n\n"
                
                explanation += "CONFLICT CALCULATION:\n"
                explanation += "For queen at (col, row):\n"
                explanation += "   conflicts = 0\n"
                explanation += "   for each other queen at (c, r):\n"
                explanation += "       if r == row:  # same row\n"
                explanation += "           conflicts += 1\n"
                explanation += "       if |r - row| == |c - col|:  # diagonal\n"
                explanation += "           conflicts += 1\n\n"
                
                explanation += "ADVANTAGES:\n"
                explanation += "• Works on complete assignments (local search)\n"
                explanation += "• Very fast for large N (N=1000+)\n"
                explanation += "• Usually finds solution in O(N) steps\n"
                explanation += "• Better than backtracking for large boards\n"
                
        elif 'hanoi' in question_lower:
            explanation += "PROBLEM: Hanoi Towers\n"
            explanation += "-" * 70 + "\n"
            explanation += "Goal: Move all disks from source to destination tower\n"
            explanation += "Constraint: Larger disk never on top of smaller disk\n\n"
            
            if 'A*' in correct_answer:
                explanation += "WHY A* SEARCH?\n"
                explanation += "-" * 70 + "\n"
                explanation += "HEURISTIC FUNCTION:\n"
                explanation += "   h(state) = number of disks NOT on goal tower\n\n"
                explanation += "EVALUATION FUNCTION:\n"
                explanation += "   f(n) = g(n) + h(n)\n"
                explanation += "   where g(n) = moves taken so far\n\n"
                
                explanation += "WHY IT'S OPTIMAL:\n"
                explanation += "• h(n) is admissible (never overestimates)\n"
                explanation += "• h(n) is consistent (monotonic)\n"
                explanation += "• Finds optimal solution in 2^n - 1 moves\n\n"
                
                explanation += "COMPARISON:\n"
                explanation += "• Greedy: May take suboptimal path\n"
                explanation += "• A*: Guaranteed optimal (with admissible h)\n"
                
        elif 'graph coloring' in question_lower:
            explanation += "PROBLEM: Graph Coloring\n"
            explanation += "-" * 70 + "\n"
            explanation += "Goal: Assign colors to vertices\n"
            explanation += "Constraint: Adjacent vertices have different colors\n\n"
            
            if 'Forward Checking' in correct_answer:
                explanation += "WHY BACKTRACKING WITH FORWARD CHECKING?\n"
                explanation += "-" * 70 + "\n"
                explanation += "STRATEGY:\n"
                explanation += "1. Order vertices by degree (highest first)\n"
                explanation += "2. When assigning color to vertex v:\n"
                explanation += "   • Remove that color from neighbors' domains\n"
                explanation += "3. If any neighbor has empty domain → backtrack\n\n"
                
                explanation += "DEGREE HEURISTIC:\n"
                explanation += "• High-degree vertices = more constraints\n"
                explanation += "• Assign them first (fail-first principle)\n"
                explanation += "• Reduces branching factor early\n\n"
                
        elif 'knight' in question_lower:
            explanation += "PROBLEM: Knight's Tour\n"
            explanation += "-" * 70 + "\n"
            explanation += "Goal: Visit all squares on chessboard\n"
            explanation += "Constraint: Use only knight moves (L-shaped)\n\n"
            
            if 'Greedy' in correct_answer:
                explanation += "WHY GREEDY BEST-FIRST (Warnsdorff's Rule)?\n"
                explanation += "-" * 70 + "\n"
                explanation += "WARNSDORFF'S HEURISTIC:\n"
                explanation += "Always move to square with fewest onward moves\n\n"
                explanation += "ALGORITHM:\n"
                explanation += "1. From current square, find all valid knight moves\n"
                explanation += "2. For each move, count its number of onward moves\n"
                explanation += "3. Choose move with minimum count (accessibility)\n"
                explanation += "4. Repeat until all squares visited\n\n"
                
                explanation += "WHY IT WORKS:\n"
                explanation += "• Visits hard-to-reach squares first\n"
                explanation += "• Prevents getting trapped in corners\n"
                explanation += "• Near-linear time complexity\n"
                explanation += "• Much faster than backtracking alone\n"
        
        explanation += "\n" + "=" * 70 + "\n"
        explanation += "CONCLUSION:\n"
        explanation += "The algorithm was selected based on problem-specific analysis\n"
        explanation += "considering structure, constraints, and efficiency requirements.\n"
        
        return explanation
    def _explain_search_strategy(self, question: str, correct_answer: str) -> str:
        """General search strategy explanation"""
        explanation = f"✓ CORRECT ANSWER: {correct_answer}\n\n"
        explanation += "🔍 SEARCH STRATEGY ANALYSIS\n\n"
        
        answer_lower = correct_answer.lower()
        
        strategies_info = {
            'backtracking': {
                'type': 'Uninformed, Depth-First with Constraint Checking',
                'time': 'O(b^d) where b=branching, d=depth',
                'space': 'O(d) - only current path',
                'complete': 'Yes',
                'optimal': 'No (finds first solution)',
                'description': 'Builds solution incrementally, backtracks on constraint violation'
            },
            'bfs': {
                'type': 'Uninformed, Breadth-First',
                'time': 'O(b^d)',
                'space': 'O(b^d)',
                'complete': 'Yes (if b finite)',
                'optimal': 'Yes (uniform cost)',
                'description': 'Explores all nodes at depth d before depth d+1'
            },
            'dfs': {
                'type': 'Uninformed, Depth-First',
                'time': 'O(b^m) where m=max depth',
                'space': 'O(bm)',
                'complete': 'No (infinite paths)',
                'optimal': 'No',
                'description': 'Explores deepest node first using stack'
            },
            'a*': {
                'type': 'Informed, Best-First',
                'time': 'O(b^d) worst case',
                'space': 'O(b^d)',
                'complete': 'Yes (admissible h)',
                'optimal': 'Yes (admissible & consistent h)',
                'description': 'f(n) = g(n) + h(n), expands lowest f(n)'
            },
            'greedy': {
                'type': 'Informed, Best-First',
                'time': 'O(b^m)',
                'space': 'O(b^m)',
                'complete': 'No',
                'optimal': 'No',
                'description': 'Expands node closest to goal (by h(n) only)'
            },
            'min-conflicts': {
                'type': 'Local Search, Hill-Climbing Variant',
                'time': 'O(N) average for N-Queens',
                'space': 'O(N)',
                'complete': 'No (can get stuck)',
                'optimal': 'No',
                'description': 'Iteratively reduces constraint violations'
            }
        }
        
        # Find matching strategy
        selected_info = None
        for key, info in strategies_info.items():
            if key in answer_lower:
                selected_info = info
                break
        
        if selected_info:
            explanation += f"ALGORITHM: {correct_answer}\n"
            explanation += "-" * 70 + "\n"
            explanation += f"Type: {selected_info['type']}\n"
            explanation += f"Time Complexity: {selected_info['time']}\n"
            explanation += f"Space Complexity: {selected_info['space']}\n"
            explanation += f"Complete: {selected_info['complete']}\n"
            explanation += f"Optimal: {selected_info['optimal']}\n\n"
            explanation += f"Description: {selected_info['description']}\n\n"
        
        explanation += "WHY THIS STRATEGY?\n"
        explanation += "-" * 70 + "\n"
        explanation += f"'{correct_answer}' is selected based on:\n"
        explanation += "• Problem structure and constraints\n"
        explanation += "• Required completeness/optimality guarantees\n"
        explanation += "• Computational resources (time and memory)\n"
        explanation += "• Specific problem characteristics mentioned\n"
        
        return explanation
    
    def _explain_complexity(self, question: str, correct_answer: str) -> str:
        """Complexity analysis explanation"""
        explanation = f"✓ CORRECT ANSWER: {correct_answer}\n\n"
        explanation += "⏱️ COMPLEXITY ANALYSIS\n\n"
        
        explanation += "BIG-O NOTATION:\n"
        explanation += "f(n) = O(g(n)) ⟺ ∃c, n₀ > 0: f(n) ≤ c·g(n) ∀n ≥ n₀\n\n"
        
        explanation += "COMMON CLASSES (fastest → slowest):\n"
        explanation += "O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2ⁿ) < O(n!)\n\n"
        
        explanation += f"For this problem: {correct_answer}\n"
        
        return explanation
    
    def _explain_graph_theory(self, question: str, correct_answer: str) -> str:
        """Graph theory explanation"""
        explanation = f"✓ CORRECT ANSWER: {correct_answer}\n\n"
        explanation += "📈 GRAPH THEORY\n\n"
        
        if 'coloring' in question.lower():
            explanation += "GRAPH COLORING:\n"
            explanation += "Assign colors to vertices: no adjacent vertices same color\n"
            explanation += "Chromatic number χ(G) = minimum colors needed\n"
            explanation += "χ(G) ≤ Δ(G) + 1 where Δ = max degree\n"
        
        return explanation
    
    def _get_fallback_explanation(self, question: str, correct_answer: str) -> str:
        """Provide a fallback explanation when AI model is unavailable"""
        return (
            f"The correct answer is '{correct_answer}'.\n\n"
            f"This answer directly addresses the question and represents the most accurate "
            f"response based on the course material. The other options, while potentially "
            f"related to the topic, do not correctly answer the specific question asked."
        )

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