import random
from flask import Flask, render_template, redirect, session, jsonify
from flask_login import LoginManager, login_required, logout_user, login_user
from data import db_session
from forms.login import LoginForm
from forms.register import RegisterForm
from data.users import User
from data.tests import Test
from data.subthemes import Subtheme


app = Flask(__name__)
app.secret_key = 'very secret key pam'
app.config['JSON_AS_ASCII'] = False
login_manager = LoginManager()
login_manager.init_app(app)


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
def main_page():
    return render_template('main.html')


#API
@app.route('/api/get-user-id', methods=['GET', 'POST'])
def get_user_id():
    return jsonify({'user_id': session['user_id']})


@app.route('/api/get-test/<int:test_id>', methods=['GET', 'POST'])
def get_test(test_id):
    db_ses = db_session.create_session()
    if test_id == 0:
        f = {'tests': [test.to_dict(rules=('-subthemes.test', '-subthemes.tasks.subtheme')) for test in db_ses.query(Test).all()]}
    else:
        f = {'test': db_ses.query(Test).get(test_id).to_dict(rules=('-subthemes.test', '-subthemes.tasks.subtheme'))}
    return jsonify(f)


@app.route('/api/start-test/<int:user_id>/<int:test_id>/<int:subtheme_id>', methods=['GET', 'POST'])
def start_test(user_id, test_id, subtheme_id):
    db_ses = db_session.create_session()
    f = db_ses.query(Subtheme).get(subtheme_id)
    user = db_ses.query(User).get(user_id)
    tmp = [task.task for task in f.tasks]
    random.shuffle(tmp)
    user.tasks = str(tmp)
    user.success = 0
    user.resolved = 0
    db_ses.commit()
    next_task_dict = next_task(user_id, -1, 0)
    next_task_dict['description'] = f.description
    return next_task_dict


@app.route('/api/next-task/<int:user_id>/<int:last_task_id>/<int:last_status>', methods=['GET', 'POST'])
def next_task(user_id, last_task_id, last_status): # last_status: 0 - first task, 1 - last task was right, 2 - last task was wrong
    db_ses = db_session.create_session()
    user = db_ses.query(User).get(user_id)
    if last_status != 0:
        user.resolved += 1
        if last_status == 1:
            user.success += 1
    db_ses.commit()
    tasks = eval(user.tasks)
    last_task_id += 1
    if last_task_id >= len(tasks):
        resolved = user.resolved
        success = user.success
        user.resolved = 0
        user.success = 0
        user.tasks = '[]'
        db_ses.commit()
        return jsonify({'success': success, 'resolved': resolved})
    if last_status == 0:
        return {'task_id': last_task_id, 'task': eval(user.tasks)[last_task_id]}
    return jsonify({'task_id': last_task_id, 'task': eval(user.tasks)[last_task_id]})


if __name__ == '__main__':
    db_session.global_init('db/rus.db')
    app.run(port=5005)
