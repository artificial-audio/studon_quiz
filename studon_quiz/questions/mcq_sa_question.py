# Copyright (c) 2026 Friedrich-Alexander-Universität Erlangen-Nürnberg
# SPDX-License-Identifier: MIT

import re
from lxml import etree
from studon_quiz.questions.question import Question


class McqSAQuestion(Question):
    """Representation of a single-answer multiple choice question.

    Stores required and optional fields and produces QTI XML for the question.

    Attributes:
        mandatory_fields: Mapping of required field names to values (type, title, 
            options, problem_statement).
        optional_fields: Mapping of optional field names to values (summary, 
            feedback, hint).
    """

    def __init__(self):

        self.mandatory_fields = {
            'type': 'mcq-sa',
            'title': None,
            'options':None,
            'problem_statement': None
        }

        self.optional_fields = {
            'summary': None,
            'feedback':None,
            'hint': None
        }
    
    
    def get_type(self):
        return self.mandatory_fields['type']
    
    def set_title(self, title):
        self.mandatory_fields['title'] = title
    
    def get_title(self):
        return self.mandatory_fields['title']
    
    def set_summary(self, summary):
        self.optional_fields['summary'] = summary
    
    def get_summary(self):
        return self.optional_fields['summary']
    
    def set_problem_statement(self, problem_statement):
        self.mandatory_fields['problem_statement'] = problem_statement
    
    def get_problem_statement(self):
        return self.mandatory_fields['problem_statement']
    
    def set_options(self, options):
        self.mandatory_fields['options'] = options
    
    def get_options(self):
        return self.mandatory_fields['options']
    
    def set_feedback(self, feedback):
        self.optional_fields['feedback'] = feedback
    
    def get_feedback(self):
        return self.optional_fields['feedback']
    
    def set_hint(self, hint):
        self.optional_fields['hint'] = hint
    
    def get_hint(self):
        return self.optional_fields['hint']

    def get_field_names(self):
        return list(self.mandatory_fields.keys()) + list(self.optional_fields.keys())
    
    def isValid(self):
        """Check that all mandatory fields are present.

        Returns:
            bool: True if none of the mandatory fields are None, otherwise False.
        """
        for field_name, field_value in self.mandatory_fields.items():
            if field_value is None:
                return False
        return True

    def is_valid(self):
        """Adapter to satisfy the `Question` abstract interface.

        Returns:
            bool: Result of :meth:`isValid`.
        """
        return self.isValid()

    def to_qti_xml(self, ident: str, author: str = "User", ilias_version: str = "9.16.0") -> etree._Element:
        """Produce the QTI `item` XML element for this question.

        Args:
            ident: Unique identifier for the generated QTI item.
            author: Author name to include in metadata (default provided).
            ilias_version: ILIAS version string to include in metadata.

        Returns:
            lxml.etree._Element: Constructed QTI `item` element containing presentation,
                response processing, feedback and optional hint elements.
        """
        item = etree.Element("item", ident=ident, title=self.get_title(), maxattempts="0")
        qticomment = etree.SubElement(item, "qticomment")
        qticomment.text = self.get_summary() or ""
        
        # Metadata
        itemmetadata = etree.SubElement(item, "itemmetadata")
        itemmetadata.append(self._create_qtimetadata(ident, author, ilias_version))
        
        # Presentation
        item.append(self._create_presentation(ident))
        
        # Response processing
        item.append(self._create_resprocessing())
        
        # Feedback
        for fb in self._create_itemfeedback():
            item.append(fb)
        
        for fb in self._create_feedbackOverall():
            item.append(fb)
        
        hint = self._create_hint()
        if hint is not None:
            item.append(hint)
        
        return item

    def _create_qtimetadata(self, ident: str, author: str, ilias_version: str) -> etree._Element:
        """Create a `qtimetadata` element populated with standard fields.

        Args:
            ident: External id to include in the metadata.
            author: Author name.
            ilias_version: ILIAS version string.

        Returns:
            lxml.etree._Element: The `qtimetadata` element ready to be appended to the item.
        """
        qtimetadata = etree.Element("qtimetadata")
        fields = {
            "ILIAS_VERSION": ilias_version,
            "QUESTIONTYPE": "SINGLE CHOICE QUESTION",
            "AUTHOR": author,
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

    def _create_presentation(self, ident: str) -> etree._Element:
        """Create the `presentation` element with problem statement and options.

        The returned element includes any embedded images converted into
        `matimage` children with attributes preserved.
        """
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
        
        # Extract image references from problem statement with dimensions
        images = self._extract_images_with_dimensions(problem_statement)
        for img_data in images:
            attrs = {"label": img_data['src'], "uri": f"objects/{img_data['filename']}"}
            if img_data['width']:
                attrs['width'] = img_data['width']
            if img_data['height']:
                attrs['height'] = img_data['height']
            etree.SubElement(material, "matimage", **attrs)
        
        # Response (single choice)
        response_lid = etree.SubElement(flow, "response_lid", ident="MCSR", rcardinality="Single")
        render_choice = etree.SubElement(response_lid, "render_choice", shuffle="Yes")

        options = self.get_options() or []
        for idx, opt in enumerate(options):
            resp_label = etree.SubElement(render_choice, "response_label", ident=str(idx))
            resp_material = etree.SubElement(resp_label, "material")
            resp_mattext = etree.SubElement(resp_material, "mattext", texttype="text/xhtml")
            
            # Get option text
            opt_text = opt if isinstance(opt, str) else opt.get('text', '')
            resp_mattext.text = f"<p>{opt_text}</p>"
            
            # Extract image references from option text with dimensions
            images = self._extract_images_with_dimensions(opt_text)
            for img_data in images:
                attrs = {"label": img_data['src'], "uri": f"objects/{img_data['filename']}"}
                if img_data['width']:
                    attrs['width'] = img_data['width']
                if img_data['height']:
                    attrs['height'] = img_data['height']
                etree.SubElement(resp_material, "matimage", **attrs)
                
        return presentation

    def _create_resprocessing(self) -> etree._Element:
        """Create the `resprocessing` element implementing scoring rules.

        Returns
        -------
        lxml.etree._Element
            The `resprocessing` element describing score calculation and
            displayfeedback links for each option.
        """
        resprocessing = etree.Element("resprocessing")
        outcomes = etree.SubElement(resprocessing, "outcomes")
        etree.SubElement(outcomes, "decvar")

        options = self.get_options() or []
        correct_indices = []
        
        for idx, opt in enumerate(options):
            # If option has score
            score = opt.get("score", 0) if isinstance(opt, dict) else 0
            if score > 0:
                correct_indices.append(idx)
                
            respcondition = etree.SubElement(resprocessing, "respcondition", **{"continue": "Yes"})
            conditionvar = etree.SubElement(respcondition, "conditionvar")
            varequal = etree.SubElement(conditionvar, "varequal", respident="MCSR")
            varequal.text = str(idx)
            setvar = etree.SubElement(respcondition, "setvar", action="Add")
            setvar.text = str(score)
            displayfeedback = etree.SubElement(respcondition, "displayfeedback", feedbacktype="Response", linkrefid=f"response_{idx}")
        
        # Add respcondition for overall correct feedback
        if correct_indices:
            rc_correct = etree.SubElement(resprocessing, "respcondition", **{"continue": "Yes"})
            cv_correct = etree.SubElement(rc_correct, "conditionvar")
            # For single answer, assume first correct index is the right one
            varequal_correct = etree.SubElement(cv_correct, "varequal", respident="MCSR")
            varequal_correct.text = str(correct_indices[0])
            etree.SubElement(rc_correct, "displayfeedback", feedbacktype="Response", linkrefid="response_allcorrect")
        
        # Add respcondition for overall wrong feedback
        if correct_indices:
            rc_wrong = etree.SubElement(resprocessing, "respcondition", **{"continue": "Yes"})
            cv_wrong = etree.SubElement(rc_wrong, "conditionvar")
            not_elem = etree.SubElement(cv_wrong, "not")
            varequal_wrong = etree.SubElement(not_elem, "varequal", respident="MCSR")
            varequal_wrong.text = str(correct_indices[0])
            etree.SubElement(rc_wrong, "displayfeedback", feedbacktype="Response", linkrefid="response_onenotcorrect")
        
        return resprocessing

    def _create_itemfeedback(self) -> list:
        """Create a list of per-option `itemfeedback` elements.

        Returns
        -------
        list
            List of `lxml.etree.Element` objects representing feedback for
            each response option.
        """
        feedbacks = []
        options = self.get_options() or []
        for idx, opt in enumerate(options):
            itemfeedback = etree.Element("itemfeedback", ident=f"response_{idx}", view="All")
            flow_mat = etree.SubElement(itemfeedback, "flow_mat")
            material = etree.SubElement(flow_mat, "material")
            fb_text = ""
            if isinstance(opt, dict):
                fb_text = opt.get("feedback", "")
            elif self.get_feedback():
                fb_text = self.get_feedback()
            etree.SubElement(material, "mattext", texttype="text/plain").text = fb_text
            feedbacks.append(itemfeedback)
        return feedbacks

    def _create_feedbackOverall(self) -> list:
        """Create overall feedback elements for correct/wrong outcomes.

        Returns
        -------
        list
            List of `itemfeedback` elements for overall feedback.
        """
        feedbacks = []
        feedback = self.get_feedback()
        
        # Always create response_allcorrect element
        correct_feedback = ""
        if isinstance(feedback, dict) and 'Correct' in feedback:
            correct_feedback = feedback['Correct']
        
        itemfeedback_correct = etree.Element("itemfeedback", ident="response_allcorrect", view="All")
        flow_mat_correct = etree.SubElement(itemfeedback_correct, "flow_mat")
        material_correct = etree.SubElement(flow_mat_correct, "material")
        mattext_correct = etree.SubElement(material_correct, "mattext", texttype="text/xhtml")
        mattext_correct.text = f"<p>{correct_feedback}</p>"
        
        # Extract images from Correct feedback
        if correct_feedback:
            images = self._extract_images_with_dimensions(correct_feedback)
            for img_data in images:
                attrs = {"label": img_data['src'], "uri": f"objects/{img_data['filename']}"}
                if img_data['width']:
                    attrs['width'] = img_data['width']
                if img_data['height']:
                    attrs['height'] = img_data['height']
                etree.SubElement(material_correct, "matimage", **attrs)
        
        feedbacks.append(itemfeedback_correct)
        
        # Always create response_onenotcorrect element
        wrong_feedback = ""
        if isinstance(feedback, dict) and 'Wrong' in feedback:
            wrong_feedback = feedback['Wrong']
        
        itemfeedback_wrong = etree.Element("itemfeedback", ident="response_onenotcorrect", view="All")
        flow_mat_wrong = etree.SubElement(itemfeedback_wrong, "flow_mat")
        material_wrong = etree.SubElement(flow_mat_wrong, "material")
        mattext_wrong = etree.SubElement(material_wrong, "mattext", texttype="text/xhtml")
        mattext_wrong.text = f"<p>{wrong_feedback}</p>"
        
        # Extract images from Wrong feedback
        if wrong_feedback:
            images = self._extract_images_with_dimensions(wrong_feedback)
            for img_data in images:
                attrs = {"label": img_data['src'], "uri": f"objects/{img_data['filename']}"}
                if img_data['width']:
                    attrs['width'] = img_data['width']
                if img_data['height']:
                    attrs['height'] = img_data['height']
                etree.SubElement(material_wrong, "matimage", **attrs)
        
        feedbacks.append(itemfeedback_wrong)
        
        return feedbacks
    
    def _create_hint(self) -> etree._Element:
        """Create a `solutionhint` element when a hint is present.

        Returns
        -------
        lxml.etree._Element or None
            The created `solutionhint` element, or None if no hint data is
            available.
        """
        hint_data = self.get_hint()
        hint = hint_data.get('hint') if isinstance(hint_data, dict) else None
        penalty_points = hint_data.get('penalty', 0) if isinstance(hint_data, dict) else 0
        if hint:
            solutionhint = etree.Element("solutionhint", index="1", points=str(penalty_points))
            etree.SubElement(solutionhint, "p").text = hint
            return solutionhint
        return None

    def _extract_images_with_dimensions(self, text: str) -> list:
        """Parse HTML and extract image attributes including dimensions.

        Args:
            text: HTML text containing one or more `<img>` tags.

        Returns:
            list: A list of dictionaries with keys: ``src``, ``filename``,
                ``width``, and ``height``. Values are strings or ``None`` if
                not present.
        """
        images = []
        # Pattern to match complete img tags
        img_tag_pattern = r'<img[^>]+>'
        img_tags = re.findall(img_tag_pattern, text)
        
        for img_tag in img_tags:
            img_data = {'src': None, 'filename': None, 'width': None, 'height': None}
            
            # Extract src attribute
            src_pattern = r'src=["\']([^"\']+)["\']'
            src_match = re.search(src_pattern, img_tag)
            if src_match:
                img_data['src'] = src_match.group(1)
            
            # Extract title attribute (filename)
            title_pattern = r'title=["\']([^"\']+)["\']'
            title_match = re.search(title_pattern, img_tag)
            if title_match:
                img_data['filename'] = title_match.group(1)
            
            # Extract width attribute
            width_pattern = r'width=["\']([^"\']+)["\']'
            width_match = re.search(width_pattern, img_tag)
            if width_match:
                img_data['width'] = width_match.group(1)
            
            # Extract height attribute
            height_pattern = r'height=["\']([^"\']+)["\']'
            height_match = re.search(height_pattern, img_tag)
            if height_match:
                img_data['height'] = height_match.group(1)
            
            images.append(img_data)
        
        return images