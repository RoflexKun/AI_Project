import os
from typing import List, Tuple

class NLPQuestionAnswer:
    def __init__(self, output_folder: str):
        self.output_folder = output_folder
        self.problem_keywords = [
            'n-queens', 'hanoi', 'colorare graf', 'parcurs calului',
            'n queens', 'generalised hanoi', 'graph coloring', "knight's tour"
        ]


    def parse_text_files(self) -> List[tuple]:
        # Recursively search for keywords in all .txt files in output_folder
        # Returns list of (keyword, question, [strategies])
        all_strategies = set()
        for root, dirs, files in os.walk(self.output_folder):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, encoding='utf-8') as f:
                            lines = f.readlines()
                        for i, line in enumerate(lines):
                            if 'search strategies' in line.lower():
                                for j in range(i+1, len(lines)):
                                    l = lines[j].strip()
                                    l_lower = l.lower()
                                    # Stop at blank line or new section
                                    if not l or l.endswith(':') or '?' in l:
                                        break
                                    # Stop collecting if line is blank
                                    if not l:
                                        break
                                    # Skip lines that are not actual strategies
                                    if (
                                        'uninformed' in l_lower or
                                        'informed' in l_lower or
                                        'reasoning' in l_lower or
                                        'deterministic' in l_lower or
                                        ',' in l or
                                        l_lower == 'beam' or
                                        'models' in l_lower or
                                        'problems' in l_lower or
                                        'systems' in l_lower
                                    ):
                                        continue
                                    all_strategies.add(l_lower)
                    except Exception:
                        pass
        # Now, for each keyword found in any file, use the same list of strategies
        found = {}
        for root, dirs, files in os.walk(self.output_folder):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, encoding='utf-8') as f:
                            content = f.read()
                            content_lower = content.lower()
                            for keyword in self.problem_keywords:
                                if keyword.lower() in content_lower and keyword not in found:
                                    found[keyword] = (
                                        keyword,
                                        f"What is the most suitable search strategy for the {keyword} problem?",
                                        sorted([s.lower() for s in all_strategies])
                                    )
                    except Exception:
                        pass
        return list(found.values())

    def generate_questions(self, parsed_data: List[tuple]) -> List[str]:
        # parsed_data: list of (keyword, question, correct_answer_text)
        return [q for _, q, _ in parsed_data]
