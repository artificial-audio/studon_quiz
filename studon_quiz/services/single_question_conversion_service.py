# Copyright (c) 2026 Friedrich-Alexander-Universität Erlangen-Nürnberg
# SPDX-License-Identifier: MIT

"""Service to convert a single markdown question file into a QTI package.

This module provides a thin service used by the CLI layer and tests to
convert a single markdown file into a QTI package saved at the given
output path.
"""

import pathlib
from studon_quiz.questions.question_bank import QuestionBank


class SingleQuestionConversionService:
    """Convert a single markdown file to a QTI package.

    Args:
        input_file: Path to the markdown input file representing one question.
        output_file: Destination path for the generated QTI package (zip).
    """

    def __init__(self, input_file: pathlib.Path, output_file: pathlib.Path):
        self.input_file = input_file
        self.output_file = output_file
        qb = QuestionBank()
        qb.add_question(self.input_file)

    def convert(self) -> bool:
        """Perform conversion and save the QTI package.

        Returns:
            bool: True when the package was saved successfully, False otherwise.
        """
        qb = QuestionBank()
        return qb.save_package(output_path=self.output_file)