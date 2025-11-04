import os
from typing import List, Tuple

class NLPQuestionAnswer:
    def __init__(self, output_folder: str):
        self.output_folder = output_folder
        self.problem_keywords = [
            'n-queens', 'hanoi', 'colorare graf', 'parcurs calului',
            'n queens', 'generalised hanoi', 'graph coloring', "knight's tour"
        ]

    def parse_text_files(self) -> List[str]:
        # Recursively search for keywords in all .txt files in output_folder
        found_keywords = set()
        for root, dirs, files in os.walk(self.output_folder):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, encoding='utf-8') as f:
                            content = f.read().lower()
                            for keyword in self.problem_keywords:
                                if keyword.lower() in content:
                                    found_keywords.add(keyword)
                    except Exception:
                        pass
        return list(found_keywords)

    def generate_questions(self, found_keywords: List[str]) -> List[str]:
        questions = []
        for keyword in found_keywords:
            questions.append(
                f"Care este cea mai potrivită strategie de rezolvare pentru problema {keyword}?"
            )
        return questions
