from flask import Flask, render_template, url_for, request, session, redirect, flash, Markup, make_response
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from gridfs import GridFS
import bcrypt
import re

allowed_extensions = ('png', 'jpg', 'gif', 'jpeg')
values = []

app = Flask(__name__)
client = MongoClient('localhost:27017')
db = client.BucketList
users = db.allUsers
file_system = GridFS(db)


def allowed_check(file_name):
    file_type = file_name.split(".")
    if file_type[1] in allowed_extensions:
        return True
    else:
        return False


def get_wishes(user_name):
    login_user = users.find_one({'_id': user_name})
    count = int(login_user['count'])
    del values[:]
    for i in range(0, count):
        print "Value of count: " + str(i)
        data_set = {
            'name': login_user[str(i)]['wish_name'],
            'picture': login_user[str(i)]['wish_pic']
        }
        values.append(data_set)

    print "Result: " + str(values)


@app.route('/')
def index():
    if 'username' in session:
        get_wishes(session['username'])
        return render_template('dashboard.html', result=values)

    else:
        return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    login_user = users.find_one({'_id': request.form['userName']})

    if login_user is not None:
        if bcrypt.hashpw(request.form['passWord'].encode('utf-8'), login_user['password'].encode('utf-8')) == \
                login_user['password'].encode('utf-8'):
            session['username'] = request.form['userName']
            session['picture'] = login_user['pictureName']
            session['quote'] = login_user['quote']
            session['count'] = login_user['count']
            return redirect(url_for('index', result=values))

    message = Markup("Invalid username or password...")
    flash(message, category='login')
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        existing_user = users.find_one({'_id': request.form['userName']})

        if existing_user is None:
            hash_pass = bcrypt.hashpw(request.form['passWord'].encode('utf-8'), bcrypt.gensalt())
            # noinspection PyShadowingNames
            file_image = request.files['file']
            result = allowed_check(file_image.filename)
            if not result:
                message = "Incorrect file type. Please input correct file('png', 'jpg', 'gif', 'jpeg')..."
                flash(message, category='signup')
                return redirect(url_for('index'))
            file_name = secure_filename(file_image.filename)
            object_id = file_system.put(file_image, content_type=file_image.content_type, filename=file_name)
            data_set = {
                '_id': request.form['userName'],
                'name': request.form['userName'],
                'quote': request.form['userQuote'],
                'password': hash_pass,
                'picture': str(object_id),
                'pictureName': file_name,
                'count': "0"
            }
            users.insert(data_set)
            message = Markup("Successfully Registered. Please login to continue...")
            flash(message=message, category='login')
            return redirect(url_for('index'))

        else:
            message = "Username already exists. Please select a new one..."
            flash(message=message, category='signup')
            return redirect(url_for('index'))


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/submitWish', methods=['POST'])
def submit_wish():

    tags = request.form['tags']
    tags = tags.split(";")
    for i in range(0, len(tags)):
        tags[i] = tags[i].strip()

    data_set = {
        'wish_name': request.form['wishName'],
        'wish_pic': request.form['wishPic'],
        'date': request.form['date'],
        'tags': tags
    }

    current_user = users.find_one({'_id': session['username']})
    count = int(current_user['count'])
    users.update({'_id': session['username']}, {'$set': {str(count): data_set}}, upsert=True)
    users.update({'_id': session['username']}, {'$set': {'count': str(count + 1)}}, upsert=True)

    return render_template('dashboard.html')


@app.route('/images/<filename>')
def file_image(filename):
    thing = file_system.get_last_version(filename=filename)
    response = make_response(thing.read())
    response.mimetype = thing.content_type
    return response


if __name__ == '__main__':
    app.secret_key = 'someKey'
    app.run(debug=True)
