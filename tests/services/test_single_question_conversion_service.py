# Copyright (c) 2026 Friedrich-Alexander-Universität Erlangen-Nürnberg
# SPDX-License-Identifier: MIT

from pathlib import Path
from qticonverter.services.single_question_conversion_service import SingleQuestionConversionService
import importlib.resources as pkg_resources

def test_single_question_conversion_service(tmp_path: Path) -> None:
    inputFile = pkg_resources.files("qticonverter")/"markdown_template/mcq-sa.md"
    assert Path(inputFile).exists()
    outputFile = tmp_path/'output.zip'
    service = SingleQuestionConversionService(input_file=inputFile, output_file=outputFile)
    service.convert()
    newPath = outputFile.parent /(outputFile.stem+'__qpl.zip')
    assert newPath.exists()