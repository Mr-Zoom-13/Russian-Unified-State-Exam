import datetime
import random
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask import Flask, render_template, redirect, session, jsonify
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from sqlalchemy import inspect
from data import db_session
from forms.login import LoginForm
from forms.register import RegisterForm
from data.users import User
from data.tests import Test
from data.subthemes import Subtheme
from data.tasks import Task
from data.answers import Answer
from data.logs import Log
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = 'very secret key pam'
app.config['JSON_AS_ASCII'] = False
login_manager = LoginManager()
login_manager.init_app(app)
admin = Admin(app)


class MyModelView(ModelView):
    def is_accessible(self):
        if hasattr(current_user, 'id'):
            if current_user.id == 1:
                return True
        return False


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


@login_manager.user_loader
def load_user(user_id):
    db_ses = db_session.create_session()
    return db_ses.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/', methods=['GET', 'POST'])
def main_login_user():
    if hasattr(current_user, 'id'):
        return redirect('/main')
    form = LoginForm()
    if form.validate_on_submit():
        db_ses = db_session.create_session()
        user = db_ses.query(User).filter(User.email == form.email.data).first()
        if user.check_password(form.password.data):
            login_user(user)
            session['user_id'] = user.id
            return redirect('/main')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if hasattr(current_user, 'id'):
        return redirect('/main')
    form = RegisterForm()
    if form.validate_on_submit():
        db_ses = db_session.create_session()
        is_exists = db_ses.query(User).filter(User.email == form.email.data).first()
        if is_exists:
            return 'ERROR'
        user = User()
        user.email = form.email.data
        user.surname = form.surname.data
        user.name = form.name.data
        user.set_password(form.password.data)
        db_ses.add(user)
        db_ses.commit()
        login_user(user)
        session['user_id'] = user.id
        return redirect('/main')
    return render_template('register.html', form=form)


@app.route('/main')
@login_required
def main_page():
    if eval(current_user.tasks):
        db_ses = db_session.create_session()
        task = db_ses.query(Task).get(eval(current_user.tasks)[current_user.resolved])
        if task.type_task == 0:
            answers = []
        else:
            answers = '|'.join([i.answer for i in task.answers])
        return render_template('main.html', continue_task=1, task_pos=current_user.resolved,
                               task=task.task, test_id=current_user.test_id,
                               subtheme_id=current_user.subtheme_id, type_task=task.type_task,
                               answers=answers, id=current_user.id, main=True)
    return render_template('main.html', id=current_user.id, main=True)


@app.route('/making-tests')
@login_required
def making_tests():
    if current_user.id == 1:
        return render_template('main.html', making_tests=True, id=1)
    return redirect('/main')


@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    if current_user.id == user_id:
        db_ses = db_session.create_session()
        user = db_ses.query(User).get(user_id)
        logs = db_ses.query(Log).filter(Log.user_id == user_id).all()
        logs.reverse()
        refactored_logs = []
        month = datetime.datetime.now().month
        statistic_legend = ['5', '4', '3', '2']
        statistic = [0, 0, 0, 0]
        for log in logs:
            prc = int(round(log.success / log.resolved, 2) * 100)
            if log.date.month == month:
                if prc >= 87:
                    statistic[0] += 1
                elif prc >= 66:
                    statistic[1] += 1
                elif prc >= 42:
                    statistic[2] += 1
                else:
                    statistic[3] += 1
            refactored_logs.append({'date': str(log.date), 'theme': log.test.title,
                                    'subtheme': log.subtheme.title, 'success': log.success,
                                    'resolved': log.resolved, 'prc': prc})
        if statistic == [0, 0, 0, 0]:
            return render_template('profile.html', id=current_user.id, email=user.email,
                                   name=user.name, surname=user.surname, logs=logs,
                                   no_stat=True)
        else:
            plt.pie(statistic, labels=statistic_legend)
            plt.legend()
            plt.savefig('static/img/1.png')
            plt.close()
            return render_template('profile.html', id=current_user.id, email=user.email,
                                   name=user.name, surname=user.surname, logs=refactored_logs)
    return redirect('/profile/' + str(current_user.id))


