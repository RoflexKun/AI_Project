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

    def generate_random_question(self):
        category = random.choice(['strategy_simulation', 'nash_equilibrium', 'csp_evaluation', 'minmax_evaluation'])

        if category == 'strategy_simulation':
            return self._gen_strategy()
        elif category == 'nash_equilibrium':
            return self._gen_nash()
        elif category == 'csp_evaluation':
            return self._gen_csp()
        elif category == 'minmax_evaluation':
            return self._gen_minmax()


    def _gen_minmax(self):
        template_obj = random.choice(self.templates['minmax_evaluation'])
        raw_text = template_obj['template']

        config = random.choice([
            {'depth': 2, 'branching': 3},
            {'depth': 2, 'branching': 2},
            {'depth': 3, 'branching': 2},
        ])

        depth = config['depth']
        branching = config['branching']

        def build_tree(current_depth):
            if current_depth == depth:
                return random.randint(1, 20)
            else:
                return [build_tree(current_depth + 1) for _ in range(branching)]

        game_tree = build_tree(0)

        total_leaves_count = branching ** depth

        instance_details = (
            f"Tree Structure (Nested List): {str(game_tree)}\n"
            f"Depth: {depth}\n"
            f"Branching Factor: {branching}"
        )

        visited_leaves = 0

        def solve_alpha_beta(node, current_depth, is_max, alpha, beta):
            nonlocal visited_leaves

            if isinstance(node, int):
                visited_leaves += 1
                return node

            if is_max:
                best_val = -float('inf')
                for child in node:
                    val = solve_alpha_beta(child, current_depth + 1, False, alpha, beta)
                    best_val = max(best_val, val)
                    alpha = max(alpha, best_val)

                    if beta <= alpha:
                        break
                return best_val
            else:
                best_val = float('inf')
                for child in node:
                    val = solve_alpha_beta(child, current_depth + 1, True, alpha, beta)
                    best_val = min(best_val, val)
                    beta = min(beta, best_val)

                    if beta <= alpha:
                        break
                return best_val

        root_val = solve_alpha_beta(game_tree, 0, True, -float('inf'), float('inf'))

        correct_ans = f"Root: {root_val}, Visited leaves: {visited_leaves}"

        explanation = (
            f"The MinMax algorithm evaluates the tree by propagating values from the leaves. "
            f"Alpha-Beta pruning optimizes this by cutting off branches that won't affect the decision. "
            f"Here, the root value is determined to be {root_val}. Due to pruning, the algorithm only needed "
            f"to visit {visited_leaves} leaves out of a total possible {total_leaves_count}, proving its efficiency."
        )

        wrong_answers = set()
        attempts = 0

        while len(wrong_answers) < 3 and attempts < 50:
            r_val = random.randint(1, 25)

            r_vis = random.randint(1, total_leaves_count)

            candidate = f"Root: {r_val}, Visited leaves: {r_vis}"
            if candidate != correct_ans:
                wrong_answers.add(candidate)

            attempts += 1

        wrong_list = list(wrong_answers)

        return raw_text.format(instance_details=instance_details), correct_ans, wrong_list[:3], explanation

    def generate_problem_instance(self, problem):
        # Now returns 3 values: instance_str, winner, explanation
        if problem == 'n-queens':
            return self._race_n_queens()
        elif problem == 'generalised Hanoi':
            return self._race_hanoi_logic()
        elif problem == 'graph coloring':
            return self._race_graph_coloring()
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
        rw_conf = count_conflicts(rw_board)
        rw_improved = rw_conf < initial_conflicts

        if mc_improved:
            winner = "Min-Conflicts Heuristic"
            explanation = (
                f"The Min-Conflicts heuristic specifically targets the variable with conflicts and chooses the value "
                f"that minimizes them. In this step, it successfully reduced conflicts from {initial_conflicts} to {min_conf}. "
                f"Random search (uninformed) often fails to improve or does so inefficiently."
            )
        elif rw_improved:
            winner = "Random Search"
            explanation = (
                f"In this rare random instance, a random move happened to improve the state to {rw_conf} conflicts. "
                f"Min-Conflicts found no immediate local improvement (plateau), making the random jump the 'winner' for this specific step."
            )
        else:
            winner = "Standard Backtracking"
            explanation = (
                f"Neither the local heuristic (Min-Conflicts) nor the random step found an immediate improvement. "
                f"Standard Backtracking is required to systematically explore the tree and escape this local optimum."
            )

        return instance_str, winner, explanation

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
        smart_node = sorted_nodes[0][0]

        # ALGORITM 2: Random Choice (Naive)
        naive_choice = random.choice(nodes)
        naive_degree = degrees[naive_choice]

        if smart_degree > naive_degree:
            winner = "Backtracking with Forward Checking"
            explanation = (
                f"Efficient graph coloring uses the 'Degree Heuristic' (choosing the most constrained variable first). "
                f"Node {smart_node} has the highest degree ({smart_degree}), imposing the most constraints. "
                f"The random choice {naive_choice} only has degree {naive_degree}. Choosing the most constrained variable first prunes the search tree effectively."
            )
        else:
            winner = "Standard Backtracking"
            explanation = (
                f"In this instance, the random choice picked a node with the same degree as the maximum degree ({smart_degree}). "
                f"Since there is no heuristic advantage in this specific comparison, Standard Backtracking is the baseline correct answer."
            )

        return instance_str, winner, explanation

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
            return instance_str, "Random Search", "No moves available. Any strategy fails."

        min_degree = 9
        best_move = None
        for (nc, nr) in current_moves:
            degree = len(get_valid_moves(nc, nr))
            if degree < min_degree:
                min_degree = degree
                best_move = (nc, nr)

        rand_move = random.choice(current_moves)
        rand_degree = len(get_valid_moves(rand_move[0], rand_move[1]))

        if min_degree <= rand_degree:
            winner = "Greedy Best-First Search"
            explanation = (
                f"Warnsdorff's Rule is a Greedy Best-First strategy that selects the move leading to the square with the fewest onward moves. "
                f"The best move leads to a square with {min_degree} moves, while the random move leads to one with {rand_degree} moves. "
                f"Minimizing the degree prevents the knight from getting stranded early."
            )
        else:
            winner = "Random Search"
            explanation = "Random Search logic fallback (unexpected case)."

        return instance_str, winner, explanation

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
            explanation = (
                f"A* Search combines path cost (g) and heuristic (h) to guarantee optimality. "
                f"For {n_disks} disks, the optimal solution takes {optimal_steps_math} steps. "
                f"A* found the solution in exactly {solution_found_steps} steps. Greedy approaches often yield suboptimal paths."
            )
        else:
            winner = "Greedy Best-First Search"
            explanation = "A suboptimal path was found, which is typical for Greedy Search."

        return instance_str, winner, explanation

    def _solve_forward_checking(self, template_text):
        colors = ['Red', 'Green', 'Blue', 'Yellow', 'Orange', 'Purple', 'Brown']

        number_of_nodes = random.randint(1, 10)
        number_of_colors = random.randint(1, len(colors))

        nodes_used = set()

        for i in range(number_of_nodes):
            nodes_used.add(chr(ord('A') + i))

        colors_used = set()
        while len(colors_used) < number_of_colors:
            colors_used.add(random.choice(colors))
        colors_list = sorted(list(colors_used))

        edges = []
        adjacency = {n: [] for n in nodes_used}
        for i in range(len(nodes_used)):
            for j in range(i + 1, len(nodes_used)):
                if random.random() > 0.5:
                    u, v = nodes_used[i], nodes_used[j]
                    edges.append(f"{u}-{v}")
                    adjacency[u].append(v)
                    adjacency[v].append(u)

        edges_str = ", ".join(edges) if edges else "No constraints (Independent variables)"

        nodes_with_neighbors = [n for n in nodes_used if len(adjacency[n]) > 0]
        assigned_node = random.choice(nodes_with_neighbors) if nodes_with_neighbors else random.choice(nodes_used)
        assigned_color = random.choice(colors_list)

        instance_details = (
            f"Variables: {', '.join(nodes_used)}\n"
            f"Initial Domains: {{{', '.join(colors_list)}}}\n"
            f"Constraints (Edges): {edges_str}\n"
            f"Recent Move: Backtracking assigned {assigned_node} = {assigned_color}"
        )

        full_domain_str = ", ".join(colors_list)
        reduced_domain_list = [c for c in colors_list if c != assigned_color]
        reduced_domain_str = ", ".join(reduced_domain_list)

        ans_parts = []
        neighbors_affected = []
        remaining_nodes = [n for n in nodes_used if n != assigned_node]

        for n in remaining_nodes:
            if n in adjacency[assigned_node]:
                ans_parts.append(f"{n}: {{{reduced_domain_str}}}")
                neighbors_affected.append(n)
            else:
                ans_parts.append(f"{n}: {{{full_domain_str}}}")

        correct_ans = ", ".join(ans_parts)

        explanation = (
            f"Forward Checking maintains consistency by removing the assigned value from the domains of all connected neighbors. "
            f"Here, {assigned_node} was assigned {assigned_color}. Its neighbors are {neighbors_affected}. "
            f"Thus, {assigned_color} must be removed from their domains to satisfy the constraint."
        )

        wrong_answers = set()
        attempts = 0

        while len(wrong_answers) < 3 and attempts < 50:
            current_wrong = []
            for n in remaining_nodes:
                dom = random.choice([full_domain_str, reduced_domain_str])
                current_wrong.append(f"{n}: {{{dom}}}")
            w_str = ", ".join(current_wrong)
            if w_str != correct_ans: wrong_answers.add(w_str)
            attempts += 1
        while len(wrong_answers) < 3: wrong_answers.add("No changes made")

        return template_text.format(instance_details=instance_details), correct_ans, list(wrong_answers)[:3], explanation

    def _gen_csp(self):
        template_obj = random.choice(self.templates['csp_evaluation'])
        raw_text = template_obj['template']

        if 'Forward Checking' in raw_text:
            return self._solve_forward_checking(raw_text)
        else:
            return self._solve_mrv(raw_text)

    def _solve_mrv(self, template_text):
        colors = ['Red', 'Green', 'Blue', 'Yellow', 'Orange', 'Purple', 'Brown']

        number_of_nodes = random.randint(1, 10)
        number_of_colors = random.randint(1, len(colors))

        nodes_used = sorted(list({chr(ord('A') + i) for i in range(number_of_nodes)}))
        colors_list = random.sample(colors, min(len(colors), number_of_colors))
        colors_list.sort()

        domain_state = {}
        for node in nodes_used:
            size = random.randint(1, len(colors_list))
            domain_state[node] = sorted(random.sample(colors_list, size))

        display_lines = [f"   Variable {node}: {{{', '.join(cols)}}}" for node, cols in domain_state.items()]
        random.shuffle(display_lines)
        instance_details = "Current Domains:\n" + "\n".join(display_lines)

        min_len = min(len(cols) for cols in domain_state.values())
        winners = [n for n, cols in domain_state.items() if len(cols) == min_len]
        winners.sort()

        best_var = winners[0]
        correct_ans = f"Variable {best_var} (size {min_len})"

        explanation = (
            f"The MRV (Minimum Remaining Values) heuristic optimizes CSP solving by selecting the variable "
            f"with the fewest legal values left in its domain. This helps identify failures early. "
            f"Variable {best_var} has the smallest domain size ({min_len}), making it the correct choice."
        )

        wrong_answers = set()
        attempts = 0

        while len(wrong_answers) < 3 and attempts < 50:
            node = random.choice(nodes_used)
            size = len(domain_state[node])
            fake = f"Variable {node} (size {size})"
            if size > min_len: wrong_answers.add(fake)
            elif size == min_len and node != best_var: wrong_answers.add(f"Variable {node} (random tie)")
            attempts += 1
        while len(wrong_answers) < 3: wrong_answers.add("Any variable")

        return template_text.format(instance_details=instance_details), correct_ans, list(wrong_answers)[:3], explanation

    def _generate_wrong_answers(self, problem_answer):

        pool = [algo for algo in self.all_algorithms_pool if algo != problem_answer]
        return random.sample(pool, min(3, len(pool)))

    def _gen_strategy(self):
        template_obj = random.choice(self.templates['strategy_simulation'])
        raw_text = template_obj['template']

        problem = random.choice(self.problems_list)
        
        problem_instance, problem_answer, explanation = self.generate_problem_instance(problem)

        question_text = raw_text.format(problem_name=problem, instance_details=problem_instance)
        wrong_answers = self._generate_wrong_answers(problem_answer)

        return question_text, problem_answer, wrong_answers, explanation

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
        analysis_lines = []
        for r in range(2):
            for c in range(2):
                val_a, val_b = matrix[r][c]
                alt_a = matrix[1 - r][c][0]
                best_a = alt_a <= val_a
                
                alt_b = matrix[r][1 - c][1]
                best_b = alt_b <= val_b

                if best_a and best_b:
                    row_name = "Up" if r == 0 else "Down"
                    col_name = "Left" if c == 0 else "Right"
                    equilibria.append(f"(A:{row_name}, B:{col_name})")
                    analysis_lines.append(f"- (A:{row_name}, B:{col_name}) is stable: A ({val_a} >= {alt_a}) and B ({val_b} >= {alt_b}) cannot improve.")

        if not equilibria:
            ans = "No pure Nash equilibrium exists."
            explanation = "Checking all 4 outcomes reveals that in every case, at least one player can improve their payoff by unilaterally switching strategy."
        else:
            ans = "Pure Nash Equilibria: " + ", ".join(equilibria)
            explanation = "A Nash Equilibrium is a state where no player benefits from changing strategy alone.\n" + "\n".join(analysis_lines)

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
        while len(wrong_answers) < 3 and attempts < 100:
            fake = random.choice(possible_fakes)
            # Ensure the fake answer is not the correct one and hasn't been added yet
            if fake != ans and fake not in wrong_answers:
                wrong_answers.append(fake)
            attempts += 1
        while len(wrong_answers) < 3: wrong_answers.append("No pure Nash equilibrium exists.")

        return raw_text.format(matrix_representation=matrix_str), ans, wrong_answers, explanation