__author__ = 'amirali'

"""
Defines the "schema" for Quiz Objects, since we are using OEM (MonogoEngine) Question is a question of type string and
question number as int, both required, question number is unique Each question has a list of choices, but no required.
Each choice has a boolean is_answer and string text, which are required and a feedback filed which is optional.
"""

from mongoengine import EmbeddedDocument, StringField, Document, IntField, ListField, EmbeddedDocumentField, \
    BooleanField


# "schema" definition
class Choice(EmbeddedDocument):
    """
    defines choice objects as specified in the header
    """
    is_answer = BooleanField(required=True)
    text = StringField(required=True)
    feedback = StringField()


class QuizQuestion(Document):
    """
    defines question objects as specified in the header
    """
    quiz_name = StringField(required=True)
    question_number = IntField(unique=True)
    question = StringField(required=True)
    choices = ListField(EmbeddedDocumentField(Choice))

    def __str__(self):
        return "Q%d) %s" % (self.question_number, self.question)