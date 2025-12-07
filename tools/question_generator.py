import json
import random
import os

class QuestionGenerator:

    def __init__(self, resources_path):
        templates_path = os.path.join(resources_path, 'question_templates.json')
        with open(templates_path, 'r', encoding='utf-8') as file:
            self.templates = json.load(file)

        self.strategy_answers = {
            "n-queens": "Backtracking with optimizations (MRV, Forward Checking) or Min-Conflicts for large n.",
            "generalised hanoi": "A* or IDA* with an admissible heuristic (if optimal path is needed) or DFS/Backtracking.",
            "graph coloring": "Backtracking with MRV, LCV and Forward Checking.",
            "knight's tour": "Backtracking with Warnsdorff's heuristic."
        }

    def generate_random_question(self):
        category = random.choice(['strategy', 'nash_equilibrium'])

        if category == 'strategy':
            return self._gen_strategy()
        elif category == 'nash_equilibrium':
            return self._gen_nash()

    def _gen_strategy(self):
        template_obj = random.choice(self.templates['strategy'])
        raw_text = template_obj['template']

        problem = random.choice(list(self.strategy_answers.keys()))

        question_text = raw_text.format(problem_name=problem)
        answer_text = self.strategy_answers[problem]

        # Generate 3 false answers by selecting all answers that are NOT the correct one
        wrong_answers = [v for k, v in self.strategy_answers.items() if k != problem]

        return question_text, answer_text, wrong_answers

    def _gen_nash(self):
        template_obj = random.choice(self.templates['nash_equilibrium'])
        raw_text = template_obj['template']

        matrix = [[(random.randint(-5, 10), random.randint(-5, 10)) for _ in range(2)] for _ in range(2)]

        matrix_str = (
            f"        Player B (Left)   Player B (Right)\n"
            f"A (Up)     {matrix[0][0]}             {matrix[0][1]}\n"
            f"A (Down)   {matrix[1][0]}             {matrix[1][1]}"
        )

        equilibria = []
        for r in range(2):
            for c in range(2):
                val_a, val_b = matrix[r][c]

                best_a = matrix[1 - r][c][0] <= val_a
                best_b = matrix[r][1 - c][1] <= val_b

                if best_a and best_b:
                    row_name = "Up" if r == 0 else "Down"
                    col_name = "Left" if c == 0 else "Right"
                    equilibria.append(f"(A:{row_name}, B:{col_name})")

        if not equilibria:
            ans = "No pure Nash equilibrium exists."
        else:
            ans = "Pure Nash Equilibria: " + ", ".join(equilibria)

        # Generate 3 unique false answers
        possible_fakes = [
            "No pure Nash equilibrium exists.",
            "Pure Nash Equilibria: (A:Up, B:Left)",
            "Pure Nash Equilibria: (A:Up, B:Right)",
            "Pure Nash Equilibria: (A:Down, B:Left)",
            "Pure Nash Equilibria: (A:Down, B:Right)",
            "Pure Nash Equilibria: (A:Up, B:Left), (A:Down, B:Right)",
            "Pure Nash Equilibria: (A:Up, B:Right), (A:Down, B:Left)"
        ]

        wrong_answers = []
        attempts = 0
        while len(wrong_answers) < 3 and attempts < 50:
            fake = random.choice(possible_fakes)
            # Ensure the fake answer is not the correct one and hasn't been added yet
            if fake != ans and fake not in wrong_answers:
                wrong_answers.append(fake)
            attempts += 1

        # Fallback in case we didn't find 3 distinct ones (rare)
        while len(wrong_answers) < 3:
            wrong_answers.append("No pure Nash equilibrium exists.")

        question_text = raw_text.format(matrix_representation=matrix_str)
        return question_text, ans, wrong_answers