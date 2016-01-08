#!/usr/bin/python
import flask
import json
import sqlite3
import re
import random
import Queue
import threading
import string
import os
import hashlib

SQLITE_FILE = "skill_tester.db"

app = flask.Flask(__name__)

class AuthError(BaseException):
    pass

class ValidationError(BaseException):
    pass

def get_post_param(param, default="", mandatory=False):
    res = default
    if param in flask.request.form:
        if mandatory and param.strip() == "":
            raise ValidationError('Parameter "%s" must not be empty' % param)
        res = flask.request.form[param]
    elif mandatory:
        raise ValidationError('Parameter "%s" is mandatory' % param)
    return res

class DBConsumer:
    def __init__(self, filename):
        self.filename = filename
        self.looping = False
        self.queue = Queue.Queue()
        self.thread = threading.Thread(None, self.__loop)
        self.thread.start()
        self.result = None
        self.success = False

    def __loop(self):
        self.db = sqlite3.connect(SQLITE_FILE)
        self.db.row_factory = sqlite3.Row
        self.cur = self.db.cursor()
        self.cur.execute("PRAGMA foreign_keys = ON")
        try:
            self.looping = True
            while self.looping:
                try:
                    req, params, commit, evt1, evt2 = self.queue.get(True, 0.1)
                    try:
                        if params:
                            self.cur.execute(req, params)
                        else:
                            self.cur.execute(req)
                        if commit:
                            self.db.commit()
                        self.result = self.cur.fetchall()
                        self.success = True
                    except BaseException as ex:
                        self.success = False
                        self.result = ex
                    evt1.set()
                    evt2.wait(0.1)
                except Queue.Empty:
                    pass
        finally:
            self.db.close()

    def close(self):
        self.looping = False
        self.thread.join(5)

    def query(self, req, params=None, commit=False):
        evt1 = threading.Event()
        evt2 = threading.Event()
        res = self.queue.put_nowait((req, params, commit, evt1, evt2))
        evt1.wait()
        res = self.result
        success = self.success
        evt2.set()
        if not success:
            raise self.result
        return res

    def execute(self, req, params=None):
        self.query(req, params, True)

    instance = None
    @staticmethod
    def get_instance():
        if not DBConsumer.instance:
            DBConsumer.instance = DBConsumer(SQLITE_FILE)
        return DBConsumer.instance


####################### ADMIN ##################################################
def test_logged():
    if "is_admin" not in flask.session:
        raise AuthError("You are not logged")

@app.route("/admin/is_logged")
def www_is_logged():
    res = False
    try:
        test_logged()
        res = True
    except AuthError:
        pass
    return json.dumps(res)

@app.route("/admin/get_users")
def www_get_users():
    res = []
    try:
        test_logged()
        req = "SELECT id, login FROM users;"
        for user_id, login in DBConsumer.get_instance().query(req):
            res.append({"id" : user_id, "login" : login})
    except AuthError as ex:
        flask.abort(flask.make_response(str(ex), 403))
    except ValidationError as ex:
        flask.abort(flask.make_response(str(ex), 400))
    return json.dumps(res)

@app.route("/admin/delete_user", methods=["POST"])
def www_delete_user():
    res = False
    try:
        test_logged()
        user_id = int(get_post_param("id", mandatory=True))
        req = "DELETE FROM users WHERE id = ?;"
        DBConsumer.get_instance().execute(req, (user_id,))
        res = True
    except AuthError as ex:
        flask.abort(flask.make_response(str(ex), 403))
    except ValidationError as ex:
        flask.abort(flask.make_response(str(ex), 400))
    return json.dumps(res)

@app.route("/admin/create_user", methods=["POST"])
def www_create_user():
    res = False
    try:
        test_logged()
        login = get_post_param("login", mandatory=True)
        password = get_post_param("password", mandatory=True)
        password = get_password(password)
        req = "INSERT INTO users (login, password) VALUES (?, ?);"
        DBConsumer.get_instance().execute(req, (login, password))
        res = True
    except AuthError as ex:
        flask.abort(flask.make_response(str(ex), 403))
    except ValidationError as ex:
        flask.abort(flask.make_response(str(ex), 400))
    return json.dumps(res)

