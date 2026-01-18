from pathlib import Path
from typing import List, Optional
from qticonverter.questions.question_bank import QuestionBank

class FolderConversionService:
    def __init__(self, source_folder: Path, output_file: Path):
        self.source_folder = source_folder
        self.output_file = output_file

    def convert(self, file_extension: Optional[str] = None) -> bool:
        qb = QuestionBank()
        
        if not self.source_folder.exists():
            raise ValueError(f"Source folder does not exist: {self.source_folder}")
        
        files = self.source_folder.glob(pattern="*.md")
        
        for file_path in files:
            if file_extension is None or file_path.suffix == file_extension:
                try:
                    qb.add_question(file_path)
                except Exception as e:
                    print(f"Error converting {file_path}: {e}")
        return qb.save_package(self.output_file)