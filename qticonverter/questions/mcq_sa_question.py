import re
from lxml import etree
from qticonverter.questions.question import Question


class McqSAQuestion(Question):
    
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
        for field_name, field_value in self.mandatory_fields.items():
            if field_value is None:
                return False
        return True

    def is_valid(self):
        """Implement abstract method from Question base class"""
        return self.isValid()

    def to_qti_xml(self, ident: str, author: str = "Bharadwaj Lakuduva Suresh Babu", ilias_version: str = "9.16.0") -> etree._Element:
        """
        Generate QTI XML item element for this MCQ Single Answer question.
        
        Args:
            ident: Unique identifier for the question item
            author: Author name for metadata
            ilias_version: ILIAS version string
            
        Returns:
            An lxml etree Element representing the complete QTI item
        """
        item = etree.Element("item", ident=ident, title=self.get_title(), maxattempts="0")
        etree.SubElement(item, "qticomment")
        
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
        """Create QTI metadata element"""
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
        """Create presentation element with problem statement and options"""
        presentation = etree.Element("presentation", label=self.get_title())
        flow = etree.SubElement(presentation, "flow")
        
        # Problem statement
        material = etree.SubElement(flow, "material")
        mattext = etree.SubElement(material, "mattext", texttype="text/xhtml")
        problem_statement = self.get_problem_statement()
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
        """Create response processing element with scoring logic"""
        resprocessing = etree.Element("resprocessing")
        outcomes = etree.SubElement(resprocessing, "outcomes")
        etree.SubElement(outcomes, "decvar")

        options = self.get_options() or []
        for idx, opt in enumerate(options):
            # If option has score
            score = opt.get("score", 0) if isinstance(opt, dict) else 0
            respcondition = etree.SubElement(resprocessing, "respcondition", **{"continue": "Yes"})
            conditionvar = etree.SubElement(respcondition, "conditionvar")
            varequal = etree.SubElement(conditionvar, "varequal", respident="MCSR")
            varequal.text = str(idx)
            setvar = etree.SubElement(respcondition, "setvar", action="Add")
            setvar.text = str(score)
            displayfeedback = etree.SubElement(respcondition, "displayfeedback", feedbacktype="Response", linkrefid=f"response_{idx}")
        return resprocessing

    def _create_itemfeedback(self) -> list:
        """Create per-option feedback elements"""
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
        """Create overall correct/wrong feedback elements"""
        feedbacks = []
        feedback = self.get_feedback()
        if feedback and isinstance(feedback, dict):
            if 'Correct' in feedback:
                correct_feedback = feedback['Correct']
                itemfeedback_correct = etree.Element("itemfeedback", ident="response_allcorrect", view="All")
                flow_mat_correct = etree.SubElement(itemfeedback_correct, "flow_mat")
                material_correct = etree.SubElement(flow_mat_correct, "material")
                etree.SubElement(material_correct, "mattext", texttype="text/xhtml").text = f"<p>{correct_feedback}</p>"
                feedbacks.append(itemfeedback_correct)

            if 'Wrong' in feedback:
                wrong_feedback = feedback['Wrong']
                itemfeedback_wrong = etree.Element("itemfeedback", ident="response_onenotcorrect", view="All")
                flow_mat_wrong = etree.SubElement(itemfeedback_wrong, "flow_mat")
                material_wrong = etree.SubElement(flow_mat_wrong, "material")
                etree.SubElement(material_wrong, "mattext", texttype="text/xhtml").text = f"<p>{wrong_feedback}</p>"
                feedbacks.append(itemfeedback_wrong)
        return feedbacks
    
    def _create_hint(self) -> etree._Element:
        """Create hint element with penalty points"""
        hint_data = self.get_hint()
        hint = hint_data.get('hint') if isinstance(hint_data, dict) else None
        penalty_points = hint_data.get('penalty', 0) if isinstance(hint_data, dict) else 0
        if hint:
            solutionhint = etree.Element("solutionhint", index="1", points=str(penalty_points))
            etree.SubElement(solutionhint, "p").text = hint
            return solutionhint
        return None

    def _extract_images_with_dimensions(self, text: str) -> list:
        """
        Extract image data including src, filename, width, and height from HTML img tags.
        
        Args:
            text: HTML text containing img tags
            
        Returns:
            List of dicts with keys: 'src', 'filename', 'width', 'height'
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