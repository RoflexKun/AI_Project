import json
import random
import os
import heapq

class QuestionGenerator:

    def __init__(self, resources_path):
        templates_path = os.path.join(resources_path, 'question_templates.json')
        with open(templates_path, 'r', encoding='utf-8') as file:
            self.templates = json.load(file)

        self.problems_list = [
            "n-queens",
            "generalised Hanoi",
            "graph coloring",
            "knight's tour"
        ]

        self.all_algorithms_pool = [
            "Random Search",
            "Breadth-First Search (BFS)",
            "Uniform Cost Search",
            "Depth-First Search (DFS)",
            "Iterative Deepening Search (IDS)",
            "Bidirectional Search",
            "Standard Backtracking",
            "Greedy Best-First Search",
            "Hillclimbing",
            "Simulated Annealing",
            "Beam Search",
            "A* Search",
            "IDA* (Iterative Deepening A*)",
            "Min-Conflicts Heuristic",
            "Backtracking with Forward Checking"
        ]

    def generate_problem_instance(self, problem):
        # --- 1. N-QUEENS (Min-Conflicts vs Random) ---
        if problem == 'n-queens':
            return self._race_n_queens()

        # --- 2. GENERALISED HANOI (A* vs Greedy) ---
        elif problem == 'generalised Hanoi':
            return self._race_hanoi_logic()

        # --- 3. GRAPH COLORING (Heuristic vs Naive) ---
        elif problem == 'graph coloring':
            return self._race_graph_coloring()

        # --- 4. KNIGHT'S TOUR (Warnsdorff vs Random) ---
        elif problem == "knight's tour":
            return self._race_knights_tour()

    def _race_n_queens(self):
        n = 8
        board = [random.randint(0, n - 1) for _ in range(n)]  # board[col] = row

        def count_conflicts(current_board):
            conflicts = 0
            for i in range(n):
                for j in range(i + 1, n):
                    if current_board[i] == current_board[j] or abs(current_board[i] - current_board[j]) == abs(i - j):
                        conflicts += 1
            return conflicts

        initial_conflicts = count_conflicts(board)
        instance_str = f"An {n}x{n} board with initial configuration (rows): {board}. Current conflicts: {initial_conflicts}."

        # ALGORITM 1: Min-Conflicts
        mc_board = list(board)
        mc_improved = False
        col_to_fix = random.randint(0, n - 1)
        min_conf = count_conflicts(mc_board)

        for r in range(n):
            mc_board[col_to_fix] = r
            c = count_conflicts(mc_board)
            if c < min_conf:
                min_conf = c
                mc_improved = True

        # ALGORITM 2: Random Walk (Uninformed)
        rw_board = list(board)
        rw_board[col_to_fix] = random.randint(0, n - 1)
        rw_improved = count_conflicts(rw_board) < initial_conflicts

        if mc_improved:
            winner = "Min-Conflicts Heuristic"
        elif rw_improved:
            winner = "Random Search"
        else:
            winner = "Standard Backtracking"

        return instance_str, winner

    def _race_graph_coloring(self):
        nodes = ['A', 'B', 'C', 'D', 'E']
        edges = {}
        for n in nodes:
            edges[n] = []

        edge_desc = []
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                if random.random() > 0.4:
                    u, v = nodes[i], nodes[j]
                    edges[u].append(v)
                    edges[v].append(u)
                    edge_desc.append(f"{u}-{v}")

        instance_str = f"Graph nodes: {nodes}. Edges: {', '.join(edge_desc)}."

        # ALGORITM 1: Degree Heuristic (Smart)
        degrees = {n: len(edges[n]) for n in nodes}
        sorted_nodes = sorted(degrees.items(), key=lambda item: item[1], reverse=True)
        smart_degree = sorted_nodes[0][1]

        # ALGORITM 2: Random Choice (Naive)
        naive_choice = random.choice(nodes)
        naive_degree = degrees[naive_choice]

        if smart_degree > naive_degree:
            winner = "Backtracking with Forward Checking"
        else:
            winner = "Standard Backtracking"

        return instance_str, winner

    def _race_knights_tour(self):

        cols = "ABCDEFGH"
        start_c, start_r = random.randint(0, 7), random.randint(0, 7)
        start_pos_str = f"{cols[start_c]}{start_r + 1}"

        instance_str = f"8x8 Chessboard. Knight at {start_pos_str}. Goal: Visit all squares."

        moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

        def get_valid_moves(c, r):
            valid = []
            for dc, dr in moves:
                nc, nr = c + dc, r + dr
                if 0 <= nc < 8 and 0 <= nr < 8:
                    valid.append((nc, nr))
            return valid

        # ALGORITM 1: Warnsdorff (Greedy Best-First)
        current_moves = get_valid_moves(start_c, start_r)

        if not current_moves:
            return instance_str, "Random Search"

        min_degree = 9

        for (nc, nr) in current_moves:
            degree = len(get_valid_moves(nc, nr))
            if degree < min_degree:
                min_degree = degree

        # ALGORITM 2: Random Choice
        rand_move = random.choice(current_moves)
        rand_degree = len(get_valid_moves(rand_move[0], rand_move[1]))

        if min_degree <= rand_degree:
            winner = "Greedy Best-First Search"
        else:
            winner = "Random Search"

        return instance_str, winner

    def _race_hanoi_logic(self):

        n_disks = random.randint(3, 4)
        optimal_steps_math = 2 ** n_disks - 1
        instance_str = f"Hanoi Towers with {n_disks} disks. Goal: Move stack to the last tower."

        initial_state = (tuple(range(n_disks)), (), ())
        goal_state = ((), (), tuple(range(n_disks)))

        # --- IMPLEMENTARE A* SEARCH ---

        def heuristic(state):
            return n_disks - len(state[2])

        open_set = []
        heapq.heappush(open_set, (heuristic(initial_state), 0, initial_state))

        g_score = {initial_state: 0}

        solution_found_steps = -1

        while open_set:
            current_f, current_g, current_state = heapq.heappop(open_set)

            if current_state == goal_state:
                solution_found_steps = current_g
                break

            towers = [list(t) for t in current_state]

            for source_idx in range(3):
                if not towers[source_idx]:
                    continue

                disk = towers[source_idx][0]

                for target_idx in range(3):
                    if source_idx == target_idx:
                        continue

                    if not towers[target_idx] or towers[target_idx][0] > disk:
                        new_towers = [list(t) for t in current_state]
                        new_towers[source_idx].pop(0)
                        new_towers[target_idx].insert(0, disk)
                        neighbor = tuple(tuple(t) for t in new_towers)

                        tentative_g = current_g + 1

                        if tentative_g < g_score.get(neighbor, float('inf')):
                            g_score[neighbor] = tentative_g
                            f = tentative_g + heuristic(neighbor)
                            heapq.heappush(open_set, (f, tentative_g, neighbor))


        if solution_found_steps == optimal_steps_math:
            winner = "A* Search"
        else:
            winner = "Greedy Best-First Search"

        return instance_str, winner

    def generate_random_question(self):
        category = random.choice(['strategy_simulation', 'nash_equilibrium'])

        if category == 'strategy_simulation':
            return self._gen_strategy()
        elif category == 'nash_equilibrium':
            return self._gen_nash()

    def _generate_wrong_answers(self, problem_answer):
        wrong_answers = set()
        while len(wrong_answers) < 3:
            index = random.randint(0, len(self.all_algorithms_pool)-1)
            if self.all_algorithms_pool[index] == problem_answer:
                continue
            else:
                wrong_answers.add(self.all_algorithms_pool[index])

        return list(wrong_answers)

    def _gen_strategy(self):
        template_obj = random.choice(self.templates['strategy_simulation'])
        raw_text = template_obj['template']

        problem = random.choice(self.problems_list)
        problem_instance, problem_answer = self.generate_problem_instance(problem)

        question_text = raw_text.format(problem_name=problem, instance_details=problem_instance)
        answer_text = problem_answer

        # Generate 3 false answers by selecting all answers that are NOT the correct one
        wrong_answers = self._generate_wrong_answers(answer_text)

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
        while len(wrong_answers) < 3:
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