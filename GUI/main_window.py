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
        
        # Detect question type and generate appropriate explanation
        question_lower = question.lower()
        
        # 1. Nash Equilibrium / Game Theory
        if any(keyword in question_lower for keyword in ['nash', 'equilibrium', 'payoff', 'game theory', 'strategy profile', 'best response']):
            return self._explain_nash_equilibrium(question, correct_answer)
        
        # 2. Search Strategies / AI Algorithms
        elif any(keyword in question_lower for keyword in ['search strategy', 'backtracking', 'dfs', 'bfs', 'a*', 'heuristic', 'uninformed', 'informed']):
            return self._explain_search_strategy(question, correct_answer)
        
        # 3. Complexity / Big-O
        elif any(keyword in question_lower for keyword in ['complexity', 'time complexity', 'space complexity', 'big-o', 'o(', 'running time']):
            return self._explain_complexity(question, correct_answer)
        
        # 4. Graph Theory
        elif any(keyword in question_lower for keyword in ['graph', 'vertex', 'edge', 'path', 'cycle', 'tree', 'coloring']):
            return self._explain_graph_theory(question, correct_answer)
        
        # 5. Try AI model for general questions
        elif self.explanation_model:
            try:
                prompt = f"Explain in detail with logical reasoning why '{correct_answer}' is the correct answer to: {question}"
                result = self.explanation_model(prompt, max_length=250, do_sample=False)
                explanation = result[0]['generated_text'].strip()
                if explanation:
                    return explanation
            except Exception as e:
                print(f"Error generating explanation: {e}")
        
        # Fallback
        return self._get_fallback_explanation(question, correct_answer)
    
    def _explain_nash_equilibrium(self, question: str, correct_answer: str) -> str:
        """Detailed explanation for Nash equilibrium problems with calculations"""
        explanation = f"✓ CORRECT ANSWER: {correct_answer}\n\n"
        explanation += "📊 NASH EQUILIBRIUM ANALYSIS:\n\n"
        
        explanation += "DEFINITION:\n"
        explanation += "A Nash Equilibrium is a strategy profile where no player can improve their payoff by unilaterally changing their strategy, given the strategies of other players.\n\n"
        
        explanation += "VERIFICATION PROCESS:\n"
        explanation += "To verify a Nash equilibrium:\n\n"
        
        explanation += "1. PLAYER 1's BEST RESPONSE:\n"
        explanation += "   • Fix Player 2's strategy\n"
        explanation += "   • Check if Player 1 can improve by deviating\n"
        explanation += "   • If current payoff ≥ any alternative payoff → No incentive to deviate\n\n"
        
        explanation += "2. PLAYER 2's BEST RESPONSE:\n"
        explanation += "   • Fix Player 1's strategy\n"
        explanation += "   • Check if Player 2 can improve by deviating\n"
        explanation += "   • If current payoff ≥ any alternative payoff → No incentive to deviate\n\n"
        
        explanation += "MATHEMATICAL CHECK:\n"
        explanation += f"For strategy profile {correct_answer}:\n"
        explanation += "   • u₁(s₁*, s₂*) ≥ u₁(s₁, s₂*) for all s₁ ∈ S₁\n"
        explanation += "   • u₂(s₁*, s₂*) ≥ u₂(s₁*, s₂) for all s₂ ∈ S₂\n\n"
        
        explanation += "Where:\n"
        explanation += "   • uᵢ = payoff function for player i\n"
        explanation += "   • sᵢ* = equilibrium strategy for player i\n"
        explanation += "   • Sᵢ = strategy space for player i\n\n"
        
        explanation += "WHY OTHER OPTIONS ARE WRONG:\n"
        explanation += "The other strategy profiles fail because at least one player has an incentive to deviate (can achieve a strictly higher payoff by changing strategy)."
        
        return explanation
    
    def _explain_search_strategy(self, question: str, correct_answer: str) -> str:
        """Detailed explanation for search strategy problems"""
        explanation = f"✓ CORRECT ANSWER: {correct_answer}\n\n"
        explanation += "🔍 SEARCH STRATEGY ANALYSIS:\n\n"
        
        answer_lower = correct_answer.lower()
        
        if 'backtracking' in answer_lower or 'standard backtracking' in answer_lower:
            explanation += "BACKTRACKING EXPLANATION:\n\n"
            explanation += "ALGORITHM:\n"
            explanation += "1. Build solution incrementally\n"
            explanation += "2. Check constraints at each step\n"
            explanation += "3. If constraint violated → backtrack (undo last choice)\n"
            explanation += "4. Try alternative choices\n"
            explanation += "5. Continue until solution found or all possibilities exhausted\n\n"
            
            explanation += "CHARACTERISTICS:\n"
            explanation += "• Type: Uninformed, depth-first search with constraint checking\n"
            explanation += "• Memory: O(depth) - only stores current path\n"
            explanation += "• Completeness: Yes (finds solution if exists)\n"
            explanation += "• Optimality: Finds first solution, not necessarily optimal\n\n"
            
            explanation += "ADVANTAGES:\n"
            explanation += "• Efficient memory usage\n"
            explanation += "• Natural for constraint satisfaction problems\n"
            explanation += "• Prunes invalid branches early\n\n"
            
        elif 'bfs' in answer_lower or 'breadth-first' in answer_lower:
            explanation += "BREADTH-FIRST SEARCH (BFS):\n\n"
            explanation += "ALGORITHM:\n"
            explanation += "1. Explore all nodes at depth d before depth d+1\n"
            explanation += "2. Use queue (FIFO) for frontier management\n"
            explanation += "3. Expand shallowest unexpanded node first\n\n"
            
            explanation += "PROPERTIES:\n"
            explanation += "• Time Complexity: O(b^d)\n"
            explanation += "• Space Complexity: O(b^d)\n"
            explanation += "• Complete: Yes (if b is finite)\n"
            explanation += "• Optimal: Yes (if step costs are equal)\n\n"
            
            explanation += "WHERE b = branching factor, d = depth of solution\n\n"
            
        elif 'dfs' in answer_lower or 'depth-first' in answer_lower:
            explanation += "DEPTH-FIRST SEARCH (DFS):\n\n"
            explanation += "ALGORITHM:\n"
            explanation += "1. Explore deepest node first\n"
            explanation += "2. Use stack (LIFO) for frontier management\n"
            explanation += "3. Backtrack when reaching dead end\n\n"
            
            explanation += "PROPERTIES:\n"
            explanation += "• Time Complexity: O(b^m)\n"
            explanation += "• Space Complexity: O(bm)\n"
            explanation += "• Complete: No (can get stuck in infinite paths)\n"
            explanation += "• Optimal: No\n\n"
            
            explanation += "WHERE b = branching factor, m = maximum depth\n\n"
            
        elif 'a*' in answer_lower or 'a star' in answer_lower:
            explanation += "A* SEARCH:\n\n"
            explanation += "ALGORITHM:\n"
            explanation += "1. f(n) = g(n) + h(n)\n"
            explanation += "   • g(n) = actual cost from start to n\n"
            explanation += "   • h(n) = estimated cost from n to goal (heuristic)\n"
            explanation += "2. Expand node with lowest f(n) value\n\n"
            
            explanation += "PROPERTIES:\n"
            explanation += "• Complete: Yes (with admissible heuristic)\n"
            explanation += "• Optimal: Yes (with admissible & consistent heuristic)\n"
            explanation += "• Informed search strategy\n\n"
            
            explanation += "ADMISSIBLE HEURISTIC:\n"
            explanation += "h(n) ≤ h*(n) where h*(n) is true cost to goal\n\n"
        
        explanation += "WHY THIS STRATEGY:\n"
        explanation += f"'{correct_answer}' is optimal for this problem based on:\n"
        explanation += "• Problem structure and constraints\n"
        explanation += "• Required completeness and optimality guarantees\n"
        explanation += "• Computational resource constraints (time/memory)\n"
        
        return explanation
    
    def _explain_complexity(self, question: str, correct_answer: str) -> str:
        """Detailed explanation for complexity analysis"""
        explanation = f"✓ CORRECT ANSWER: {correct_answer}\n\n"
        explanation += "⏱️ COMPLEXITY ANALYSIS:\n\n"
        
        explanation += "BIG-O NOTATION:\n"
        explanation += "Describes upper bound on algorithm's growth rate\n"
        explanation += "f(n) = O(g(n)) means: ∃ c, n₀ > 0 such that f(n) ≤ c·g(n) for all n ≥ n₀\n\n"
        
        explanation += "CALCULATION:\n"
        explanation += f"For the given algorithm, the complexity is {correct_answer}\n\n"
        
        explanation += "COMMON COMPLEXITY CLASSES (from fastest to slowest):\n"
        explanation += "• O(1)        - Constant time\n"
        explanation += "• O(log n)    - Logarithmic (binary search)\n"
        explanation += "• O(n)        - Linear (single loop)\n"
        explanation += "• O(n log n)  - Linearithmic (merge sort)\n"
        explanation += "• O(n²)       - Quadratic (nested loops)\n"
        explanation += "• O(n³)       - Cubic (triple nested loops)\n"
        explanation += "• O(2ⁿ)       - Exponential (recursive subproblems)\n"
        explanation += "• O(n!)       - Factorial (permutations)\n\n"
        
        explanation += "ANALYSIS METHOD:\n"
        explanation += "1. Identify loops and recursive calls\n"
        explanation += "2. Count operations as function of input size\n"
        explanation += "3. Focus on dominant term (highest growth rate)\n"
        explanation += "4. Drop constants and lower-order terms\n"
        
        return explanation
    
    def _explain_graph_theory(self, question: str, correct_answer: str) -> str:
        """Detailed explanation for graph theory problems"""
        explanation = f"✓ CORRECT ANSWER: {correct_answer}\n\n"
        explanation += "📈 GRAPH THEORY ANALYSIS:\n\n"
        
        if 'coloring' in question.lower():
            explanation += "GRAPH COLORING:\n\n"
            explanation += "DEFINITION:\n"
            explanation += "Assign colors to vertices such that no two adjacent vertices share the same color.\n\n"
            
            explanation += "CHROMATIC NUMBER χ(G):\n"
            explanation += "Minimum number of colors needed to properly color graph G\n\n"
            
            explanation += "PROPERTIES:\n"
            explanation += "• χ(G) ≤ Δ(G) + 1  (where Δ = maximum degree)\n"
            explanation += "• χ(G) = 2 if and only if G is bipartite\n"
            explanation += "• χ(Kₙ) = n  (complete graph)\n\n"
            
        elif 'path' in question.lower() or 'cycle' in question.lower():
            explanation += "GRAPH PATHS & CYCLES:\n\n"
            explanation += "PATH: Sequence of vertices where each pair is connected by edge\n"
            explanation += "• Simple path: no repeated vertices\n"
            explanation += "• Length: number of edges in path\n\n"
            
            explanation += "CYCLE: Path that starts and ends at same vertex\n"
            explanation += "• Simple cycle: no repeated vertices (except first/last)\n\n"
            
        explanation += "REASONING:\n"
        explanation += f"The answer '{correct_answer}' is correct because it satisfies the graph properties and constraints specified in the question."
        
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