# Copyright (c) 2026 Friedrich-Alexander-Universität Erlangen-Nürnberg
# SPDX-License-Identifier: MIT

from qti_package_maker.package_interface import QTIPackageInterface
from pathlib import Path


class studon_quiz:
    """Lightweight wrapper around the QTIPackageInterface used in tests.

    The class provides a small convenience API to create and persist a
    QTI package with multiple choice items. It is intentionally small and
    used primarily by the test-suite and examples in this project.
    """

    def __init__(self):
        """Create a `studon_quiz` instance and initialize the packer.

        The underlying `QTIPackageInterface` is instantiated with
        example defaults that are suitable for local testing.
        """
        self.qti_packer = QTIPackageInterface("example_assessment", verbose=True, allow_mixed=True)

    def add_multiple_choice_SA(self, question_text: str, choices_list: list[str], answer_text: str):
        """Add a single-answer multiple choice item to the package.

        Parameters
        ----------
        question_text : str
            The textual problem statement or prompt.
        choices_list : list[str]
            List of possible answer choices.
        answer_text : str
            The correct answer text used by the packer API.
        """
        self.qti_packer.add_item(item_type="MC", item_tuple=(question_text, choices_list, answer_text))

    def add_multiple_choice_MA(self, question_text: str, choices_list: list[str], answer_text: str):
        """Add a multiple-answer multiple choice item to the package.

        Parameters are the same as :meth:`add_multiple_choice_SA` but the
        created item allows multiple correct responses.
        """
        self.qti_packer.add_item(item_type="MA", item_tuple=(question_text, choices_list, answer_text))

    def save_package(self, output_path: Path):
        """Persist the assembled QTI package to `output_path`.

        Parameters
        ----------
        output_path : pathlib.Path
            Path to the output file that will contain the generated
            QTI package (zip).
        """
        self.qti_packer.save_package(engine_name="canvas_qti_v1_2", outfile=str(output_path))