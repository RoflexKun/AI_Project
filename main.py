# main.py
import os
from GUI.main_window import Ui_main_window
from tools.question_generator import QuestionGenerator


def get_resources_path() -> str:
    script_path = os.path.abspath(__file__)
    project_path = script_path[: script_path.rfind("\\")]
    return project_path + '\\resources'


if __name__ == '__main__':
    resources_path = get_resources_path()

    q_gen = QuestionGenerator(resources_path)

    output_folder = os.path.abspath(__file__)[: os.path.abspath(__file__).rfind('\\')] + '\\output'

    main_window = Ui_main_window(
        generator=q_gen,
    )
    main_window.start_window()