@app.route("/admin/logout")
def www_logout():
    flask.session.pop("is_admin", None)
    res = True
    return json.dumps(res)

@app.route("/admin/login", methods=["POST"])
def www_login():
    res = False
    try:
        login = get_post_param("login", mandatory=True)
        password = get_post_param("password", mandatory=True)
        password = get_password(password)
        req = "SELECT password FROM users WHERE login = ?"
        row = DBConsumer.get_instance().query(req, (login,))
        if not row:
            raise AuthError("Erreur d'authentification")
        if row[0]['password'] != password:
            raise AuthError("Erreur d'authentification.")
        flask.session["is_admin"] = login
        res = True
    except AuthError as ex:
        flask.abort(flask.make_response(str(ex), 403))
    except ValidationError as ex:
        flask.abort(flask.make_response(str(ex), 400))
    return json.dumps(res)

@app.route("/admin/get_languages")
def www_get_languages():
    res = []
    try:
        test_logged()
        req = "SELECT language FROM question GROUP BY language"
        for row in DBConsumer.get_instance().query(req):
            res.append(row["language"])
    except AuthError as ex:
        flask.abort(flask.make_response(str(ex), 403))
    return json.dumps(res)

@app.route("/admin/get_questions")
def www_get_questions():
    res = []
    try:
        test_logged()
        req = "SELECT id, name, language, qtype as 'type' FROM question"
        for row in DBConsumer.get_instance().query(req):
            res.append(dict(zip(row.keys(), row)))
    except AuthError as ex:
        flask.abort(flask.make_response(str(ex), 403))
    return json.dumps(res)

@app.route("/admin/get_questions_filter", methods=["POST"])
def www_get_questions_filter():
    res = []
    try:
        test_logged()
        try:
            filters = json.loads(get_post_param("filters", mandatory=True))
        except ValueError:
            raise ValidationError("Wrong JSON for filters")
        language = get_post_param("language", mandatory=True)

        req = "SELECT id, name, language, qtype as 'type' FROM question WHERE qtype = ?  AND language = ?ORDER BY RANDOM() LIMIT ?"
        for qtype, nb in filters.iteritems():
            nb = int(nb)
            for row in DBConsumer.get_instance().query(req, (qtype, language, nb)):
                res.append(dict(zip(row.keys(), row)))
        random.shuffle(res)
    except ValidationError as ex:
        flask.abort(flask.make_response(str(ex), 400))
    except AuthError as ex:
        flask.abort(flask.make_response(str(ex), 403))
    return json.dumps(res)

@app.route("/admin/delete_question", methods=["POST"])
def www_delete_question():
    res = False
    try:
        test_logged()
        id = int(get_post_param("id", mandatory=True))
        req = "DELETE FROM question WHERE id = ?"
        DBConsumer.get_instance().execute(req, (id,))
        res = True
    except ValidationError as ex:
        flask.abort(flask.make_response(str(ex), 400))
    except AuthError as ex:
        flask.abort(flask.make_response(str(ex), 403))
    return str(res)

@app.route("/admin/get_question", methods=["POST"])
def www_get_question():
    res = None
    try:
        test_logged()
        id = int(get_post_param("id", mandatory=True))
        req = "SELECT id, name, language, text, qtype as 'type', answers, options FROM question WHERE id = ? LIMIT 1"
        row = DBConsumer.get_instance().query(req, (id,))
        if row is None:
            raise ValidationError("No question %s" % num)
        res = dict(zip(row[0].keys(), row[0]))
        res["answers"] = json.loads(res["answers"])
        res["options"] = json.loads(res["options"])
    except ValidationError as ex:
        flask.abort(flask.make_response(str(ex), 400))
    except AuthError as ex:
        flask.abort(flask.make_response(str(ex), 403))
    return json.dumps(res)

