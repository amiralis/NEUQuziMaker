__author__ = 'amirali'

from flask import Flask, jsonify, render_template, request, redirect, url_for
import QuizObjects
import UserStatObjects
from pymongo import Connection
from mongoengine import context_managers, register_connection
import os

app = Flask(__name__)
app.secret_key = os.urandom(128)

## SHOULD DISABLE DEBUG FEATURE BEFORE DEPLOYMENT
app.debug = False


#Helper functions
def __check_db_exists(quiz_no):
    connection = Connection()
    if not quiz_no.startswith('quiz'):
        return False

    return quiz_no in connection.database_names()

def numeric_compare(x ,y):
	return int(x[4:])- int(y[4:])

def __get_quiz_list():
    quiz_list = []
    for db in Connection().database_names():
        if db.startswith('quiz'):
            quiz_list.append(db)
    return sorted(quiz_list, cmp=numeric_compare)


def setupDBs():
    register_connection('default', 'users_attempt_stat')
    for _q in __get_quiz_list():
        register_connection(_q, _q)


def parseArgs(params):
    try:
        paramsList = params.split('&')
        parsedParams = dict()
        parsedParams['quiz_no'] = int(paramsList[0][2:])
        parsedParams['question_no'] = int(paramsList[1][2:])
        return parsedParams
    except Exception:
        return None


def logUserAnswers(username, question_number, quiz_number, choices, is_correct):
    setupDBs()
    with context_managers.switch_db(UserStatObjects.UserAttempt, 'default') as UserAttempt:
        UserAttempt(username=username, question_number=question_number, quiz=quiz_number,
                    choices=choices, is_correct=is_correct).save()


def getFromDB(db, question_number=None):
    setupDBs()
    with context_managers.switch_db(QuizObjects.QuizQuestion, db) as QuizQuestion:
        if question_number is None:
            return QuizQuestion.objects()
        return QuizQuestion.objects(question_number=question_number)


################## Setting UP the DB
setupDBs()
#####################################

#Routing methods, for html urls
@app.route('/_validate')
def validate():
    """Validates the input from the user. need the quiz number, question number.
    If the answer is correct it renders the quiz page otherwise it returns the feedback"""

    quiz_no = request.args.get('quiz_no', 'Default', type=str)
    if not __check_db_exists('quiz' + quiz_no):
        return jsonify(result='WRONG QUIZ')

    question_number = int(request.args.get('question_number', 'Default', type=str))

    quiz_question = getFromDB('quiz'+quiz_no, question_number)[0]

    choices_feedback = []
    answers_indices = []
    answer_index = 1

    for choice in quiz_question.choices:
        choices_feedback.append(choice.feedback)
        if choice.is_answer:
            answers_indices.append(answer_index)
        answer_index += 1

    user_answers = []
    for i in range(len(choices_feedback)):
        user_answers.append(request.args.get('c' + str(i + 1), 'Default', type=str))

    is_correct = False
    user_answers_indices = []
    _index = 1
    for _answer in user_answers:
        if _answer == 'true':
            user_answers_indices.append(_index)
        _index += 1

    #user chose all the right answers, no more no less; no to add process and load next question
    if user_answers_indices == answers_indices:
        is_correct = True
        n = question_number + 1

    #user didn't choose everything right, returns feed back of all chosen items
    wrong_answer_feedback = ""
    _index = 1
    for __feedback in choices_feedback:
        if __feedback and _index in user_answers_indices:
            wrong_answer_feedback += __feedback + '\n'
        _index += 1

    if wrong_answer_feedback == "":
        wrong_answer_feedback = "Try Again"

    logUserAnswers(request.environ['SSL_CLIENT_S_DN_CN'], question_number, 'quiz'+quiz_no,
                   user_answers_indices, is_correct)

    if is_correct:
        return jsonify(result=url_for('test', params='')+("q=%s&n=%s" % (quiz_no, n)))
    return jsonify(result=wrong_answer_feedback)


@app.route('/test/<params>')
def test(params):
    parsedParams = parseArgs(params)
    if parsedParams is None:
        return render_template('quiz_error.html', error='wrong quiz')

    quiz_no = parsedParams['quiz_no']
    question_no = parsedParams['question_no']

    quiz_no = 'quiz' + str(quiz_no)

    if not __check_db_exists(quiz_no):
        return render_template('quiz_error.html', error='Wrong Quiz')

    _quiz_question = getFromDB(quiz_no, question_no)

    #check if there is any record back from database, if not it checks if we reached the total number of questions.
    # If so it will return the quiz_finished page, otherwise returns the quiz_error page.
    #If there is a record in the database, renders the quiz page.
    if len(_quiz_question) == 0 and question_no == (len(getFromDB(quiz_no)) + 1):
        return render_template('quiz_finished.html')
    elif len(_quiz_question) == 0:
        return render_template('quiz_error.html', error='wrong question number')

    quiz_question = getFromDB(quiz_no, question_no)[0]
    question = quiz_question.question
    choices = []
    for choice in quiz_question.choices:
        choices.append(choice.text)
    return render_template('quiz.html', choices=choices, question=question,
                           quiz_number=int(quiz_no[4:]), question_number=question_no, quiz_name=quiz_question.quiz_name)


# helper ADT to store information about a quiz and its location
class _quiz():
    def __init__(self, quiz_name, quiz_location):
        self.quiz_name = quiz_name
        self.quiz_location = quiz_location


@app.route('/<quiz_no>/')
def quiz(quiz_no):
    """ Entry point to start the quiz. if renders the test page with quiz number and question number 1."""

    return redirect(url_for('test', params="q=%s&n=1" % quiz_no[4:]))


@app.route('/')
def index():
    quizzes = []
    for _q in __get_quiz_list():
        quizzes.append(_quiz(getFromDB(_q)[0]['quiz_name'], url_for('index')+_q))
    return render_template('quizzes.html', quizzes=quizzes)


if __name__ == '__main__':
    app.run()