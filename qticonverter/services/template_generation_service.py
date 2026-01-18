from pathlib import Path
import shutil
from loguru import logger
import importlib.resources as pkg_resources

class TemplateGenerationService:
    _questionTemplates = {"mcq-sa": pkg_resources.files("qticonverter") / "markdown_template/mcq-sa.md",
                          "mcq-ma": pkg_resources.files("qticonverter") / "markdown_template/mcq-ma.md"}
    
    def __init__(self, f_name: Path, q_type: str) -> None:
        self._f_name = f_name
        self._q_type = q_type
        logger.info(f"Initialized TemplateGenerationService with file name: {self._f_name} and question type: {self._q_type}")
    
    def generate_template(self):
        success = True
        logger.info(f"Generating template for question type: {self._q_type}")
        if self._q_type in TemplateGenerationService._questionTemplates:
            try:
                logger.debug(f"Copying template from {self._questionTemplates[self._q_type]} to {self._f_name}")
                shutil.copy(src=str(self._questionTemplates[self._q_type]), dst=str(self._f_name))
                logger.info("Template generated successfully.")
            except Exception as e:
                logger.error(f"Failed to generate template: {e}")
                success = False
        else:
            logger.warning(f"Question type '{self._q_type}' not found in templates.")
            success = False
        return success