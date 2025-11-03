
import os

from pathlib import Path
from pptx import Presentation

class FileParser:
    output_path = ''

    def __init__(self, file_path):
        self.file_path = Path(file_path)

    def create_output_directory(self, script_path):
        parent_path = script_path[ : script_path.rfind('\\')]

        FileParser.output_path = parent_path + '\\output'
        os.makedirs(FileParser.output_path, exist_ok=True)

    def parse_files(self):
        for file in self.file_path.iterdir():
            file_name = file.name
            if file_name.endswith('.pptx'):
                self.parse_pptx(file)

    def parse_pptx(self, file_path):
        powerpoint_file = Presentation(file_path)
        powerpoint_name = file_path.name[ : file_path.name.rfind('.')]
        print(powerpoint_name)

        output_file_path = FileParser.output_path + '\\' + powerpoint_name + '.txt'

        for slide in powerpoint_file.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    text_frame = shape.text_frame
                    if not Path(output_file_path).exists():
                        Path(output_file_path).write_text(shape.text_frame.text)
                    else:
                        with open(output_file_path, 'a', encoding='utf-8') as output_file:
                            output_file.write(shape.text_frame.text)

