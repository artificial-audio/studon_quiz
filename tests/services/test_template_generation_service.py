from qticonverter.services.template_generation_service import TemplateGenerationService
from pathlib import Path 

def test_template_generation_mcq_sa(tmp_path: Path) -> None:
    outputFile = tmp_path/'test.md'
    service = TemplateGenerationService(f_name=outputFile, q_type='mcq-sa')
    service.generate_template()
    assert outputFile.exists()