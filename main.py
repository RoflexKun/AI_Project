import os
import random

from GUI.main_window import Ui_main_window
import tools.file_parser
from tools.question_generator import QuestionGenerator
from tools.nlp_question_answer import NLPQuestionAnswer

def get_resources_path() -> str:
    script_path = os.path.abspath(__file__)
    project_path = script_path[: script_path.rfind("\\")]
    return project_path + '\\resources'

if __name__ == '__main__':
    resources_path = get_resources_path()

    # 1️⃣ Parse course files
    # FOR NOW ITS COMMENTED FOR OPTIMISATION REASONS
    #file_parser = tools.file_parser.FileParser(resources_path + '\\courses')
    #file_parser.create_output_directory(os.path.abspath(__file__))
    #file_parser.parse_files()

    # 2️⃣ Generate Multiple Choice Questions
    q_gen = QuestionGenerator(resources_path)
    questions_mc = []
    for _ in range(10):
        try:
            question, correct_ans, wrong_answers, explanation = q_gen.generate_random_question()
            questions_mc.append((question, correct_ans, wrong_answers, explanation))
        except Exception as e:
            print(f"Error generating question: {e}")
            continue

    # 3️⃣ NLP Question/Answer
    output_folder = os.path.abspath(__file__)[: os.path.abspath(__file__).rfind('\\')] + '\\output'
    nlp_qa = NLPQuestionAnswer(output_folder)
    parsed_data = nlp_qa.parse_text_files()  # list of (keyword, question, [strategies])
    questions_nlp = [q for _, q, _ in parsed_data]
    strategies_list = [s for _, _, s in parsed_data]

    # 4️⃣ Combine all questions
    all_questions = questions_mc + questions_nlp

    # 5️⃣ Launch GUI
    main_window = Ui_main_window(
        questions=all_questions,
        nlp_qa=nlp_qa,
        strategies_list=strategies_list
    )
    main_window.start_window()