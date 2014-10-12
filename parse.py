#!/usr/bin/env

__author__ = 'amirali'

import sys
import os
from mongoengine import connect
from QuizObjects import *


def process_quiz(quiz_file, DB, quiz_name):
    """Add the lines read from file to the DB"""
    data = open(quiz_file)
    if data is None:
        return
    line = data.readline()
    q_number = 1
    while line:
        while line.startswith('#'):
            line = data.readline()
        if line.upper().startswith('Q)'):
            question = QuizQuestion(question_number=q_number, question=line[2:].strip(), quiz_name=quiz_name)
            q_number += 1
            line = data.readline()
            choices = []
            while line.upper().startswith('C') or line.upper().startswith('ANS'):
                if line.upper().startswith('C'):
                    choices.append(Choice(text=line[3:].strip(), is_answer=False))
                else:
                    choices.append(Choice(text=line[4:].strip(), is_answer=True))
                line = data.readline()
                if line.upper().startswith('FEED'):
                    choices[-1].feedback = line[5:].strip()
                    line = data.readline()
            question.choices = choices
            add_to_db(question, DB)
        else:
            line = data.readline()
    data.close()


def add_to_db(question, DB):
    with connect(DB):
        question.save()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: Parse.py QUIZFILE QUIZNAME"
    elif os.path.exists(sys.argv[1]):
        #find out the quiz number and automatically increase it.
        _quiz_no = 1
        if os.path.exists('_quiz_no'):
            with open('_quiz_no', 'r') as f:
                l = f.readline()
                if l:
                    _quiz_no = int(l)

        process_quiz(sys.argv[1], 'quiz'+str(_quiz_no), sys.argv[2])

        _quiz_no += 1
        with open('_quiz_no', 'w') as f:
            f.write(str(_quiz_no))

    else:
        print "Quiz File Does Not Exist"