from pathlib import Path
import shutil
import importlib.resources as pkg_resources

class TemplateGenerationService:
    _questionTemplates = {"mcq-sa":pkg_resources.files("qticonverter")/"markdown_template/mcq-sa.md"}
    def __init__(self,f_name:Path, q_type: str) -> None:
        self._f_name = f_name
        self._q_type = q_type
    
    def generate_template(self):
        success = True
        if self._q_type in TemplateGenerationService._questionTemplates:
            try:
                shutil.copy(src=str(self._questionTemplates[self._q_type]), dst=str(self._f_name))
            except:
                success = False
        return success