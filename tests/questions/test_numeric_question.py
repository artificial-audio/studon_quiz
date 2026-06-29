# Copyright (c) 2026 Friedrich-Alexander-Universität Erlangen-Nürnberg
# SPDX-License-Identifier: MIT

import pytest
from lxml import etree
from studon_quiz.questions.numeric_question import NumericQuestion


def test_initial_state():
    q = NumericQuestion()

    assert q.get_type() == "num"
    assert q.get_title() is None
    assert q.get_problem_statement() is None
    assert q.get_correct_answer() is None
    assert q.get_points() is None

    assert q.get_summary() is None
    assert q.get_feedback() is None
    assert q.get_hint() is None
    assert q.get_options() is None

    assert not q.isValid()


def test_setters_and_getters():
    q = NumericQuestion()

    q.set_title("Resistance Calculation")
    q.set_problem_statement("Calculate the total resistance in ohms")
    q.set_correct_answer(12.01)
    q.set_points(3)
    q.set_tolerance(0.01)
    q.set_maxchars(8)
    q.set_summary("Short description")
    q.set_feedback({"Correct": "Well done", "Wrong": "Try again"})
    q.set_hint({"hint": "Check Ohm's law", "penalty": 1})

    assert q.get_title() == "Resistance Calculation"
    assert q.get_problem_statement() == "Calculate the total resistance in ohms"
    assert q.get_correct_answer() == 12.01
    assert q.get_points() == 3.0
    assert q.get_tolerance() == 0.01
    assert q.get_maxchars() == 8
    assert q.get_summary() == "Short description"
    assert q.get_feedback() == {"Correct": "Well done", "Wrong": "Try again"}
    assert q.get_hint() == {"hint": "Check Ohm's law", "penalty": 1}

    assert q.isValid()


def test_get_field_names():
    q = NumericQuestion()
    field_names = q.get_field_names()

    expected = [
        'type', 'title', 'problem_statement', 'correct_answer', 'points',
        'summary', 'feedback', 'hint', 'tolerance', 'maxchars'
    ]
    assert set(field_names) == set(expected)


def test_isValid_missing_mandatory():
    q = NumericQuestion()
    q.set_title("Test")
    q.set_problem_statement("What is 2+2?")
    # correct_answer and points still None
    assert not q.isValid()

    q.set_correct_answer(4.0)
    assert not q.isValid()

    q.set_points(1)
    assert q.isValid()


def test_default_tolerance_and_maxchars():
    q = NumericQuestion()
    assert q.get_tolerance() == 0.0
    assert q.get_maxchars() == 10


def _make_question(**kwargs) -> NumericQuestion:
    """Helper to create a fully populated NumericQuestion."""
    q = NumericQuestion()
    q.set_title(kwargs.get("title", "Test Question"))
    q.set_problem_statement(kwargs.get("problem_statement", "What is 2+2?"))
    q.set_correct_answer(kwargs.get("correct_answer", 4.0))
    q.set_points(kwargs.get("points", 3))
    q.set_tolerance(kwargs.get("tolerance", 0.5))
    q.set_maxchars(kwargs.get("maxchars", 5))
    if "summary" in kwargs:
        q.set_summary(kwargs["summary"])
    if "feedback" in kwargs:
        q.set_feedback(kwargs["feedback"])
    if "hint" in kwargs:
        q.set_hint(kwargs["hint"])
    return q


def test_to_qti_xml_basic_structure():
    q = _make_question(summary="A description")
    item = q.to_qti_xml("q_0", author="TestAuthor", ilias_version="9.18.0")

    assert item.tag == "item"
    assert item.get("ident") == "q_0"
    assert item.get("title") == "Test Question"
    assert item.get("maxattempts") == "0"

    # qticomment
    assert item.find("qticomment").text == "A description"


