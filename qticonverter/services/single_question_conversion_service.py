import pathlib
from qticonverter.questions.question_bank import QuestionBank

class SingleQuestionConversionService:
    question_type_abbr = [
        "mcq-sa",   # multiple choice (single answer)
        "mcq-ma",   # multiple choice (multiple answers)
    ]
    def __init__(self, input_file: pathlib.Path, output_file: pathlib.Path):
        qb = QuestionBank()
        self.input_file = input_file
        self.output_file = output_file
        qb.add_question(self.input_file)

    

    def convert(self) -> bool:
        qb = QuestionBank()
        return qb.save_package(output_path=self.output_file)