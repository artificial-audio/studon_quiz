import pytest
from qticonverter.questions.mcq_sa_question import McqSAQuestion  # replace with the actual module name

def test_initial_state():
    q = McqSAQuestion()
    
    # Check type is correctly set
    assert q.get_type() == "mcq-sa"
    
    # Mandatory fields are None initially except 'type'
    assert q.get_title() is None
    assert q.get_problem_statement() is None
    assert q.get_options() is None
    
    # Optional fields are None initially
    assert q.get_summary() is None
    assert q.get_feedback() is None
    assert q.get_hint() is None
    
    # isValid should be False initially (mandatory fields not set)
    assert not q.isValid()

def test_setters_and_getters():
    q = McqSAQuestion()
    
    # Set mandatory fields
    q.set_title("Matrix–Vector Multiplication")
    q.set_problem_statement("What is the result of y = Ax where A^2 is constant?")
    q.set_options(["0", "A linear transformation of x", "x^2", "A constant scalar"])
    
    # Set optional fields
    q.set_summary("Short description. Not displayed in presentation")
    q.set_feedback("Feedback for incorrect answer")
    q.set_hint("This is the hint to the question")
    
    # Test getters
    assert q.get_title() == "Matrix–Vector Multiplication"
    assert q.get_problem_statement() == "What is the result of y = Ax where A^2 is constant?"
    assert q.get_options() == ["0", "A linear transformation of x", "x^2", "A constant scalar"]
    assert q.get_summary() == "Short description. Not displayed in presentation"
    assert q.get_feedback() == "Feedback for incorrect answer"
    assert q.get_hint() == "This is the hint to the question"
    
    # Now isValid should be True
    assert q.isValid()

def test_get_field_names():
    q = McqSAQuestion()
    field_names = q.get_field_names()
    
    expected_fields = [
        'type', 'title', 'options', 'problem_statement',
        'summary', 'feedback', 'hint'
    ]
    
    assert set(field_names) == set(expected_fields)
