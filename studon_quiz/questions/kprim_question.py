# Copyright (c) 2026 Friedrich-Alexander-Universität Erlangen-Nürnberg
# SPDX-License-Identifier: MIT

from lxml import etree
from studon_quiz.questions.mcq_ma_question import McqMAQuestion


class KprimQuestion(McqMAQuestion):
    """ILIAS Kprim choice: exactly four statements, each judged true or false.

    The student marks every statement right or wrong. A statement is true when
    its option score is positive. Full points need all four judgements right;
    with partial scoring, three of four give half the points (ILIAS rule).

    The QTI layout follows ILIAS 9 (assKprimChoiceExport / assKprimChoiceImport):
    QUESTIONTYPE "KPRIM CHOICE QUESTION", one condition per statement whose
    varequal content is its correctness (1/0), and the points in the SCORE
    decvar, where minvalue > 0 switches partial scoring on.
    """

    NUM_ANSWERS = 4

    def __init__(self, points: float = 1.0, partial_scoring: bool = True):
        super().__init__()
        self.mandatory_fields['type'] = 'kprim'
        self.points = points
        self.partial_scoring = partial_scoring

    def isValid(self):
        return super().isValid() and len(self.get_options()) == self.NUM_ANSWERS

    def _correct(self):
        return [opt.get('score', 0) > 0 for opt in self.get_options()]

    def _create_qtimetadata(self, ident: str, author: str, ilias_version: str) -> etree._Element:
        qtimetadata = etree.Element("qtimetadata")
        fields = {
            "ILIAS_VERSION": ilias_version,
            "QUESTIONTYPE": "KPRIM CHOICE QUESTION",
            "AUTHOR": author,
            "additional_cont_edit_mode": "default",
            "externalId": ident,
            "answer_type": "singleLine",
            "thumb_size": "150",
            "option_label_setting": "right_wrong",
            "custom_true_option_label": "",
            "custom_false_option_label": "",
            "feedback_setting": "1",  # show the feedback of every statement
        }
        for label, entry in fields.items():
            field = etree.SubElement(qtimetadata, "qtimetadatafield")
            etree.SubElement(field, "fieldlabel").text = label
            etree.SubElement(field, "fieldentry").text = entry
        return qtimetadata

    def _create_resprocessing(self) -> etree._Element:
        resprocessing = etree.Element("resprocessing")
        outcomes = etree.SubElement(resprocessing, "outcomes")
        etree.SubElement(outcomes, "decvar", varname="SCORE", vartype="Decimal", defaultval="0",
                         minvalue=str(self.points / 2 if self.partial_scoring else 0),
                         maxvalue=str(self.points))
        correct = self._correct()
        for idx, ok in enumerate(correct):
            rc = etree.SubElement(resprocessing, "respcondition", **{"continue": "Yes"})
            cv = etree.SubElement(rc, "conditionvar")
            etree.SubElement(cv, "varequal", respident=str(idx)).text = "1" if ok else "0"
            etree.SubElement(rc, "displayfeedback", feedbacktype="Response", linkrefid=f"response_{idx}")

        rc_all = etree.SubElement(resprocessing, "respcondition", **{"continue": "Yes"})
        cv_and = etree.SubElement(etree.SubElement(rc_all, "conditionvar"), "and")
        for idx, ok in enumerate(correct):
            etree.SubElement(cv_and, "varequal", respident=str(idx)).text = "1" if ok else "0"
        etree.SubElement(rc_all, "setvar", action="Add").text = str(self.points)
        etree.SubElement(rc_all, "displayfeedback", feedbacktype="Response", linkrefid="response_allcorrect")

        rc_not = etree.SubElement(resprocessing, "respcondition", **{"continue": "Yes"})
        cv_or = etree.SubElement(etree.SubElement(rc_not, "conditionvar"), "or")
        for idx, ok in enumerate(correct):
            not_elem = etree.SubElement(cv_or, "not")
            etree.SubElement(not_elem, "varequal", respident=str(idx)).text = "1" if ok else "0"
        etree.SubElement(rc_not, "setvar", action="Add").text = "0"
        etree.SubElement(rc_not, "displayfeedback", feedbacktype="Response", linkrefid="response_onenotcorrect")
        return resprocessing

    def _create_itemfeedback(self) -> list:
        # Same as MCQ, but as XHTML so LaTeX spans in the remarks render.
        feedbacks = []
        for idx, opt in enumerate(self.get_options()):
            itemfeedback = etree.Element("itemfeedback", ident=f"response_{idx}", view="All")
            material = etree.SubElement(etree.SubElement(itemfeedback, "flow_mat"), "material")
            etree.SubElement(material, "mattext", texttype="text/xhtml").text = f"<p>{opt.get('feedback', '')}</p>"
            feedbacks.append(itemfeedback)
        return feedbacks
