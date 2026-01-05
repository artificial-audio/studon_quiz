import pathlib
from ..tools.markdown_reader import MarkdownReader

class SingleQuestionConversionService:
    def __init__(self, input_file: pathlib.Path, output_file: pathlib.Path):
        self.input_file = input_file
        self.output_file = output_file
        self.reader = MarkdownReader(str(self.input_file))
        attr = self.reader.get_attrs()
        if 'type' not in attr:
            raise ValueError("Question type not specified in the input file")
        if attr['type'] != 'mcq-sa':
            raise ValueError(f"Unsupported question type: {attr['type']}")

        self.question = {
            'title': self.reader.get_title(),
            'summary': self.reader.get_summary(),
            'problem_statement': self.reader.get_problem_statement(),
            'options': self.reader.get_options(),
            'feedback': self.reader.get_feedback(),
            'hint': self.reader.get_hint()
        }
    

    def convert(self) -> bool:
        # Placeholder for conversion logic
        try:
            with open(self.input_file, 'r') as infile:
                content = infile.read()
                # Conversion logic would go here
                converted_content = f"<converted>{content}</converted>"

            with open(self.output_file, 'w') as outfile:
                outfile.write(converted_content)

            return True
        except Exception as e:
            print(f"An error occurred during conversion: {e}")
            return False