from flask import (Flask, 
                   render_template,
                   request,
                   make_response,
                   redirect,
                   url_for,
                   flash,
                   get_flashed_messages,
                   session, 
                   )
import json
import uuid

app = Flask(__name__)
app.secret_key = '0e3a3036c7079e521eb2fa86d77d409d11c72b27'


# Аутентификация
@app.route('/')
def index():
    if 'login' in session:
        return redirect(url_for('get_users'), code=302)
    else:
        return redirect(url_for('login'), code=302)


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        session['login'] = request.form['login']
        return redirect(url_for('get_users'), code=302)


# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'), code=302)


# Список пользователей
@app.route('/users')
def get_users():
    users = json.loads(request.cookies.get('data_base_users', json.dumps([])))
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'index.html',
        users=users,
        messages=messages,
        )


# Профиль пользователя
@app.route('/users/<id>')
def get_user(id):
    users = json.loads(request.cookies.get('data_base_users', json.dumps([])))
    user = list(filter(lambda u: u.get('id') == id, users))[0]

    if not user:
        return 'Page not found', 404

    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'show.html',
        user=user,
        messages=messages,
        )


# Создание нового пользователя
@app.route('/users/new', methods=['GET', 'POST'])
def new_user():
    users = json.loads(request.cookies.get('data_base_users', json.dumps([])))

    if request.method == 'GET':
        user = {'id': '', 'nickname': '', 'email': ''}
        errors = {}
        return render_template(
            'new/new.html',
            user=user,
            errors=errors,
        )

    if request.method == 'POST':
        user = request.form.to_dict()
        if errors := validate(user):
            return render_template(
                'new/new.html',
                user=user,
                errors=errors,
            ), 422
        
        user['id'] = str(uuid.uuid4())
        users.append(user)
        encoded_users = json.dumps(users)
        response = make_response(redirect(url_for('get_users'), code=302))
        response.set_cookie('data_base_users', encoded_users)
        flash('Пользователь успешно добавлен!', 'success')
        return response 


# Редактирование профиля
@app.route('/users/<id>/edit', methods=['GET', 'POST'])
def edit_user(id):
    users = json.loads(request.cookies.get('data_base_users', json.dumps([])))
    user = list(filter(lambda u: u.get('id') == id, users))[0]
    errors = {}
    
    if request.method == 'GET':
        return render_template(
            'edit.html',
            user=user,
            errors=errors,
        )
    
    if request.method == 'POST':
        patch_data = request.form.to_dict()
        if errors := validate(patch_data):
            return render_template(
                'edit.html',
                user=patch_data,
                errors=errors,
                ), 422
        
        user['nickname'] = patch_data['nickname']
        user['email'] = patch_data['email']
        encoded_users = json.dumps(users)
        response = make_response(redirect(url_for('get_users', id=id),
                                                  code=302))
        response.set_cookie('data_base_users', encoded_users)
        flash('Профиль обновлен', 'success')
        return response


# Удаление пользователя
@app.route('/users/<id>/delete', methods=['POST'])
def delete_user(id):
    users = json.loads(request.cookies.get('data_base_users', json.dumps([])))

    for index, user in enumerate(users):
        if user.get('id') == id:
            deleted_username = user.get('nickname')
            del users[index]
            break

    encoded_users = json.dumps(users)
    response = make_response(redirect(url_for('get_users'), code=302))
    response.set_cookie('data_base_users', encoded_users)
    flash(f"Пользователь {deleted_username} удален", 'success')
    return response


# Валидация форм
def validate(user):
    errors = {}
    if not user.get('nickname'):
        errors['nickname'] = "Can't be empty"
    if not user.get('email'):
        errors['email'] = "Can't be empty"
    return errors
    
    



