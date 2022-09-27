import random
import json
import os
from flask import Flask, render_template, redirect, session, jsonify
from flask_login import LoginManager, login_required, logout_user, login_user
from data import db_session
from forms.login import LoginForm
from forms.register import RegisterForm
from data.users import User

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
    current_dir = str(os.getcwd())
    os.chdir(current_dir + '/tests')
    titles = []
    files = os.listdir()
    for i in range(len(files)):
        f = json.load(open(str(i + 1) + '.json', encoding='utf-8'))
        titles.append(f['title'])
    os.chdir(current_dir)
    return render_template('main.html', titles=titles)


#API
@app.route('/api/get-user-id', methods=['GET', 'POST'])
def get_user_id():
    return jsonify({'user_id': session['user_id']})


@app.route('/api/get-test/<int:test_id>', methods=['GET', 'POST'])
def get_test(test_id):
    current_dir = str(os.getcwd())
    os.chdir(current_dir + '/tests')
    if test_id == 0:
        f = {'tests': []}
        for i in os.listdir():
            f['tests'].append(json.load(open(i, encoding='utf-8')))
    else:
        f = json.load(open(str(test_id) + '.json', encoding='utf-8'))
    os.chdir(current_dir)
    return jsonify(f)


@app.route('/api/start-test/<int:user_id>/<int:test_id>/<int:subtheme_id>', methods=['GET', 'POST'])
def start_test(user_id, test_id, subtheme_id):
    db_ses = db_session.create_session()
    current_dir = str(os.getcwd())
    os.chdir(current_dir + '/tests')
    f = json.load(open(str(test_id) + '.json', encoding='utf-8'))
    user = db_ses.query(User).get(user_id)
    tmp = f['subthemes'][subtheme_id]['tasks']
    random.shuffle(tmp)
    user.tasks = str(tmp)
    user.success = 0
    user.resolved = 0
    db_ses.commit()
    os.chdir(current_dir)
    next_task_dict = next_task(user_id, -1, 0)
    next_task_dict['description'] = f['subthemes'][subtheme_id]['description']
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
    # last = str(os.getcwd())
    # os.chdir(str(os.getcwd()) + '/tests')
    # print(os.listdir())
    # os.chdir(last)
    db_session.global_init('db/rus.db')
    app.run(port=5005)



# {% extends "base.html" %}
# {% block content %}
# <div id="parent">
#     <h1 class="h1_title">Темы тестов</h1>
#     <div class="tests_themes">
#         {% for i in range(titles|length) %}
#         <h1 class="test_theme_and_subtheme" data-test-id="{{ i }}" onclick="open_test(this)">{{ i + 1 }}. {{ titles[i] }}</h1>
#         {% endfor %}
#     </div>
# </div>
# {% endblock %}