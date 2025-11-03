
import os

import GUI.main_window
import tools.file_parser

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
    main_window = GUI.main_window.Ui_main_window()




    main_window.start_window()