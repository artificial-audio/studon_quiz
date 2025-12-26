import importlib.resources as pkg_resources
from qticonverter.tools.markdown_reader import MarkdownReader
import pytest


def test_markdown_reader_creation():
    file = pkg_resources.files("qticonverter")/"markdown_template/mcq-sa.md"
    try:
        reader = MarkdownReader(str(file))
    except:
        pytest.fail("Object not created")
    
    file = pkg_resources.files("qticonverter")/"markdown_template/mcq-sa-unknown.md"
    with pytest.raises(Exception):
        reader = MarkdownReader(str(file))


def test_markdown_reader_get_attrs() -> None:
    file = pkg_resources.files("qticonverter")/"markdown_template/mcq-sa.md"
    reader = MarkdownReader(str(file))
    attr = reader.get_attrs()
    assert type(attr) == dict

def test_markdown_reader_get_headings() -> None:
    file = pkg_resources.files("qticonverter")/"markdown_template/mcq-sa.md"
    reader = MarkdownReader(str(file))
    attr = reader.get_headings(2)
    assert type(attr) == list

def test_markdown_reader_get_description() -> None:
    file = pkg_resources.files("qticonverter")/"markdown_template/mcq-sa.md"
    reader = MarkdownReader(str(file))
    description = reader.get_description(2, 1)
    assert type(description) == str

def test_markdown_reader_get_question_type() -> None:
    file = pkg_resources.files("qticonverter")/"markdown_template/mcq-sa.md"
    reader = MarkdownReader(str(file))
    q_type = reader.get_q_type()
    assert q_type == 'mcq-sa'

def test_markdown_reader_get_title() -> None:
    file = pkg_resources.files("qticonverter")/"markdown_template/mcq-sa.md"
    reader = MarkdownReader(str(file))
    title = reader.get_title()
    assert title == 'Matrix–Vector Multiplication'

def test_markdown_reader_get_short_description() -> None:
    file = pkg_resources.files("qticonverter")/"markdown_template/mcq-sa.md"
    reader = MarkdownReader(str(file))
    summary = reader.get_summary()
    assert type(summary) == str


def test_markdown_reader_get_problem_statement() -> None:
    file = pkg_resources.files("qticonverter")/"markdown_template/mcq-sa.md"
    reader = MarkdownReader(str(file))
    statement = reader.get_problem_statement()
    assert type(statement) == str

def test_markdown_reader_get_options() -> None:
    file = pkg_resources.files("qticonverter")/"markdown_template/mcq-sa.md"
    reader = MarkdownReader(str(file))
    statement = reader.get_options()
    assert type(statement) == list

def test_markdown_reader_get_feedback() -> None:
    file = pkg_resources.files("qticonverter")/"markdown_template/mcq-sa.md"
    reader = MarkdownReader(str(file))
    statement = reader._get_feedback()
    assert type(statement) == list