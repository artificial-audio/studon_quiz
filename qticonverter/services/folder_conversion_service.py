# Copyright (c) 2026 Friedrich-Alexander-Universität Erlangen-Nürnberg
# SPDX-License-Identifier: MIT

"""Service to convert all markdown files in a folder into a QTI package.

This module provides :class:`FolderConversionService` which traverses a
source directory for markdown files and assembles them into a single
QTI package saved at the provided output path.
"""

from pathlib import Path
from typing import List, Optional
from qticonverter.questions.question_bank import QuestionBank


class FolderConversionService:
    """Convert a folder of markdown files to a single QTI package.

    Args:
        source_folder: Directory containing markdown files to convert.
        output_file: Destination path for the combined QTI package.
    """

    def __init__(self, source_folder: Path, output_file: Path):
        self.source_folder = source_folder
        self.output_file = output_file

    def convert(self, file_extension: Optional[str] = None) -> bool:
        """Convert all matching files and save the QTI package.

        Args:
            file_extension: If provided, only convert files with this suffix (e.g., '.md').

        Returns:
            bool: True when the package was saved successfully, False otherwise.
        """
        qb = QuestionBank()

        if not self.source_folder.exists():
            raise ValueError(f"Source folder does not exist: {self.source_folder}")

        files = self.source_folder.glob('*.md')

        for file_path in files:
            if file_extension is None or file_path.suffix == file_extension:
                try:
                    qb.add_question(file_path)
                except Exception as e:
                    print(f"Error converting {file_path}: {e}")
        return qb.save_package(self.output_file)