# API
@app.route('/api/get-user-id', methods=['GET', 'POST'])
def get_user_id():
    return jsonify({'user_id': session['user_id']})


@app.route('/api/get-test/<int:test_id>', methods=['GET', 'POST'])
def get_test(test_id):
    db_ses = db_session.create_session()
    if test_id == 0:
        f = {'tests': [test.to_dict(rules=(
            '-subthemes.test', '-subthemes.tasks.subtheme', '-subthemes.tasks.answers.task'))
            for
            test in db_ses.query(Test).all()]}
    else:
        f = {'test': db_ses.query(Test).get(test_id).to_dict(
            rules=(
                '-subthemes.test', '-subthemes.tasks.subtheme',
                '-subthemes.tasks.answers.task'))}
    return jsonify(f)


@app.route('/api/start-test/<int:user_id>/<int:test_id>/<int:subtheme_id>',
           methods=['GET', 'POST'])
def start_test(user_id, test_id, subtheme_id):
    db_ses = db_session.create_session()
    f = db_ses.query(Subtheme).get(subtheme_id)
    user = db_ses.query(User).get(user_id)
    tmp = [task.id for task in f.tasks]
    random.shuffle(tmp)
    user.tasks = str(tmp)
    user.success = 0
    user.resolved = 0
    user.test_id = test_id
    user.subtheme_id = subtheme_id
    db_ses.commit()
    next_task_dict = next_task(user_id, -1, '-1')
    next_task_dict['description'] = f.description
    return next_task_dict


@app.route('/api/next-task/<int:user_id>/<int:task_pos>/<string:answer>',
           methods=['GET', 'POST'])
def next_task(user_id, task_pos, answer):
    db_ses = db_session.create_session()
    user = db_ses.query(User).get(user_id)
    tasks = eval(user.tasks)
    right_answer = db_ses.query(Answer).filter(Answer.right == 1,
                                               Answer.task_id == tasks[task_pos]).first()
    current_task = db_ses.query(Task).get(tasks[task_pos])
    task_pos += 1
    if answer != '-1':
        user.resolved += 1
        if answer == right_answer.answer:
            user.success += 1
            status = 'right'
        else:
            status = 'wrong'
    else:
        status = 'right'
    if task_pos >= len(tasks):
        success = user.success
        resolved = user.resolved
        user.success = 0
        user.resolved = 0
        user.tasks = '[]'
        log = Log()
        log.user_id = user.id
        log.test_id = current_task.subtheme.test_id
        log.subtheme_id = current_task.subtheme_id
        log.success = success
        log.resolved = resolved
        db_ses.add(log)
        db_ses.commit()
        if status == 'wrong':
            if current_task.type_task == 0:
                first = current_task.task[:int(right_answer.answer)]
                second = current_task.task[int(right_answer.answer) + 1:]
                right_letter = current_task.task[int(right_answer.answer)].upper()
            else:
                index = current_task.task.index('...')
                first = current_task.task[:index]
                second = current_task.task[index + 3:]
                right_letter = right_answer.answer.upper()
            db_ses.commit()
            return jsonify({'success': success, 'resolved': resolved, 'status': status,
                            'first': first, 'second': second,
                            'right_letter': right_letter})
        db_ses.commit()
        return jsonify({'success': success, 'resolved': resolved, 'status': status})
    else:
        task = db_ses.query(Task).get(tasks[task_pos])
        if task.type_task == 0:
            answers = []
        else:
            answers = [i.answer for i in task.answers]
        if status == 'wrong':
            if current_task.type_task == 0:
                first = current_task.task[:int(right_answer.answer)]
                second = current_task.task[int(right_answer.answer) + 1:]
                right_letter = current_task.task[int(right_answer.answer)].upper()
            else:
                index = current_task.task.index('...')
                first = current_task.task[:index]
                second = current_task.task[index + 3:]
                right_letter = right_answer.answer.upper()
            db_ses.commit()
            return jsonify(
                {'answers': answers, 'type_task': task.type_task, 'task_pos': task_pos,
                 'task': task.task, 'status': status, 'first': first, 'second': second,
                 'right_letter': right_letter})
        else:
            db_ses.commit()
            if answer == '-1':
                return {'answers': answers, 'type_task': task.type_task, 'task_pos': task_pos,
                        'task': db_ses.query(Task).get(tasks[task_pos]).task, 'status': status}
            return jsonify(
                {'answers': answers, 'type_task': task.type_task, 'task_pos': task_pos,
                 'task': db_ses.query(Task).get(tasks[task_pos]).task, 'status': status})


