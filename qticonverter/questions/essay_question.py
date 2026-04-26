import re
from lxml import etree
from qticonverter.questions.question import Question


class EssayQuestion(Question):
    """Representation of an essay (free-text) question.

    The student enters a text answer. The QTI item uses a `response_str`
    element with `fibtype="String"`.

    Attributes:
        mandatory_fields: type, title, problem_statement, correct_answer.
        optional_fields: summary, feedback, hint, maxchars.
    """

    def __init__(self):
        super().__init__()
        self.mandatory_fields = {
            "type": "essay",
            "title": None,
            "problem_statement": None,
            "correct_answer": None,
        }
        self.optional_fields = {
            "summary": None,
            "feedback": None,
            "hint": None,
            "maxchars": None,
            "maxpoints": 10,  # Default: 10 points
        }

    # -- accessors ----------------------------------------------------------
    def get_type(self) -> str:
        return self.mandatory_fields["type"]

    def set_title(self, title: str):
        self.mandatory_fields["title"] = title

    def get_title(self) -> str | None:
        return self.mandatory_fields["title"]

    def set_summary(self, summary: str | None):
        if summary:
            # Preserve paragraph breaks by normalizing whitespace per line
            # while keeping newline separators
            lines = summary.split('\n')
            normalized_lines = [' '.join(line.split()) for line in lines]
            self.optional_fields["summary"] = '\n'.join(normalized_lines)
        else:
            self.optional_fields["summary"] = summary

    def get_summary(self) -> str | None:
        return self.optional_fields["summary"]

    def set_problem_statement(self, problem_statement: str):
        if problem_statement:
            # Preserve paragraph breaks by normalizing whitespace per line/paragraph
            # while keeping newline separators
            lines = problem_statement.split('\n')
            normalized_lines = [' '.join(line.split()) for line in lines]
            self.mandatory_fields["problem_statement"] = '\n'.join(normalized_lines)
        else:
            self.mandatory_fields["problem_statement"] = problem_statement

    def get_problem_statement(self) -> str | None:
        return self.mandatory_fields["problem_statement"]

    def set_correct_answer(self, answer: str):
        self.mandatory_fields["correct_answer"] = answer

    def get_correct_answer(self) -> str | None:
        return self.mandatory_fields["correct_answer"]

    def set_hint(self, hint):
        self.optional_fields["hint"] = hint

    def get_hint(self):
        return self.optional_fields["hint"]

    def set_feedback(self, feedback):
        self.optional_fields["feedback"] = feedback

    def get_feedback(self):
        return self.optional_fields["feedback"]

    def set_maxchars(self, maxchars: int):
        self.optional_fields["maxchars"] = int(maxchars)

    def get_maxchars(self) -> int:
        return self.optional_fields["maxchars"] if self.optional_fields["maxchars"] is not None else 500

    def set_maxpoints(self, maxpoints: int):
        self.optional_fields["maxpoints"] = int(maxpoints)

    def get_maxpoints(self) -> int:
        return self.optional_fields["maxpoints"] if self.optional_fields["maxpoints"] is not None else 10

    def get_options(self) -> None:
        return None

    def get_field_names(self) -> list[str]:
        return list(self.mandatory_fields.keys()) + list(self.optional_fields.keys())

    # -- validation ---------------------------------------------------------
    def isValid(self) -> bool:
        for v in self.mandatory_fields.values():
            if v is None:
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

        # Response processing (simple string match – exact equality)
        item.append(self._create_resprocessing())

        # Feedback
        for fb in self._create_itemfeedback():
            item.append(fb)

        hint = self._create_hint()
        if hint is not None:
            item.append(hint)

        return item

    def _create_qtimetadata(self, ident: str, author: str, ilias_version: str) -> etree._Element:
        qtimetadata = etree.Element("qtimetadata")
        fields = {
            "ILIAS_VERSION": ilias_version,
            "QUESTIONTYPE": "TEXT QUESTION",
            "AUTHOR": author,
            "additional_cont_edit_mode": "default",
            "externalId": ident,
            "ilias_lifecycle": "draft",
            "lifecycle": "draft",
            # TEXT QUESTION specific fields
            "wordcounter": "0",
            "textrating": "ci",
            "matchcondition": "0",
            "termscoring": "YTowOnt9",
            "termrelation": "non",
            "specificfeedback": "non",
        }
        for label, entry in fields.items():
            field = etree.SubElement(qtimetadata, "qtimetadatafield")
            etree.SubElement(field, "fieldlabel").text = label
            etree.SubElement(field, "fieldentry").text = entry
        return qtimetadata

    def _create_presentation(self) -> etree._Element:
        presentation = etree.Element("presentation", label=self.get_title())
        flow = etree.SubElement(presentation, "flow")
        # Problem text
        material = etree.SubElement(flow, "material")
        mattext = etree.SubElement(material, "mattext", texttype="text/xhtml")
        mattext.text = f"<p>{self.get_problem_statement()}</p>"
        # Extract images like other types
        images = self._extract_images_with_dimensions(self.get_problem_statement())
        for img_data in images:
            attrs = {"label": img_data['src'], "uri": f"objects/{img_data['filename']}"}
            if img_data['width']:
                attrs['width'] = img_data['width']
            if img_data['height']:
                attrs['height'] = img_data['height']
            etree.SubElement(material, "matimage", **attrs)
        # Response string - ILIAS human-rated essay format
        response_str = etree.SubElement(
            flow, "response_str", ident="TEXT", rcardinality="Ordered"
        )
        render_fib = etree.SubElement(
            response_str, "render_fib", fibtype="String", prompt="Box", maxchars=str(self.get_maxchars())
        )
        # Add response_label as ILIAS expects
        etree.SubElement(render_fib, "response_label", ident="A")
        return presentation

    def _create_resprocessing(self) -> etree._Element:
        # ILIAS text questions use HumanRater scoremodel
        resprocessing = etree.Element("resprocessing", scoremodel="HumanRater")
        
        # Outcomes with WritingScore - use explicit closing tag
        outcomes = etree.SubElement(resprocessing, "outcomes")
        max_points_str = str(self.get_maxpoints())
        decvar = etree.SubElement(
            outcomes, "decvar", 
            varname="WritingScore", 
            vartype="Integer", 
            minvalue="0", 
            maxvalue=max_points_str
        )
        # Ensure explicit closing tag by setting text
        decvar.text = None
        
        # Condition 1: Check if points were awarded (tutor gave full score)
        rc1 = etree.SubElement(resprocessing, "respcondition", **{"continue": "Yes"})
        cv1 = etree.SubElement(rc1, "conditionvar")
        varequal1 = etree.SubElement(cv1, "varequal", respident="points")
        varequal1.text = max_points_str
        etree.SubElement(rc1, "displayfeedback", feedbacktype="Response", linkrefid="response_allcorrect")
        
        # Condition 2: Points not full (tutor gave partial/no score)
        rc2 = etree.SubElement(resprocessing, "respcondition", **{"continue": "Yes"})
        cv2 = etree.SubElement(rc2, "conditionvar")
        not_el = etree.SubElement(cv2, "not")
        varequal2 = etree.SubElement(not_el, "varequal", respident="points")
        varequal2.text = max_points_str
        etree.SubElement(rc2, "displayfeedback", feedbacktype="Response", linkrefid="response_onenotcorrect")
        
        # Condition 3: Mark as tutor_rated
        rc3 = etree.SubElement(resprocessing, "respcondition")
        cv3 = etree.SubElement(rc3, "conditionvar")
        etree.SubElement(cv3, "other").text = "tutor_rated"
        
        return resprocessing

    def _create_itemfeedback(self) -> list[etree._Element]:
        feedbacks = []
        # Detailed feedback similar to ILIAS format
        fb_data = self.get_feedback()
        
        # Correct detailed feedback (when points=10)
        correct_text = " ".join(fb_data.get("Correct", "").split()) if isinstance(fb_data, dict) else ""
        fb_all = etree.Element("itemfeedback", ident="response_allcorrect", view="All")
        fm_all = etree.SubElement(fb_all, "flow_mat")
        mat_all = etree.SubElement(fm_all, "material")
        mt = etree.SubElement(mat_all, "mattext", texttype="text/xhtml")
        mt.text = f"<p>{correct_text}</p>" if correct_text else ""
        
        # Extract images from Correct feedback
        if correct_text:
            images = self._extract_images_with_dimensions(correct_text)
            for img_data in images:
                attrs = {"label": img_data['src'], "uri": f"objects/{img_data['filename']}"}
                if img_data['width']:
                    attrs['width'] = img_data['width']
                if img_data['height']:
                    attrs['height'] = img_data['height']
                etree.SubElement(mat_all, "matimage", **attrs)
        
        feedbacks.append(fb_all)
        
        # Wrong detailed feedback (when points!=10)
        wrong_text = " ".join(fb_data.get("Wrong", "").split()) if isinstance(fb_data, dict) else ""
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
        hint_text = " ".join(hint_data.get('hint', '').split()) if isinstance(hint_data, dict) else None
        penalty_points = hint_data.get('penalty', 0) if isinstance(hint_data, dict) else 0
        if hint_text:
            # ILIAS format: hint content as HTML-escaped text, not child elements
            solutionhint = etree.Element("solutionhint", index="1", points=str(penalty_points))
            # Escape HTML tags and set as text content
            solutionhint.text = f"&lt;p&gt;{hint_text}&lt;/p&gt;"
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
