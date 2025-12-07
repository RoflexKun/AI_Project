import os
import random

import GUI.main_window
import tools.file_parser
from tools.nlp_question_answer import NLPQuestionAnswer
from tools.question_generator import QuestionGenerator

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

    # Testing QuestionGenerator (Text Only)
    q_gen = QuestionGenerator(resources_path)
    print("\n" + "=" * 60)
    print(" TESTARE GENERARE INTREBARI (MODE: TEXT-ONLY)")
    print("=" * 60)

    for i in range(1, 6):
        print(f"\n>>> TEST {i}")

        try:
            # Now we unpack 3 values: question, correct answer, and the list of wrong answers
            question, correct_ans, wrong_answers = q_gen.generate_random_question()
            options = wrong_answers + [correct_ans]
            random.shuffle(options)

            print(f"INTREBARE GENERATĂ:\n{question}")

            labels = ['a', 'b', 'c', 'd']
            correct_label = None

            for idx, option in enumerate(options):
                current_label = labels[idx]
                print(f"   {current_label}) {option}")

                # Identify which label holds the correct answer
                if option == correct_ans:
                    correct_label = current_label

                # 5. Get User Input
            user_choice = input("\nYour choice (a/b/c/d): ").strip().lower()

            # 6. Validate and Show Result
            if user_choice == correct_label:
                print(f"\n✅ CORRECT! The answer is indeed: {correct_ans}")
            else:
                print(f"\n❌ WRONG. You chose '{user_choice}'.")
                print(f"   The correct answer was '{correct_label}': {correct_ans}")

            input("\nPress Enter to continue to the next question...")

        except Exception as e:
            print(f"A apărut o eroare la generare: {e}")
            import traceback
            traceback.print_exc()

        print("-" * 60)


    # NLP Question/Answer integration
    output_folder = script_path[: script_path.rfind('\\')] + '\\output'
    nlp_qa = NLPQuestionAnswer(output_folder)
    parsed_data = nlp_qa.parse_text_files()  # list of (keyword, question, [strategies])
    questions = nlp_qa.generate_questions(parsed_data)
    strategies_list = [strategies for _, _, strategies in parsed_data]
    print('Generated Questions:')
    for q in questions:
        print('-', q)

    # Example: verifying an answer (replace with actual user input and reference answer)
    # question = questions[0]
    # user_answer = "Strategia backtracking este potrivită pentru n-queens."
    # reference_answer = "Cea mai potrivită strategie pentru n-queens este backtracking."
    # score = nlp_qa.verify_answer(question, user_answer, reference_answer)
    # print(f'Similarity score: {score:.2f}')

    main_window = GUI.main_window.Ui_main_window(questions=questions, nlp_qa=nlp_qa, strategies_list=strategies_list)
    main_window.start_window()