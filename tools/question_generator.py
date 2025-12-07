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

        return question_text, answer_text

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

        question_text = raw_text.format(matrix_representation=matrix_str)
        return question_text, ans