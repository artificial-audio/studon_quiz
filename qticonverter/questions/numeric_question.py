# Copyright (c) 2026 Friedrich-Alexander-Universität Erlangen-Nürnberg
# SPDX-License-Identifier: MIT

import re
from lxml import etree
from qticonverter.questions.question import Question


class NumericQuestion(Question):
    """Representation of a numeric (fill-in-the-blank decimal) question.

    The student must enter a numeric value within a specified tolerance
    range to receive credit. Produces QTI XML compatible with ILIAS/Studon.

    Attributes:
        mandatory_fields: Mapping of required field names to values (type, title,
            correct_answer, problem_statement, points).
        optional_fields: Mapping of optional field names to values (summary,
            feedback, hint, tolerance, maxchars).
    """

    def __init__(self):
        super().__init__()

        self.mandatory_fields: dict = {
            'type': 'num',
            'title': None,
            'problem_statement': None,
            'correct_answer': None,
            'points': None,
        }

        self.optional_fields: dict = {
            'summary': None,
            'feedback': None,
            'hint': None,
            'tolerance': None,
            'maxchars': None,
        }

    # -- accessors ----------------------------------------------------------

    def get_type(self) -> str:
        return self.mandatory_fields['type']

    def set_title(self, title: str):
        self.mandatory_fields['title'] = title

    def get_title(self) -> str | None:
        return self.mandatory_fields['title']

    def set_summary(self, summary: str | None):
        self.optional_fields['summary'] = summary

    def get_summary(self) -> str | None:
        return self.optional_fields['summary']

    def set_problem_statement(self, problem_statement: str):
        self.mandatory_fields['problem_statement'] = problem_statement

    def get_problem_statement(self) -> str | None:
        return self.mandatory_fields['problem_statement']

    def set_correct_answer(self, correct_answer: float):
        self.mandatory_fields['correct_answer'] = float(correct_answer)

    def get_correct_answer(self) -> float | None:
        return self.mandatory_fields['correct_answer']

    def set_points(self, points: float):
        self.mandatory_fields['points'] = float(points)

    def get_points(self) -> float | None:
        return self.mandatory_fields['points']

    def set_tolerance(self, tolerance: float):
        self.optional_fields['tolerance'] = float(tolerance)

    def get_tolerance(self) -> float:
        return self.optional_fields['tolerance'] if self.optional_fields['tolerance'] is not None else 0.0

    def set_maxchars(self, maxchars: int):
        self.optional_fields['maxchars'] = int(maxchars)

    def get_maxchars(self) -> int:
        return self.optional_fields['maxchars'] if self.optional_fields['maxchars'] is not None else 10

    def set_feedback(self, feedback):
        self.optional_fields['feedback'] = feedback

    def get_feedback(self):
        return self.optional_fields['feedback']

    def set_hint(self, hint):
        self.optional_fields['hint'] = hint

    def get_hint(self):
        return self.optional_fields['hint']

    def get_options(self) -> None:
        """Numeric questions have no options; returns None for API compat."""
        return None

    def get_field_names(self) -> list[str]:
        return list(self.mandatory_fields.keys()) + list(self.optional_fields.keys())

    # -- validation ---------------------------------------------------------

    def isValid(self) -> bool:
        for field_value in self.mandatory_fields.values():
            if field_value is None:
                return False
        return True

    def is_valid(self) -> bool:
        return self.isValid()

    # -- QTI generation -----------------------------------------------------

    def to_qti_xml(self, ident: str, author: str = "User", ilias_version: str = "9.16.0") -> etree._Element:
        item = etree.Element("item", ident=ident, title=self.get_title(), maxattempts="0")

        qticomment = etree.SubElement(item, "qticomment")
        qticomment.text = self.get_summary() or ""

        # Metadata
        itemmetadata = etree.SubElement(item, "itemmetadata")
        itemmetadata.append(self._create_qtimetadata(ident, author, ilias_version))

        # Presentation
        item.append(self._create_presentation())

        # Response processing
        item.append(self._create_resprocessing())

        # Feedback
        for fb in self._create_itemfeedback():
            item.append(fb)

        # Hint
        hint = self._create_hint()
        if hint is not None:
            item.append(hint)

        return item

    def _create_qtimetadata(self, ident: str, author: str, ilias_version: str) -> etree._Element:
        qtimetadata = etree.Element("qtimetadata")
        fields = {
            "ILIAS_VERSION": ilias_version,
            "QUESTIONTYPE": "NUMERIC QUESTION",
            "AUTHOR": author,
            "additional_cont_edit_mode": "default",
            "externalId": ident,
            "ilias_lifecycle": "draft",
            "lifecycle": "draft",
        }
        for label, entry in fields.items():
            field = etree.SubElement(qtimetadata, "qtimetadatafield")
            etree.SubElement(field, "fieldlabel").text = label
            etree.SubElement(field, "fieldentry").text = entry
        return qtimetadata

    def _create_presentation(self) -> etree._Element:
        presentation = etree.Element("presentation", label=self.get_title())
        flow = etree.SubElement(presentation, "flow")

        # Problem statement
        material = etree.SubElement(flow, "material")
        mattext = etree.SubElement(material, "mattext", texttype="text/xhtml")
        problem_statement = self.get_problem_statement()
        # Check if problem statement already contains <p> tags (from markdown parsing)
        # If not, wrap it in a paragraph tag for consistency
        if problem_statement and '<p>' in problem_statement:
            mattext.text = problem_statement
        else:
            mattext.text = f"<p>{problem_statement}</p>"

        # Extract image references from problem statement
        images = self._extract_images_with_dimensions(self.get_problem_statement())
        for img_data in images:
            attrs = {"label": img_data['src'], "uri": f"objects/{img_data['filename']}"}
            if img_data['width']:
                attrs['width'] = img_data['width']
            if img_data['height']:
                attrs['height'] = img_data['height']
            etree.SubElement(material, "matimage", **attrs)

        # Numeric response control
        response_num = etree.SubElement(
            flow, "response_num",
            ident="NUM", rcardinality="Single", numtype="Decimal",
        )
        etree.SubElement(
            response_num, "render_fib",
            fibtype="Decimal", maxchars=str(self.get_maxchars()),
        )

        return presentation

    def _create_resprocessing(self) -> etree._Element:
        resprocessing = etree.Element("resprocessing")
        outcomes = etree.SubElement(resprocessing, "outcomes")
        etree.SubElement(outcomes, "decvar")

        answer = self.get_correct_answer()
        tolerance = self.get_tolerance()
        lower = answer - tolerance
        upper = answer + tolerance
        points = self.get_points()

        # Condition 1: correct range → award points + "Correct" feedback
        rc1 = etree.SubElement(resprocessing, "respcondition")
        cv1 = etree.SubElement(rc1, "conditionvar")
        vargte1 = etree.SubElement(cv1, "vargte", respident="NUM")
        vargte1.text = str(lower)
        varlte1 = etree.SubElement(cv1, "varlte", respident="NUM")
        varlte1.text = str(upper)
        setvar = etree.SubElement(rc1, "setvar", action="Add")
        setvar.text = str(points)
        etree.SubElement(rc1, "displayfeedback", feedbacktype="Response", linkrefid="Correct")

        # Condition 2: correct range → show detailed correct feedback
        rc2 = etree.SubElement(resprocessing, "respcondition", **{"continue": "Yes"})
        cv2 = etree.SubElement(rc2, "conditionvar")
        vargte2 = etree.SubElement(cv2, "vargte", respident="NUM")
        vargte2.text = str(lower)
        varlte2 = etree.SubElement(cv2, "varlte", respident="NUM")
        varlte2.text = str(upper)
        etree.SubElement(rc2, "displayfeedback", feedbacktype="Response", linkrefid="response_allcorrect")

        # Condition 3: NOT in range → show incorrect feedback
        rc3 = etree.SubElement(resprocessing, "respcondition", **{"continue": "Yes"})
        cv3 = etree.SubElement(rc3, "conditionvar")
        not_el = etree.SubElement(cv3, "not")
        vargte3 = etree.SubElement(not_el, "vargte", respident="NUM")
        vargte3.text = str(lower)
        varlte3 = etree.SubElement(not_el, "varlte", respident="NUM")
        varlte3.text = str(upper)
        etree.SubElement(rc3, "displayfeedback", feedbacktype="Response", linkrefid="response_onenotcorrect")

        return resprocessing

    def _create_itemfeedback(self) -> list[etree._Element]:
        feedbacks: list[etree._Element] = []
        feedback_data = self.get_feedback()

        # "Correct" basic feedback (empty by default, matching ILIAS export)
        fb_correct = etree.Element("itemfeedback", ident="Correct", view="All")
        fm_correct = etree.SubElement(fb_correct, "flow_mat")
        mat_correct = etree.SubElement(fm_correct, "material")
        etree.SubElement(mat_correct, "mattext")
        feedbacks.append(fb_correct)

        # Detailed correct feedback
        correct_text = ""
        if isinstance(feedback_data, dict):
            correct_text = feedback_data.get("Correct", "")
        fb_allcorrect = etree.Element("itemfeedback", ident="response_allcorrect", view="All")
        fm_allcorrect = etree.SubElement(fb_allcorrect, "flow_mat")
        mat_allcorrect = etree.SubElement(fm_allcorrect, "material")
        mt_allcorrect = etree.SubElement(mat_allcorrect, "mattext", texttype="text/xhtml")
        mt_allcorrect.text = f"<p>{correct_text}</p>" if correct_text else ""
        
        # Extract images from Correct feedback
        if correct_text:
            images = self._extract_images_with_dimensions(correct_text)
            for img_data in images:
                attrs = {"label": img_data['src'], "uri": f"objects/{img_data['filename']}"}
                if img_data['width']:
                    attrs['width'] = img_data['width']
                if img_data['height']:
                    attrs['height'] = img_data['height']
                etree.SubElement(mat_allcorrect, "matimage", **attrs)
        
        feedbacks.append(fb_allcorrect)

        # Incorrect feedback
        wrong_text = ""
        if isinstance(feedback_data, dict):
            wrong_text = feedback_data.get("Wrong", "")
        fb_wrong = etree.Element("itemfeedback", ident="response_onenotcorrect", view="All")
        fm_wrong = etree.SubElement(fb_wrong, "flow_mat")
        mat_wrong = etree.SubElement(fm_wrong, "material")
        mt_wrong = etree.SubElement(mat_wrong, "mattext", texttype="text/xhtml")
        mt_wrong.text = f"<p>{wrong_text}</p>" if wrong_text else ""
        
        # Extract images from Wrong feedback
        if wrong_text:
            images = self._extract_images_with_dimensions(wrong_text)
            for img_data in images:
                attrs = {"label": img_data['src'], "uri": f"objects/{img_data['filename']}"}
                if img_data['width']:
                    attrs['width'] = img_data['width']
                if img_data['height']:
                    attrs['height'] = img_data['height']
                etree.SubElement(mat_wrong, "matimage", **attrs)
        
        feedbacks.append(fb_wrong)

        return feedbacks

    def _create_hint(self) -> etree._Element | None:
        hint_data = self.get_hint()
        hint_text = hint_data.get('hint') if isinstance(hint_data, dict) else None
        penalty_points = hint_data.get('penalty', 0) if isinstance(hint_data, dict) else 0
        if hint_text:
            solutionhint = etree.Element("solutionhint", index="1", points=str(penalty_points))
            etree.SubElement(solutionhint, "p").text = hint_text
            return solutionhint
        return None

    def _extract_images_with_dimensions(self, text: str) -> list[dict]:
        images = []
        img_tag_pattern = r'<img[^>]+>'
        img_tags = re.findall(img_tag_pattern, text)
        for img_tag in img_tags:
            img_data = {'src': None, 'filename': None, 'width': None, 'height': None}
            src_match = re.search(r'src=["\']([^"\']+)["\']', img_tag)
            if src_match:
                img_data['src'] = src_match.group(1)
            title_match = re.search(r'title=["\']([^"\']+)["\']', img_tag)
            if title_match:
                img_data['filename'] = title_match.group(1)
            width_match = re.search(r'width=["\']([^"\']+)["\']', img_tag)
            if width_match:
                img_data['width'] = width_match.group(1)
            height_match = re.search(r'height=["\']([^"\']+)["\']', img_tag)
            if height_match:
                img_data['height'] = height_match.group(1)
            images.append(img_data)
        return images
