from loguru import logger
from mcq_sa_question import McqSAQuestion
from qticonverter.tools.qti_converter import QtiConverter
from qticonverter.tools.markdown_reader import MarkdownReader
import pathlib


class QuestionBank:
    """
    A singleton class that manages a centralized repository of questions.

    This class ensures only one instance exists throughout the application lifecycle,
    providing a global point of access to manage and store all questions in the system.

    Attributes:
        questions (list): A list to hold all questions managed by the singleton instance.
    """
    question_type_abbr = [
        "mcq-sa",   # multiple choice (single answer)
        "mcq-ma",   # multiple choice (multiple answers)
    ]
    _instance = None
    converter: QtiConverter = None
    

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.converter = QtiConverter()
        return cls._instance
    
    def add_question(self, input_file: pathlib.Path):

        """
        Add a question to the question bank.

        Args:
            question: The question object to be added.
        """
        self.reader = MarkdownReader(str(input_file))
        attr = self.reader.get_attrs()
        if 'type' not in attr:
            logger.error("Question type not specified in the input file")
            raise ValueError("Question type not specified in the input file")
        if attr['type'] not in QuestionBank.question_type_abbr:
            logger.error("Unsupported question type: {}", attr['type'])
            raise ValueError(f"Unsupported question type: {attr['type']}")

        question = {
            'type': attr['type'],
            'title': self.reader.get_title(),
            'summary': self.reader.get_summary(),
            'problem_statement': self.reader.get_problem_statement(),
            'options': self.reader.get_options(),
            'feedback': self.reader.get_feedback(),
            'hint': self.reader.get_hint()
        }
        logger.info("Loaded question attributes: {}", question)
        if question['type'] == 'mcq-sa' or question['type'] == 'mcq-ma':
            self._add_mcq_question(question)
    
    def _add_mcq_question(self, question):
        correct_answer = []
        options = [option['ans'] for option in question['options']]
        logger.info("Extracted options: {}", options)

        for option in question['options']:
            option['Score'] = float(option['Score'])
            if option['Score'] != 0:
                correct_answer.append(option['ans'])
                logger.info("Identified correct answer: {}", correct_answer)
        if not correct_answer:
            logger.warning("No correct answer found in options.")
            correct_answer = None

        question_statement = question["problem_statement"]
        # remove non ascii characters
        question_statement = ''.join([i if ord(i) < 128 else ' ' for i in question_statement])
        logger.info("Processed question text: {}", question_statement)


        if question['type'] == 'mcq-sa':
            correct_answer = correct_answer[0] if correct_answer else None
            self.converter.add_multiple_choice_SA(
                question_text=question_statement,
                choices_list=options,
                answer_text=correct_answer
            )
        else:
            self.converter.add_multiple_choice_MA(
                question_text=question_statement,
                choices_list=options,
                answer_text=correct_answer
            )

    def save_package(self, output_path:pathlib.Path) -> bool:
        success = True
        try:
            self.converter.save_package(output_path=output_path)
            logger.info("Successfully saved the package.")
        except Exception as e:
            logger.error("Failed to save the package: {}", e)
            success = False
        return success