from lxml import etree
import zipfile
from pathlib import Path

class QTIWriter:
    def __init__(self, questions, author="Bharadwaj Lakuduva Suresh Babu", ilias_version="9.16.0"):
        """
        :param questions: List of McqSAQuestion objects
        """
        self.questions = questions
        self.author = author
        self.ilias_version = ilias_version

    def _create_qtimetadata(self, question, ident):
        qtimetadata = etree.Element("qtimetadata")
        fields = {
            "ILIAS_VERSION": self.ilias_version,
            "QUESTIONTYPE": "MULTIPLE CHOICE QUESTION",
            "AUTHOR": self.author,
            "additional_cont_edit_mode": "default",
            "externalId": ident,
            "ilias_lifecycle": "draft",
            "lifecycle": "draft",
            "thumb_size": "20",
            "feedback_setting": "1",
            "singleline": "0",
        }
        for label, entry in fields.items():
            field = etree.SubElement(qtimetadata, "qtimetadatafield")
            etree.SubElement(field, "fieldlabel").text = label
            etree.SubElement(field, "fieldentry").text = entry
        return qtimetadata

    def _create_presentation(self, question, ident):
        presentation = etree.Element("presentation", label=question.get_title())
        flow = etree.SubElement(presentation, "flow")
        
        # Problem statement
        material = etree.SubElement(flow, "material")
        mattext = etree.SubElement(material, "mattext", texttype="text/xhtml")
        mattext.text = f"<p>{question.get_problem_statement()}</p>"
        
        # Response (multiple choice)
        response_lid = etree.SubElement(flow, "response_lid", ident="MCMR", rcardinality="Multiple")
        render_choice = etree.SubElement(response_lid, "render_choice", shuffle="No")

        options = question.get_options() or []
        for idx, opt in enumerate(options):
            resp_label = etree.SubElement(render_choice, "response_label", ident=str(idx))
            resp_material = etree.SubElement(resp_label, "material")
            resp_mattext = etree.SubElement(resp_material, "mattext", texttype="text/xhtml")
            # If option contains image, include it
            if isinstance(opt, dict) and "image" in opt:
                resp_mattext.text = f'<p><img alt="" src="{opt["image"]}" /></p>'
                etree.SubElement(resp_material, "matimage", label=str(idx), uri=opt["image"])
            else:
                resp_mattext.text = f"<p>{opt if isinstance(opt, str) else opt.get('text','')}</p>"
        return presentation

    def _create_resprocessing(self, question):
        resprocessing = etree.Element("resprocessing")
        outcomes = etree.SubElement(resprocessing, "outcomes")
        etree.SubElement(outcomes, "decvar")

        options = question.get_options() or []
        for idx, opt in enumerate(options):
            # If option has score
            score = opt.get("score", 0) if isinstance(opt, dict) else 0
            respcondition = etree.SubElement(resprocessing, "respcondition", **{"continue": "Yes"})
            conditionvar = etree.SubElement(respcondition, "conditionvar")
            varequal = etree.SubElement(conditionvar, "varequal", respident="MCMR")
            varequal.text = str(idx)
            setvar = etree.SubElement(respcondition, "setvar", action="Add")
            setvar.text = str(score)
            displayfeedback = etree.SubElement(respcondition, "displayfeedback", feedbacktype="Response", linkrefid=f"response_{idx}")
        return resprocessing

    def _create_itemfeedback(self, question):
        feedbacks = []
        options = question.get_options() or []
        for idx, opt in enumerate(options):
            itemfeedback = etree.Element("itemfeedback", ident=f"response_{idx}", view="All")
            flow_mat = etree.SubElement(itemfeedback, "flow_mat")
            material = etree.SubElement(flow_mat, "material")
            fb_text = ""
            if isinstance(opt, dict):
                fb_text = opt.get("feedback", "")
            elif question.get_feedback():
                fb_text = question.get_feedback()
            etree.SubElement(material, "mattext", texttype="text/plain").text = fb_text
            feedbacks.append(itemfeedback)
        return feedbacks

    def write_qti(self, output_file="output"):
        root = etree.Element("questestinterop")

        for q_idx, question in enumerate(self.questions):
            if not question.isValid():
                raise ValueError(f"Question {q_idx} is missing mandatory fields")
            ident = f"q_{q_idx}"  # You can customize ident generation
            item = etree.SubElement(root, "item", ident=ident, title=question.get_title(), maxattempts="0")
            etree.SubElement(item, "qticomment")
            
            # Metadata
            itemmetadata = etree.SubElement(item, "itemmetadata")
            itemmetadata.append(self._create_qtimetadata(question, ident))
            
            # Presentation
            item.append(self._create_presentation(question, ident))
            
            # Response processing
            item.append(self._create_resprocessing(question))
            
            # Feedback
            for fb in self._create_itemfeedback(question):
                item.append(fb)

        tree = etree.ElementTree(root)
        tree.write(output_file, encoding="UTF-8", xml_declaration=True, pretty_print=True)

    # def write_ilias_zip(self, zip_name="export", output_dir="."):
    def write_ilias_zip(self, output_file="output"):
        """
        Writes the QTI XML into an ILIAS-compatible ZIP file:
        - objects/ folder (empty)
        - <zip_name>__qpl.xml (empty)
        - <zip_name>__qti.xml (contains the full XML)
        """
        output_dir = Path(output_file).parent
        package_name = output_file.stem + '__qpl'
        zip_path = output_dir / f"{package_name}.zip"

        # Generate QTI XML to a temporary file
        qti_file_name = f"{output_file.stem}__qti.xml"
        temp_qti_path = output_dir / qti_file_name
        self.write_qti(str(temp_qti_path))

        # Create the ZIP archive
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Empty objects folder
            zf.writestr(f"{package_name}/objects/", "")
            
            # Empty QPL file
            zf.writestr(f"{package_name}/{output_file.stem}__qpl.xml", "")
            
            # QTI XML file
            with open(temp_qti_path, "rb") as f:
                zf.writestr(f"{package_name}/{qti_file_name}", f.read())

        #  Remove temporary XML
        temp_qti_path.unlink()

        print(f"Created ILIAS ZIP: {zip_path}")
        return zip_path

