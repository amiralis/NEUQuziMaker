__author__ = 'amirali'

"""
Defines the "schema" for UserStat Objects.
"""

import datetime
from mongoengine import StringField, IntField, ListField, BooleanField, Document


# "schema" definition
class UserAttempt(Document):
    """
    defines UserStat objects as specified in the header
    """
    username = StringField(required=True)
    attempted_at = StringField(default=str(datetime.datetime.now()), required=True)
    question_number = IntField(required=True)
    quiz = StringField(required=True)
    choices = ListField(IntField(required=True))
    is_correct = BooleanField(required=True)

    def __str__(self):
        if self.is_correct:
            answer = 'correctly'
        else:
            answer = 'incorrectly'

        return "User: %s @ %s answered quiz:%s question:%d %s with %s " % (self.username, self.attempted_at, self.quiz,
                                                                           self.question_number, answer, self.choices)

