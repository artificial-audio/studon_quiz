# Copyright (c) 2026 Friedrich-Alexander-Universität Erlangen-Nürnberg
# SPDX-License-Identifier: MIT

import importlib.resources as pkg_resources
import pytest
from studon_quiz.questions.kprim_question import KprimQuestion
from studon_quiz.questions.question_bank import QuestionBank


def _question(scores, points=2.0, partial=True):
    q = KprimQuestion(points=points, partial_scoring=partial)
    q.set_title("t")
    q.set_problem_statement("<p>stem</p>")
    q.set_options([{"text": f"s{i}", "score": s, "feedback": f"r{i}"} for i, s in enumerate(scores)])
    q.set_summary("")
    q.set_feedback({})
    q.set_hint({})
    return q


def test_kprim_qti_matches_ilias_import():
    item = _question([1, -1, 1, 0]).to_qti_xml("id1")
    meta = {f.findtext("fieldlabel"): f.findtext("fieldentry") for f in item.iter("qtimetadatafield")}
    assert meta["QUESTIONTYPE"] == "KPRIM CHOICE QUESTION"
    assert meta["option_label_setting"] == "right_wrong"
    decvar = item.find(".//decvar")
    assert decvar.get("maxvalue") == "2.0" and float(decvar.get("minvalue")) > 0  # partial scoring on
    per_statement = [rc for rc in item.iter("respcondition") if rc.find("setvar") is None]
    assert [rc.find(".//varequal").text for rc in per_statement] == ["1", "0", "1", "0"]
    assert len(item.findall(".//response_label")) == 4


def test_kprim_partial_scoring_off():
    decvar = _question([1, 1, 0, 0], partial=False).to_qti_xml("id2").find(".//decvar")
    assert float(decvar.get("minvalue")) == 0


def test_kprim_needs_four_options(tmp_path):
    assert not _question([1, 0, 1]).is_valid()
    md = tmp_path / "k.md"
    md.write_text("type: kprim\n\n# T\nd\n\n## Quiz\n\nStem\n\n## Options\n\n"
                  + "".join(f"- s{i}\n\t- Score: 1\n\t- Remark: r\n\n" for i in range(3)))
    with pytest.raises(ValueError):
        QuestionBank().add_question(md)


def test_kprim_template_loads():
    bank = QuestionBank()
    n = len(bank.questions)
    bank.add_question(pkg_resources.files("studon_quiz") / "markdown_template/kprim.md")
    q = bank.questions[-1]
    assert len(bank.questions) == n + 1 and q.points == 2.0 and q.is_valid()
    bank.questions.pop()
