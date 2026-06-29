# Copyright (c) 2026 Friedrich-Alexander-Universität Erlangen-Nürnberg
# SPDX-License-Identifier: MIT

from studon_quiz.questions.question_bank import QuestionBank
from pathlib import Path
import importlib.resources as pkg_resources
    
def test_singleton_question_bank():
    qb1 = QuestionBank()
    qb2 = QuestionBank()
    assert qb1 is qb2, "QuestionBank instances are not the same (singleton pattern failed)"

def test_question_bank_conversion_sa(tmp_path) -> None:
    inputFile = pkg_resources.files("studon_quiz")/"markdown_template/mcq-sa.md"
    assert inputFile.exists()
    outputFile = tmp_path/'output.zip'
    question_bank = QuestionBank()
    question_bank.add_question(inputFile)
    question_bank.save_package(output_path=outputFile)
    newPath = outputFile.parent /(outputFile.stem+'__qpl.zip')
    assert newPath.exists()

def test_question_bank_conversion_ma(tmp_path) -> None:
    inputFile = pkg_resources.files("studon_quiz")/"markdown_template/mcq-ma.md"
    assert inputFile.exists()
    outputFile = tmp_path/'output_ma.zip'
    question_bank = QuestionBank()
    question_bank.add_question(inputFile)
    question_bank.save_package(output_path=outputFile)
    newPath = outputFile.parent /(outputFile.stem+'__qpl.zip')
    assert newPath.exists()