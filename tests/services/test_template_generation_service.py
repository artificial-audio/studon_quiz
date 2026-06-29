# Copyright (c) 2026 Friedrich-Alexander-Universität Erlangen-Nürnberg
# SPDX-License-Identifier: MIT

from studon_quiz.services.template_generation_service import TemplateGenerationService
from pathlib import Path 

def test_template_generation_mcq_sa(tmp_path: Path) -> None:
    outputFile = tmp_path/'test.md'
    service = TemplateGenerationService(f_name=outputFile, q_type='mcq-sa')
    service.generate_template()
    assert outputFile.exists()

def test_template_generation_essay(tmp_path: Path) -> None:
    outputFile = tmp_path/'test_essay.md'
    service = TemplateGenerationService(f_name=outputFile, q_type='essay')
    service.generate_template()
    assert outputFile.exists()
    
    # Verify template content
    with open(outputFile, 'r') as f:
        content = f.read()
        assert 'type: essay' in content
        assert 'Essay Question' in content