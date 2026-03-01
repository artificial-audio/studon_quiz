from pathlib import Path
import shutil
from loguru import logger
import importlib.resources as pkg_resources

class TemplateGenerationService:
    _questionTemplates = {
        "mcq-sa": {
            "template": pkg_resources.files("qticonverter") / "markdown_template/mcq-sa-image.md",
            "resources": [pkg_resources.files("qticonverter") / "markdown_template/images/Photo.png", 
                          pkg_resources.files("qticonverter") / "markdown_template/images/Image2.jpg"]
        },
        "mcq-ma": {
            "template": pkg_resources.files("qticonverter") / "markdown_template/mcq-ma.md",
            "resources": []
        }
    }
    
    def __init__(self, f_name: Path, q_type: str) -> None:
        self._f_name = f_name
        self._q_type = q_type
        logger.info(f"Initialized TemplateGenerationService with file name: {self._f_name} and question type: {self._q_type}")
    
    def generate_template(self):
        success = True
        logger.info(f"Generating template for question type: {self._q_type}")
        if self._q_type in TemplateGenerationService._questionTemplates:
            try:
                template_config = TemplateGenerationService._questionTemplates[self._q_type]
                logger.debug(f"Copying template from {template_config['template']} to {self._f_name}")
                shutil.copy(src=str(template_config["template"]), dst=str(self._f_name))
                
                # Copy associated resources
                for resource in template_config["resources"]:
                    relative_path = Path(*resource.parts[-2:])  # Get last 2 parts (e.g., images/Photo.png)
                    resource_dest = self._f_name.parent / relative_path
                    resource_dest.parent.mkdir(parents=True, exist_ok=True)
                    logger.debug(f"Copying resource from {resource} to {resource_dest}")
                    shutil.copy(src=str(resource), dst=str(resource_dest))
                
                logger.info("Template generated successfully.")
            except Exception as e:
                logger.error(f"Failed to generate template: {e}")
                success = False
        else:
            logger.warning(f"Question type '{self._q_type}' not found in templates.")
            success = False
        return success