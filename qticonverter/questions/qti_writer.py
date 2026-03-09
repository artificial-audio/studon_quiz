# Copyright (c) 2026 Friedrich-Alexander-Universität Erlangen-Nürnberg
# SPDX-License-Identifier: MIT

from lxml import etree
import zipfile
from pathlib import Path
import re
from qticonverter.questions.qti_helpers import QTIImageExtractor, QTIImageLocator



class QTIWriter:
    def __init__(self, questions, author="User", ilias_version="9.16.0"):
        """
        :param questions: List of Question objects (McqSAQuestion, McqMAQuestion, etc.)
        """
        self.questions = questions
        self.author = author
        self.ilias_version = ilias_version
        
    def write_qti(self, output_file="output"):
        """Generate QTI XML and write to a file.

        Args:
            output_file: Path to write the QTI XML file (default: 'output').

        Raises:
            ValueError: When any question is missing mandatory fields.
        """
        root = etree.Element("questestinterop")

        for q_idx, question in enumerate(self.questions):
            if not question.is_valid():
                raise ValueError(f"Question {q_idx} is missing mandatory fields")
            ident = f"q_{q_idx}"
            # Use the question's to_qti_xml method to generate the item
            item = question.to_qti_xml(ident, self.author, self.ilias_version)
            root.append(item)
        
        tree = etree.ElementTree(root)
        tree.write(output_file, encoding="UTF-8", xml_declaration=True, pretty_print=True)


    def write_ilias_zip(self, output_file="output"):
        """Generate and package QTI XML with images into an ILIAS ZIP.

        The generated ZIP archive has the structure:
        - `<name>__qpl/` (directory)
            - `objects/` (directory containing referenced image files)
            - `<name>__qpl.xml` (empty metadata file)
            - `<name>__qti.xml` (full QTI XML)

        Args:
            output_file: Path stem for the output ZIP and internal XML files.

        Returns:
            pathlib.Path: Path to the created ZIP file.
        """
        output_dir = Path(output_file).parent
        package_name = output_file.stem + '__qpl'
        zip_path = output_dir / f"{package_name}.zip"

        # Generate QTI XML to a temporary file
        qti_file_name = f"{output_file.stem}__qti.xml"
        temp_qti_path = output_dir / qti_file_name
        self.write_qti(str(temp_qti_path))

        # Collect all unique images from all questions
        all_images = set()
        for question in self.questions:
            all_images.update(QTIImageExtractor.collect_all_images_from_question(question))

        # Create the ZIP archive
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Empty objects folder
            zf.writestr(f"{package_name}/objects/", "")
            
            # Locate and copy image files to objects folder
            found_images, missing_images = QTIImageLocator.locate_images(all_images, output_dir)
            
            for img_name, img_path in found_images.items():
                with open(img_path, "rb") as f:
                    zf.writestr(f"{package_name}/objects/{img_name}", f.read())
            
            # Warn about missing images
            for img_name in missing_images:
                print(f"Warning: Image file not found: {img_name}")
            
            # Empty QPL file
            zf.writestr(f"{package_name}/{output_file.stem}__qpl.xml", "")
            
            # QTI XML file
            with open(temp_qti_path, "rb") as f:
                zf.writestr(f"{package_name}/{qti_file_name}", f.read())

        # Remove temporary XML
        temp_qti_path.unlink()

        print(f"Created ILIAS ZIP: {zip_path}")
        return zip_path