@app.route("/admin/edit_question", methods=["POST"])
def www_edit_question():
    res = ""
    try:
        test_logged()
        id = get_post_param("id", None)
        name = get_post_param("name", mandatory=True)
        language = get_post_param("language", mandatory=True)
        text = get_post_param("text", mandatory=True)
        type = get_post_param("type", mandatory=True)
        try:
            answers = json.dumps(json.loads(get_post_param("answers", mandatory=True)))
        except ValueError:
            raise ValidationError("Wrong JSON for answers")

        try:
            options = json.dumps(json.loads(get_post_param("options", mandatory=True)))
        except ValueError:
            raise ValidationError("Wrong JSON for options")

        if not id:
            req = "INSERT INTO question (name, language, text, qtype, answers, options) VALUES (?, ?, ?, ?, ?, ?)"
            DBConsumer.get_instance().execute(req, (name, language, text, type, answers, options))
        else:
            try:
                id = int(id)
            except ValueError:
                raise ValidationError("Wrong id")
            #TODO (maybe) test if the id exists in database. If not, nothing is modified, but the user will get a success
            #             in another hand, this should never occurs, and we do not want the let know to an attacker wich id exists or not...
            req = "UPDATE question SET name=?, language=?, text=?, qtype=?, answers=?, options=? WHERE id=?"
            DBConsumer.get_instance().execute(req, (name, language, text, type, answers, options, id))
        res = True

    except ValidationError as ex:
        flask.abort(flask.make_response(str(ex), 400))
    except AuthError as ex:
        flask.abort(flask.make_response(str(ex), 403))
    return str(res)

@app.route("/admin/get_tests")
def www_get_tests():
    res = []
    try:
        test_logged()
        req = """
                SELECT
                    id,
                    creation_date,
                    finished,
                    username,
                    (
                        SELECT COUNT(test_question.question_id)
                        FROM test_question
                        WHERE test_question.test_id = test.id
                    ) as 'nb_questions',
                    (SELECT COUNT(answer.id) FROM answer WHERE answer.test_id = test.id) as nb_answers,
                    (SELECT COUNT(answer.id) FROM answer WHERE answer.test_id = test.id AND answer.success = 1) as nb_success
                FROM test
            """
        for row in DBConsumer.get_instance().query(req):
            res.append(dict(zip(row.keys(), row)))
    except AuthError as ex:
        flask.abort(flask.make_response(str(ex), 403))
    return json.dumps(res)

@app.route("/admin/get_test", methods=["POST"])
def www_get_test():
    res = {}
    try:
        test_logged()
        id = int(get_post_param("id", mandatory=True))
        req = """
            SELECT
                test.username,
                test.finished,
                question.id as 'qid',
                question.name,
                question.language,
                question.qtype as 'type',
                answer.success,
                (SELECT COUNT(ans2.id) FROM answer ans2 WHERE ans2.question_id = question.id) as nb_answers,
                (SELECT COUNT(ans2.id) FROM answer ans2 WHERE ans2.question_id = question.id AND ans2.success = 1) as nb_success
            FROM test
            LEFT JOIN test_question ON test_question.test_id = test.id
            LEFT JOIN question ON question.id = test_question.question_id
            LEFT JOIN answer ON answer.test_id = test.id AND answer.question_id = question.id
            WHERE test.id = ?
            """
        res["id"] = id
        res["questions"] = []
        for row in DBConsumer.get_instance().query(req, (id,)):
            user, finished, qid, name, language, qtype, success, nb_answers, nb_success = row
            res["username"] = user
            res["finished"] = finished
            question = {}
            question["id"] = qid
            question["name"] = name
            question["language"] = language
            question["type"] = qtype
            question["success"] = success
            question["nb_answers"] = nb_answers
            question["nb_success"] = success
            res["questions"].append(question)
    except ValidationError as ex:
        flask.abort(flask.make_response(str(ex), 400))
    except AuthError as ex:
        flask.abort(flask.make_response(str(ex), 403))
    return json.dumps(res)

