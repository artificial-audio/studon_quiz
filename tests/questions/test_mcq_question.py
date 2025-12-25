from tests.questions.test_question import Question
from tests.questions.test_field import Field

class McqQuestion(Question):
    choices: Field
    pass