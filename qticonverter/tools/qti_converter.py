from qti_package_maker.package_interface import QTIPackageInterface
from pathlib import Path


class QtiConverter:
    def __init__(self, output_path:Path): 
       self.qti_packer = QTIPackageInterface("example_assessment", verbose=True, allow_mixed=True)
       self.output_path = output_path
    
    def add_multiple_choice(self, question_text: str, choices_list: list[str], answer_text: str):
        self.qti_packer.add_item(item_type="MC", item_tuple=(question_text, choices_list, answer_text))
    
    def save_package(self):
        self.qti_packer.save_package(engine_name="canvas_qti_v1_2", outfile=str(self.output_path))