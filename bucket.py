from flask import Flask, render_template, url_for, request, session, redirect, flash, Markup, make_response
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from gridfs import GridFS
from datetime import datetime
from random import sample
import bcrypt


allowed_extensions = ('png', 'jpg', 'gif', 'jpeg', 'JPG')
values = []

app = Flask(__name__)
client = MongoClient('localhost:27017')
db = client.BucketList
users = db.allUsers
all_tags = db.allTags
buckets = db.allBuckets
file_system = GridFS(db)


def allowed_check(file_name):
    file_type = file_name.split(".")
    if file_type[1] in allowed_extensions:
        return True
    else:
        return False


def get_wishes(get_users):
    if get_users:
        login_user = users.find_one({'_id': session['username']})
        session['count'] = login_user['count']
        user_buckets = buckets.find({'user_name': session['username']})
        del values[:]
        for data in user_buckets:
            data_set = {
                'name': data['wish_name'],
                'picture': data['wish_pic'],
                'date': data['date'],
                'tags': data['tags'],
                'dateDiff': (datetime.strptime(data['date'], "%Y-%m-%d").date() - datetime.now().date()).days
            }
            values.append(data_set)
    else:
        results = buckets.find()
        del values[:]
        count = results.count()
        if count == 0:
            return
        if count > 6:
            count = 6
        whole_numbers = range(0, count)
        count = sample(whole_numbers, count)
        for i in range(0, len(count)):
            data_set = {
                'name': results[count[i]]['wish_name'],
                'picture': results[count[i]]['wish_pic'],
                'date': results[count[i]]['date'],
                'tags': results[count[i]]['tags'],
                'userName': results[count[i]]['user_name'],
                'dateDiff': (datetime.strptime(results[count[i]]['date'], "%Y-%m-%d").date()
                             - datetime.now().date()).days
            }
            values.append(data_set)


@app.route('/')
def index():
    if 'username' in session:
        get_wishes(True)
        return render_template('dashboard.html', result=values)

    else:
        get_wishes(False)
        return render_template('index.html', result=values, valueCount=len(values))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        login_user = users.find_one({'_id': request.form['userName']})

        if login_user is not None:
            if bcrypt.hashpw(request.form['passWord'].encode('utf-8'), login_user['password'].encode('utf-8')) == \
                    login_user['password'].encode('utf-8'):
                session['username'] = request.form['userName']
                session['picture'] = login_user['pictureName']
                session['quote'] = login_user['quote']
                session['count'] = login_user['count']
                return redirect(url_for('index'))

        message = Markup("Invalid username or password...")
        flash(message, category='login')
        return redirect(url_for('index'))

    else:
        return redirect(url_for('index'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        print "Function Called"
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

    else:
        return redirect(url_for('index'))


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/submitWish', methods=['POST', 'GET'])
def submit_wish():
    if request.method == 'POST':
        tags = request.form['bucketTags']
        tags = tags.split("    ;")
        # noinspection PyShadowingNames
        file_image = request.files['imageFile']
        result = allowed_check(file_image.filename)
        if not result:
            message = "Incorrect file type. Please input correct file('png', 'jpg', 'gif', 'jpeg')..."
            flash(message, category='submit')
            return redirect(url_for('index'))

        file_name = secure_filename(file_image.filename)
        object_id = file_system.put(file_image, content_type=file_image.content_type, filename=file_name)

        data_set = {
            'user_name': session['username'],
            'wish_name': request.form['wishName'],
            'wish_pic': file_name,
            'objectId': str(object_id),
            'date': request.form['date'],
            'tags': tags
        }

        current_user = users.find_one({'_id': session['username']})
        count = int(current_user['count'])
        users.update({'_id': session['username']}, {'$set': {'count': str(count + 1)}}, upsert=True)
        buckets.insert_one(data_set)
        for tag in tags:
            data = all_tags.find({'_id': tag})
            count = data.count()
            if count <= 0:
                all_tags.update({'_id': tag}, {'$set': {'count': "1", "1": data_set}}, upsert=True)
            else:
                current_count = int(data[0]['count']) + 1
                all_tags.update({'_id': tag}, {'$set': {'count': str(current_count), str(current_count): data_set}}, upsert=True)

    return redirect(url_for('index'))


@app.route('/images/<filename>')
def file_image(filename):
    thing = file_system.get_last_version(filename=filename)
    response = make_response(thing.read())
    response.mimetype = thing.content_type
    return response


if __name__ == '__main__':
    app.secret_key = 'someKey'
    app.run(debug=True)