@app.route('/api/get-subthemes/<int:test_id>')
def get_subthemes(test_id):
    db_ses = db_session.create_session()
    # return jsonify({'subthemes': [subtheme.to_dict(rules=('-subtheme.test.subthemes', '-subtheme.tasks.subtheme', '-subtheme.tasks.answers.task')) for subtheme in db_ses.query(Subtheme).filter(Subtheme.test_id == test_id).all()]})
    return jsonify(
        {'subthemes': [object_as_dict(subtheme) for subtheme in db_ses.query(Subtheme).filter(
            Subtheme.test_id == test_id).all()]})


@app.route('/api/create-theme/<string:title>')
def create_test(title):
    db_ses = db_session.create_session()
    already_exists = db_ses.query(Test).filter(Test.title == title).first()
    if already_exists:
        return jsonify({'status': 400, 'Description': 'Already exists'})
    test = Test()
    test.title = title
    db_ses.add(test)
    db_ses.commit()
    return jsonify({"status": 200, 'Description': 'Success', 'Id': test.id})


@app.route('/api/create-subtheme/<int:test_id>/<string:title>/<string:description>')
def create_subtheme(test_id, title, description):
    db_ses = db_session.create_session()
    already_exists = db_ses.query(Subtheme).filter(Subtheme.title == title,
                                                   Subtheme.test_id == test_id).first()
    if already_exists:
        return jsonify({'status': 400, 'Description': 'Already exists'})
    subtheme = Subtheme()
    subtheme.title = title
    subtheme.description = description
    subtheme.test_id = test_id
    db_ses.add(subtheme)
    db_ses.commit()
    return jsonify({"status": 200, 'Description': 'Success', 'Id': subtheme.id})


@app.route(
    '/api/create-task/<int:subtheme_id>/<string:task_p>/<int:type_task>/<string:answers>')
def create_task(subtheme_id, task_p, type_task, answers):
    db_ses = db_session.create_session()
    already_exists = db_ses.query(Task).filter(Task.task == task_p,
                                               Task.subtheme_id == subtheme_id,
                                               Task.type_task == type_task).first()
    if already_exists:
        return jsonify({'status': 400, 'Description': 'Already exists'})
    task = Task()
    task.task = task_p
    task.subtheme_id = subtheme_id
    task.type_task = type_task
    answers = answers.split('|')
    for i in range(len(answers)):
        answer = Answer()
        answer.answer = answers[i]
        answer.task_id = task.id
        if not i:
            answer.right = 1
        else:
            answer.right = 0
        db_ses.add(answer)
        task.answers.append(answer)
    db_ses.add(task)
    db_ses.commit()
    return jsonify({"status": 200, 'Description': 'Success'})


if __name__ == '__main__':
    db_session.global_init('db/rus.db')
    db_sess = db_session.create_session()
    admin.add_view(MyModelView(User, db_sess))
    admin.add_view(MyModelView(Test, db_sess))
    admin.add_view(MyModelView(Subtheme, db_sess))
    admin.add_view(MyModelView(Task, db_sess))
    admin.add_view(MyModelView(Answer, db_sess))
    db_sess.close()
    app.run(port=5005)
