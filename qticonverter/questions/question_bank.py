# Copyright (c) 2026 Friedrich-Alexander-Universität Erlangen-Nürnberg
# SPDX-License-Identifier: MIT

from loguru import logger
from .mcq_sa_question import McqSAQuestion
from .mcq_ma_question import McqMAQuestion
from .numeric_question import NumericQuestion
from qticonverter.tools.qti_converter import QtiConverter
from qticonverter.tools.markdown_reader import MarkdownReader
from qticonverter.questions.qti_writer import QTIWriter
import pathlib


class QuestionBank:
    """Singleton repository managing questions and coordinating conversion.

    This class implements the singleton pattern to ensure only one instance
    exists throughout the application lifecycle. It coordinates parsing
    markdown files, creating question objects, and orchestrating their
    conversion to QTI packages.

    Attributes
    ----------
    questions : list
        List of Question objects managed by this bank.
    converter : QtiConverter
        Test converter instance initialized at singleton creation.
    """
    question_type_abbr = [
        "mcq-sa",   # multiple choice (single answer)
        "mcq-ma",   # multiple choice (multiple answers)
        "num",      # numeric question
    ]
    _instance = None
    questions = []
    converter: QtiConverter = None
    

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.converter = QtiConverter()
        return cls._instance
    
    def add_question(self, input_file: pathlib.Path):
        """Parse a markdown file and add its question to the bank.

        The function parses the markdown file using `MarkdownReader`,
        validates the question type, instantiates the appropriate
        question class (McqSAQuestion or McqMAQuestion), and appends it
        to the internal questions list.

        Args:
            input_file: Path to the markdown file describing the question.

        Raises:
            ValueError: When the file has no `type` attribute or an unsupported type.
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

        if question['type'] == 'num':
            question['answer_params'] = self.reader.get_answer_params()

        logger.info("Loaded question attributes: {}", question)
        if question['type'] == 'mcq-sa' or question['type'] == 'mcq-ma':
            self._add_mcq_question(question)
        elif question['type'] == 'num':
            self._add_numeric_question(question)
    
    def _add_mcq_question(self, question):
        """Helper to instantiate and add an MCQ question to the bank.

        Args:
            question: Dictionary containing question metadata and fields.
        """
        correct_answer = []
        options = [{"text": option['ans'], "score": float(option['Score']), "feedback": option.get('Remark', '')} for option in question['options']]
        logger.info("Extracted options: {}", options)

        question_statement = question["problem_statement"]
        # remove non ascii characters
        question_statement = ''.join([i if ord(i) < 128 else ' ' for i in question_statement])
        logger.info("Processed question text: {}", question_statement)

        if question['type'] == 'mcq-sa':
            q = McqSAQuestion()
            q.set_title(title=question['title'])
            q.set_problem_statement(question_statement)
            q.set_options(options)  
            q.set_summary(question['summary'])
            q.set_feedback(question['feedback'])
            q.set_hint(question['hint'])
            self.questions.append(q)
        elif question['type'] == 'mcq-ma':
            q = McqMAQuestion()
            q.set_title(title=question['title'])
            q.set_problem_statement(question_statement)
            q.set_options(options)  
            q.set_summary(question['summary'])
            q.set_feedback(question['feedback'])
            q.set_hint(question['hint'])
            self.questions.append(q)

    def _add_numeric_question(self, question: dict):
        """Helper to instantiate and add a numeric question to the bank.

        Args:
            question: Dictionary containing question metadata and fields.
        """
        q = NumericQuestion()
        q.set_title(question['title'])
        q.set_problem_statement(question['problem_statement'])
        q.set_summary(question['summary'])
        q.set_feedback(question['feedback'])
        q.set_hint(question['hint'])

        answer_params = question.get('answer_params', {})
        q.set_correct_answer(float(answer_params.get('correct_answer', 0)))
        q.set_points(float(answer_params.get('points', 1)))
        if 'tolerance' in answer_params:
            q.set_tolerance(float(answer_params['tolerance']))
        if 'maxchars' in answer_params:
            q.set_maxchars(int(answer_params['maxchars']))

        logger.info("Added numeric question: {}", question['title'])
        self.questions.append(q)

    def save_package(self, output_path: pathlib.Path) -> bool:
        """Orchestrate QTI XML generation and ZIP packaging.

        Args:
            output_path: Destination path for the generated QTI package.

        Returns:
            bool: True on successful save, False on error.
        """
        success = True
        try:
            writer = QTIWriter(self.questions)
            writer.write_ilias_zip( output_path)
            logger.info("Successfully saved the package.")
        except Exception as e:
            logger.error("Failed to save the package: {}", e)
            success = False
        return success