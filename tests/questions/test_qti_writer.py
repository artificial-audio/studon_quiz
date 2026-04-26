# Copyright (c) 2026 Friedrich-Alexander-Universität Erlangen-Nürnberg
# SPDX-License-Identifier: MIT

import pytest
from lxml import etree
from qticonverter.questions.mcq_sa_question import McqSAQuestion  # replace with actual path
from qticonverter.questions.qti_writer import QTIWriter  # replace with actual path
import os

def create_sample_question():
    q = McqSAQuestion()
    q.set_title("Matrix–Vector Multiplication")
    q.set_problem_statement("Which of the following statements about matrix vector multiplication are correct?")
    q.set_options([
        {"text": "The result is always a scalar", "score": 1, "feedback": "Correct!"},
        {"text": "It requires x to have dimensions compatible with A", "score": 0, "feedback": "Incorrect."},
        {"text": "The output dimension depends on the number of rows in A", "score": 0, "feedback": "Incorrect."},
        {"text": "This is the third correct option", "score": 1, "feedback": "Also correct"}
    ])
    q.set_feedback("General feedback")
    return q

def test_qti_writer_creates_xml(tmp_path):
    q = create_sample_question()
    writer = QTIWriter([q])
    
    output_file = tmp_path / "test_qti.xml"
    writer.write_qti(str(output_file))
    
    # Check file was created
    assert output_file.exists()
    
    # Parse XML
    tree = etree.parse(str(output_file))
    root = tree.getroot()
    
    # Root tag should be questestinterop
    assert root.tag == "questestinterop"
    
    # There should be one item
    items = root.findall("item")
    assert len(items) == 1
    
    item = items[0]
    
    # Check item attributes
    assert item.get("title") == q.get_title()
    assert item.get("maxattempts") == "0"
    
    # Check presentation exists and contains question text
    presentation = item.find("presentation")
    assert presentation is not None
    mattext = presentation.find(".//mattext")
    assert mattext is not None
    assert q.get_problem_statement() in mattext.text
    
    # Check response labels (options)
    response_labels = presentation.findall(".//response_label")
    assert len(response_labels) == len(q.get_options())
    
    # Check that image option has matimage
    image_option = q.get_options()[3]
    if "image" in image_option:
        matimage = presentation.find(".//matimage")
        assert matimage is not None
        assert matimage.get("uri") == image_option["image"]
    
    # Check resprocessing has correct number of respcondition
    # Should have one for each option plus two for overall feedback (response_allcorrect and response_onenotcorrect)
    resprocessing = item.find("resprocessing")
    respconditions = resprocessing.findall("respcondition")
    assert len(respconditions) == len(q.get_options()) + 2  # +2 for overall feedback respconditions
    
    # Check itemfeedback exists for each option plus two overall feedback elements
    itemfeedbacks = item.findall("itemfeedback")
    assert len(itemfeedbacks) == len(q.get_options()) + 2  # +2 for overall feedback elements
    
    # Optionally, check XML can be serialized
    xml_str = etree.tostring(root, encoding="UTF-8", pretty_print=True).decode()
    assert "<questestinterop>" in xml_str
