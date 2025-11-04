
import os


import GUI.main_window
import tools.file_parser
from tools.nlp_question_answer import NLPQuestionAnswer

script_path = os.path.abspath(__file__)

def get_resources_path() -> str:
    project_path = script_path[ : script_path.rfind("\\")]
    return project_path + '\\resources'

if __name__ == '__main__':
    resources_path = get_resources_path()
    print('Resources path: ', resources_path)
    file_parser = tools.file_parser.FileParser(resources_path + '\\courses')
    file_parser.create_output_directory(script_path)
    file_parser.parse_files()

    # NLP Question/Answer integration
    output_folder = script_path[: script_path.rfind('\\')] + '\\output'
    nlp_qa = NLPQuestionAnswer(output_folder)
    parsed_data = nlp_qa.parse_text_files()
    questions = nlp_qa.generate_questions(parsed_data)
    print('Generated Questions:')
    for q in questions:
        print('-', q)

    # Example: verifying an answer (replace with actual user input and reference answer)
    # question = questions[0]
    # user_answer = "Strategia backtracking este potrivită pentru n-queens."
    # reference_answer = "Cea mai potrivită strategie pentru n-queens este backtracking."
    # score = nlp_qa.verify_answer(question, user_answer, reference_answer)
    # print(f'Similarity score: {score:.2f}')

    main_window = GUI.main_window.Ui_main_window(questions=questions, nlp_qa=nlp_qa, parsed_data=parsed_data)
    main_window.start_window()