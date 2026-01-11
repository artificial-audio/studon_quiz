import pathlib
from ..tools.markdown_reader import MarkdownReader
from loguru import logger
from qticonverter.tools.qti_converter import QtiConverter

class SingleQuestionConversionService:
    def __init__(self, input_file: pathlib.Path, output_file: pathlib.Path):
        self.input_file = input_file
        self.output_file = output_file
        self.converter = QtiConverter(output_path=output_file)
        self.reader = MarkdownReader(str(self.input_file))
        logger.info("Initialized MarkdownReader with input file: {}", self.input_file)

        attr = self.reader.get_attrs()
        if 'type' not in attr:
            logger.error("Question type not specified in the input file")
            raise ValueError("Question type not specified in the input file")
        if attr['type'] != 'mcq-sa':
            logger.error("Unsupported question type: {}", attr['type'])
            raise ValueError(f"Unsupported question type: {attr['type']}")

        self.question = {
            'title': self.reader.get_title(),
            'summary': self.reader.get_summary(),
            'problem_statement': self.reader.get_problem_statement(),
            'options': self.reader.get_options(),
            'feedback': self.reader.get_feedback(),
            'hint': self.reader.get_hint()
        }
        logger.info("Loaded question attributes: {}", self.question)

    def convert(self) -> bool:
        success = True
        options = [option['ans'] for option in self.question['options']]
        logger.info("Extracted options: {}", options)

        for option in self.question['options']:
            if option['Score'] == '1':
                correct_answer = option['ans']
                logger.info("Identified correct answer: {}", correct_answer)
                break
        else:
            logger.warning("No correct answer found in options.")
            correct_answer = None

        question = self.question["problem_statement"]
        # remove non ascii characters
        question = ''.join([i if ord(i) < 128 else ' ' for i in question])
        logger.info("Processed question text: {}", question)

        self.converter.add_multiple_choice(
            question_text=question,
            choices_list=options,
            answer_text=correct_answer
        )

        try:
            self.converter.save_package()
            logger.info("Successfully saved the package.")
        except Exception as e:
            logger.error("Failed to save the package: {}", e)
            success = False
        return success