def test_to_qti_xml_metadata():
    q = _make_question()
    item = q.to_qti_xml("q_0", author="TestAuthor", ilias_version="9.18.0")

    qtimetadata = item.find(".//qtimetadata")
    fields = {f.find("fieldlabel").text: f.find("fieldentry").text
              for f in qtimetadata.findall("qtimetadatafield")}

    assert fields["ILIAS_VERSION"] == "9.18.0"
    assert fields["QUESTIONTYPE"] == "NUMERIC QUESTION"
    assert fields["AUTHOR"] == "TestAuthor"
    assert fields["additional_cont_edit_mode"] == "default"
    assert fields["externalId"] == "q_0"
    assert fields["ilias_lifecycle"] == "draft"
    assert fields["lifecycle"] == "draft"


def test_to_qti_xml_presentation():
    q = _make_question(maxchars=7)
    item = q.to_qti_xml("q_0")

    presentation = item.find("presentation")
    assert presentation.get("label") == "Test Question"

    mattext = presentation.find(".//mattext")
    assert mattext.get("texttype") == "text/xhtml"
    assert "<p>What is 2+2?</p>" in mattext.text

    response_num = presentation.find(".//response_num")
    assert response_num.get("ident") == "NUM"
    assert response_num.get("rcardinality") == "Single"
    assert response_num.get("numtype") == "Decimal"

    render_fib = response_num.find("render_fib")
    assert render_fib.get("fibtype") == "Decimal"
    assert render_fib.get("maxchars") == "7"


def test_to_qti_xml_resprocessing_range():
    q = _make_question(correct_answer=10.0, tolerance=0.5, points=5)
    item = q.to_qti_xml("q_0")

    resprocessing = item.find("resprocessing")
    conditions = resprocessing.findall("respcondition")
    assert len(conditions) == 3

    # Condition 1: correct range → award points
    cv1 = conditions[0].find("conditionvar")
    assert cv1.find("vargte").text == "9.5"
    assert cv1.find("varlte").text == "10.5"
    assert conditions[0].find("setvar").text == "5.0"

    # Condition 2: correct range → allcorrect feedback
    assert conditions[1].get("continue") == "Yes"
    fb2 = conditions[1].find("displayfeedback")
    assert fb2.get("linkrefid") == "response_allcorrect"

    # Condition 3: NOT range → onenotcorrect feedback
    assert conditions[2].get("continue") == "Yes"
    not_el = conditions[2].find(".//not")
    assert not_el is not None
    fb3 = conditions[2].find("displayfeedback")
    assert fb3.get("linkrefid") == "response_onenotcorrect"


def test_to_qti_xml_feedback():
    q = _make_question(feedback={"Correct": "Great job", "Wrong": "Review notes"})
    item = q.to_qti_xml("q_0")

    feedbacks = item.findall("itemfeedback")
    assert len(feedbacks) == 3

    fb_map = {fb.get("ident"): fb for fb in feedbacks}

    # Empty "Correct" placeholder
    assert fb_map["Correct"].find(".//mattext").text is None

    # Detailed feedback
    assert "<p>Great job</p>" in fb_map["response_allcorrect"].find(".//mattext").text
    assert "<p>Review notes</p>" in fb_map["response_onenotcorrect"].find(".//mattext").text


def test_to_qti_xml_feedback_no_data():
    q = _make_question()
    item = q.to_qti_xml("q_0")

    feedbacks = item.findall("itemfeedback")
    assert len(feedbacks) == 3


def test_to_qti_xml_hint():
    q = _make_question(hint={"hint": "Use Ohm's law", "penalty": 2})
    item = q.to_qti_xml("q_0")

    hint = item.find("solutionhint")
    assert hint is not None
    assert hint.get("index") == "1"
    assert hint.get("points") == "2"
    assert hint.find("p").text == "Use Ohm's law"


def test_to_qti_xml_no_hint():
    q = _make_question()
    item = q.to_qti_xml("q_0")

    assert item.find("solutionhint") is None


def test_to_qti_xml_zero_tolerance():
    """When tolerance is 0, lower and upper bounds equal the answer."""
    q = _make_question(correct_answer=42.0, tolerance=0.0, points=1)
    item = q.to_qti_xml("q_0")

    cv = item.find(".//respcondition/conditionvar")
    assert cv.find("vargte").text == "42.0"
    assert cv.find("varlte").text == "42.0"