@app.route("/admin/delete_test", methods=["POST"])
def www_delete_test():
    res = False
    try:
        test_logged()
        id = int(get_post_param("id", mandatory=True))
        req = "DELETE FROM test WHERE id = ?"
        DBConsumer.get_instance().execute(req, (id,))
        res = True
    except ValidationError as ex:
        flask.abort(flask.make_response(str(ex), 400))
    except AuthError as ex:
        flask.abort(flask.make_response(str(ex), 403))
    return str(res)

@app.route("/admin/edit_test", methods=["POST"])
def www_edit_test():
    res = False
    try:
        test_logged()
        test_id = get_post_param("id", None)
        finished = int(get_post_param("finished", mandatory=True))
        user = get_post_param("user", mandatory=True)
        try:
            questions = json.loads(get_post_param("questions", mandatory=True))
        except ValueError:
            raise ValidationError("Wrong JSON for questions")

        if not test_id:
            req = "INSERT INTO test (username, creation_date) VALUES (?, DATETIME())"
            DBConsumer.get_instance().execute(req, (user, ))
            test_id = DBConsumer.get_instance().cur.lastrowid
        else:
            try:
                test_id = int(test_id)
            except ValueError:
                raise ValidationError("Wrong id")
            #TODO (maybe) test if the id exists in database. If not, nothing is modified, but the user will get a success
            #             in another hand, this should never occurs, and we do not want the let know to an attacker wich id exists or not...
            req = "UPDATE test SET username=?, finished=? WHERE id=?"
            DBConsumer.get_instance().execute(req, (user, finished, test_id))
            req = "DELETE FROM test_question WHERE test_id = ?"
            DBConsumer.get_instance().execute(req, (test_id, ))
        req = "INSERT INTO test_question (test_id, question_id, num) VALUES (?, ?, ?)"
        num = 1
        for qid in questions:
            try:
                DBConsumer.get_instance().execute(req, (test_id, qid, num))
                num += 1
            except sqlite3.IntegrityError:
                raise ValidationError("Question '%s' does not exists" % str(qid))
        res = True

    except ValidationError as ex:
        flask.abort(flask.make_response(str(ex), 400))
    except AuthError as ex:
        flask.abort(flask.make_response(str(ex), 403))
    return str(res)
###############################################################################

####################### USER ##################################################
@app.route("/finish")
def www_finish():
    res = False
    try:
        if "test_id" not in flask.session:
            raise AuthError("You are not doing a test")
        test_id = flask.session["test_id"]

        req = "UPDATE test SET finished = 1 WHERE id = ?"
        DBConsumer.get_instance().execute(req, (test_id,))
        flask.session.pop('test_id', None)
        res = True
    except AuthError as ex:
        flask.abort(flask.make_response(str(ex), 403))
    return json.dumps(res)

@app.route("/ask_question", methods=["POST"])
def www_ask_question():
    res = None
    try:
        if "test_id" not in flask.session:
            raise AuthError("You are not doing a test")
        test_id = flask.session["test_id"]

        num = int(get_post_param("num", mandatory=True))
        req = """
                SELECT
                    tq.num,
                    q.text,
                    q.qtype as 'type',
                    q.options,
                    q.language,
                    (SELECT COUNT(num) FROM test_question tq2 WHERE tq2.test_id = t.id) as 'total',
                    answer.text as 'last_answer'
                FROM test t
                LEFT JOIN test_question tq ON tq.test_id = t.id
                LEFT JOIN question q ON q.id = tq.question_id
                LEFT JOIN answer ON answer.question_id = q.id AND answer.test_id = t.id
                WHERE t.id = ?
                LIMIT ?,1
            """
        row = DBConsumer.get_instance().query(req, (test_id, num - 1,))[0]
        if row is None:
            raise ValidationError("No question %s" % num)
        res = dict(zip(row.keys(), row))

        res["options"] = json.loads(res["options"]);
        res["done"] = []
        req = """
                SELECT num
                FROM test_question tq
                INNER JOIN answer ON tq.test_id = answer.test_id AND tq.question_id = answer.question_id
                WHERE tq.test_id = ?
             """
        for row in DBConsumer.get_instance().query(req, (test_id,)):
            res["done"].append(row[0])
    except ValidationError as ex:
        flask.abort(flask.make_response(str(ex), 400))
    except AuthError as ex:
        flask.abort(flask.make_response(str(ex), 403))
    return json.dumps(res)

