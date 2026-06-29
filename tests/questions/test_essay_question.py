# Copyright (c) 2026 Friedrich-Alexander-Universität Erlangen-Nürnberg
# SPDX-License-Identifier: MIT

import pytest
from lxml import etree
from studon_quiz.questions.essay_question import EssayQuestion


def test_initial_state():
    q = EssayQuestion()

    assert q.get_type() == "essay"
    assert q.get_title() is None
    assert q.get_problem_statement() is None
    assert q.get_correct_answer() is None

    assert q.get_summary() is None
    assert q.get_feedback() is None
    assert q.get_hint() is None
    assert q.get_options() is None

    assert not q.isValid()


def test_setters_and_getters():
    q = EssayQuestion()

    q.set_title("Essay Question")
    q.set_problem_statement("Write an essay on the topic")
    q.set_correct_answer("Expected answer text")
    q.set_maxchars(1000)

    q.set_summary("Short description")
    q.set_feedback({"Correct": "Well done", "Wrong": "Try again"})
    q.set_hint({"hint": "Check the guidelines", "penalty": 1})

    assert q.get_title() == "Essay Question"
    assert q.get_problem_statement() == "Write an essay on the topic"
    assert q.get_correct_answer() == "Expected answer text"
    assert q.get_maxchars() == 1000
    assert q.get_summary() == "Short description"
    assert q.get_feedback() == {"Correct": "Well done", "Wrong": "Try again"}
    assert q.get_hint() == {"hint": "Check the guidelines", "penalty": 1}

    assert q.isValid()


def test_get_field_names():
    q = EssayQuestion()
    field_names = q.get_field_names()

    expected = [
        'type', 'title', 'problem_statement', 'correct_answer',
        'summary', 'feedback', 'hint', 'maxchars', 'maxpoints'
    ]
    assert set(field_names) == set(expected)


def test_isValid_missing_mandatory():
    q = EssayQuestion()
    q.set_title("Test")
    q.set_problem_statement("What is something?")
    # correct_answer still None
    assert not q.isValid()

    q.set_correct_answer("Answer")
    assert q.isValid()


def test_default_maxchars():
    q = EssayQuestion()
    assert q.get_maxchars() == 500


def _make_question(**kwargs) -> EssayQuestion:
    """Helper to create a fully populated EssayQuestion."""
    q = EssayQuestion()
    q.set_title(kwargs.get("title", "Test Essay"))
    q.set_problem_statement(kwargs.get("problem_statement", "Write about the topic"))
    q.set_correct_answer(kwargs.get("correct_answer", "Model answer"))
    q.set_maxchars(kwargs.get("maxchars", 500))
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
    assert item.get("title") == "Test Essay"
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
    assert fields["QUESTIONTYPE"] == "TEXT QUESTION"
    assert fields["AUTHOR"] == "TestAuthor"
    assert fields["additional_cont_edit_mode"] == "default"
    assert fields["externalId"] == "q_0"
    assert fields["ilias_lifecycle"] == "draft"
    assert fields["lifecycle"] == "draft"
    
    # TEXT QUESTION specific fields
    assert fields["wordcounter"] == "0"
    assert fields["textrating"] == "ci"
    assert fields["matchcondition"] == "0"
    assert fields["termscoring"] == "YTowOnt9"
    assert fields["termrelation"] == "non"
    assert fields["specificfeedback"] == "non"


def test_to_qti_xml_presentation():
    q = _make_question(maxchars=1000)
    item = q.to_qti_xml("q_0")

    presentation = item.find("presentation")
    assert presentation.get("label") == "Test Essay"

    mattext = presentation.find(".//mattext")
    assert mattext.get("texttype") == "text/xhtml"
    assert "<p>Write about the topic</p>" in mattext.text

    response_str = presentation.find(".//response_str")
    assert response_str.get("ident") == "TEXT"
    assert response_str.get("rcardinality") == "Ordered"

    render_fib = response_str.find("render_fib")
    assert render_fib.get("fibtype") == "String"
    assert render_fib.get("maxchars") == "1000"
    # ILIAS human-rated essay format
    assert render_fib.get("prompt") == "Box"
    
    # Must have response_label child element
    response_label = render_fib.find("response_label")
    assert response_label is not None
    assert response_label.get("ident") == "A"


def test_to_qti_xml_feedback():
    q = _make_question(feedback={"Correct": "Great job", "Wrong": "Review notes"})
    item = q.to_qti_xml("q_0")

    feedbacks = item.findall("itemfeedback")
    # Should have 2 feedback items (no separate "Correct" item)
    assert len(feedbacks) == 2

    fb_map = {fb.get("ident"): fb for fb in feedbacks}

    # Detailed feedback
    assert "<p>Great job</p>" in fb_map["response_allcorrect"].find(".//mattext").text
    assert "<p>Review notes</p>" in fb_map["response_onenotcorrect"].find(".//mattext").text


def test_to_qti_xml_feedback_no_data():
    q = _make_question()
    item = q.to_qti_xml("q_0")

    feedbacks = item.findall("itemfeedback")
    # Should have 2 feedback items (even if empty)
    assert len(feedbacks) == 2


def test_to_qti_xml_hint():
    q = _make_question(hint={"hint": "Follow the guidelines", "penalty": 2})
    item = q.to_qti_xml("q_0")

    hint = item.find("solutionhint")
    assert hint is not None
    assert hint.get("index") == "1"
    assert hint.get("points") == "2"
    # Hint content should be HTML-escaped text, not child elements
    assert hint.text == "&lt;p&gt;Follow the guidelines&lt;/p&gt;"


def test_to_qti_xml_no_hint():
    q = _make_question()
    item = q.to_qti_xml("q_0")

    assert item.find("solutionhint") is None


def test_to_qti_xml_resprocessing():
    q = _make_question(correct_answer="expected response")
    item = q.to_qti_xml("q_0")

    resprocessing = item.find("resprocessing")
    assert resprocessing is not None
    # ILIAS text questions use HumanRater scoremodel
    assert resprocessing.get("scoremodel") == "HumanRater"

    outcomes = resprocessing.find("outcomes")
    assert outcomes is not None
    decvar = outcomes.find("decvar")
    assert decvar is not None
    assert decvar.get("varname") == "WritingScore"
    assert decvar.get("vartype") == "Integer"
    assert decvar.get("minvalue") == "0"
    assert decvar.get("maxvalue") == "10"

    # Check response conditions (should check "points" not "TEXT")
    respconditions = resprocessing.findall("respcondition")
    assert len(respconditions) >= 2
    
    # First condition: points == 10
    varequals = respconditions[0].findall(".//varequal")
    assert len(varequals) > 0
    assert varequals[0].get("respident") == "points"
    assert varequals[0].text == "10"
    
    # Should have tutor_rated condition
    tutor_cond = None
    for rc in respconditions:
        other = rc.find(".//other")
        if other is not None and other.text == "tutor_rated":
            tutor_cond = rc
            break
    assert tutor_cond is not None
