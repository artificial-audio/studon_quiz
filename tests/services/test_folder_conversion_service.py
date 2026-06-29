# Copyright (c) 2026 Friedrich-Alexander-Universität Erlangen-Nürnberg
# SPDX-License-Identifier: MIT

from pathlib import Path
from studon_quiz.services.folder_conversion_service import FolderConversionService
import importlib.resources as pkg_resources

def test_folder_conversion_service(tmp_path: Path) -> None:
    inputFolder = pkg_resources.files("studon_quiz")/"markdown_template"
    outputFile = tmp_path/'output.zip'
    service = FolderConversionService(source_folder=inputFolder, output_file=outputFile)
    service.convert()
    newPath = outputFile.parent /(outputFile.stem+'__qpl.zip')
    assert newPath.exists()