@app.route("/get_available_tests")
def www_get_available_tests():
    res = []
    req = "SELECT username FROM test WHERE finished = 0 ORDER BY creation_date DESC"
    for row in DBConsumer.get_instance().query(req):
        res.append(row[0])
    return json.dumps(res)

@app.route("/select_test", methods=["POST"])
def www_select_test():
    res = False
    try:
        username = get_post_param("username", mandatory=True)
        req = "SELECT id FROM test WHERE username = ?"
        row = DBConsumer.get_instance().query(req, (username,))
        if not row:
            raise AuthError("You have not selected valid test")
        flask.session["test_id"] = row[0]["id"]
        res = True
    except AuthError as ex:
        flask.abort(flask.make_response(str(ex), 403))
    except ValidationError as ex:
        flask.abort(flask.make_response(str(ex), 400))
    return json.dumps(res)

@app.route("/answer", methods=["POST"])
def www_answer():
    res = False
    try:
        if "test_id" not in flask.session:
            raise AuthError("You are not doing a test")
        test_id = flask.session["test_id"]

        num = int(get_post_param("num", mandatory=True))
        answer = get_post_param("answer", mandatory=True)
        #check success
        req = """
                SELECT answers, question_id
                FROM test_question
                INNER JOIN question ON question.id = test_question.question_id
                WHERE
                    test_id = ?
                    AND
                    num = ?
                LIMIT 1
            """
        row = DBConsumer.get_instance().query(req, (test_id, num))
        if not row:
            raise AuthError("You have not answered to a valid question")
        answers = json.loads(row[0]["answers"])
        qid = row[0]["question_id"]
        success = 0
        if answer in answers:
            success = 1

        #remove existing answers (maybe we want to keep them as history, but someone could bruteforce the db and make it full)
        req = "DELETE FROM answer WHERE question_id = ? AND test_id = ?"
        DBConsumer.get_instance().execute(req, (qid, test_id,))

        req = """INSERT INTO answer (
                    datetime,
                    text,
                    success,
                    question_id,
                    test_id
                ) VALUES (
                    DATETIME(),
                    ?,
                    ?,
                    ?,
                    ?
                )
            """
        DBConsumer.get_instance().execute(req, (answer, success, qid, test_id,))
        res = True
    except AuthError as ex:
        flask.abort(flask.make_response(str(ex), 403))
    return json.dumps(res)

###############################################################################

def get_password(raw_password):
    #TODO improve security of the password encryption
    return hashlib.sha1(raw_password).hexdigest()

def generate_random_secret(length):
    """
    Generate a random secret key to use with session.

    WARNING : maybe it is not strong enought, if you want to improv it your welcome !
    @param length the secret length
    @return (String) a secret key
    """
    chars = string.printable
    random.seed = (os.urandom(1024))
    return ''.join(random.choice(chars) for i in xrange(length))

if __name__ == "__main__":
    DBConsumer.get_instance()
    try:
        # set the secret key.  keep this really secret:
        app.secret_key = generate_random_secret(1024)

        #TODO improve port (conf file ?)
        app.debug = True
        app.run(port=5123)
    finally:
        DBConsumer.get_instance().close()
