from qticonverter.tools.qti_converter import QtiConverter
from pathlib import Path


def test_qti_converter_save_package(tmp_path: Path):
    output_file_path = tmp_path / "output"
    converter = QtiConverter(output_file_path)
    
    question_text = "What is the capital of France?"
    choices_list = ["Berlin", "Madrid", "Paris"]
    answer_text = "Paris"
    
    converter.add_multiple_choice(question_text=question_text, choices_list=choices_list, answer_text=answer_text)
    
    converter.save_package()
    assert output_file_path.exists()