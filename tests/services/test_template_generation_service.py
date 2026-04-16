# Copyright (c) 2026 Friedrich-Alexander-Universität Erlangen-Nürnberg
# SPDX-License-Identifier: MIT

from qticonverter.services.template_generation_service import TemplateGenerationService
from pathlib import Path 

def test_template_generation_mcq_sa(tmp_path: Path) -> None:
    outputFile = tmp_path/'test.md'
    service = TemplateGenerationService(f_name=outputFile, q_type='mcq-sa')
    service.generate_template()
    assert outputFile.exists()

def test_template_generation_text(tmp_path: Path) -> None:
    outputFile = tmp_path/'test_text.md'
    service = TemplateGenerationService(f_name=outputFile, q_type='text')
    service.generate_template()
    assert outputFile.exists()
    
    # Verify template content
    with open(outputFile, 'r') as f:
        content = f.read()
        assert 'type: text' in content
        assert 'Essay Question' in content