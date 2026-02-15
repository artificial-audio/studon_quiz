from pathlib import Path
from qticonverter.services.folder_conversion_service import FolderConversionService
import importlib.resources as pkg_resources

def test_folder_conversion_service(tmp_path: Path) -> None:
    inputFolder = pkg_resources.files("qticonverter")/"markdown_template"
    outputFile = tmp_path/'output.zip'
    service = FolderConversionService(source_folder=inputFolder, output_file=outputFile)
    service.convert()
    newPath = outputFile.parent /(outputFile.stem+'__qpl.zip')
    assert newPath.exists()