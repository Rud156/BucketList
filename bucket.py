from datetime import datetime
from hashlib import sha512
from random import sample

from bcrypt import hashpw, gensalt
from flask import Flask, render_template, url_for, request, session, redirect, flash, Markup, make_response
from gridfs import GridFS
from pymongo import MongoClient
from werkzeug.utils import secure_filename

allowed_extensions = ('png', 'jpg', 'gif', 'jpeg')
values = []
bucket_results = []
search_value = None

app = Flask(__name__)
client = MongoClient('localhost:27017')
db = client.BucketList
users = db.allUsers
all_tags = db.allTags
buckets = db.allBuckets
file_system = GridFS(db)


def allowed_check(file_name):
    file_type = file_name.split(".")
    if file_type[1].lower() in allowed_extensions:
        return True
    else:
        return False


def get_buckets(get_users):
    if get_users:
        login_user = users.find_one({'_id': session['username'].lower()})
        session['count'] = login_user['count']
        user_buckets = buckets.find({'user_name': session['username'].lower()})
        del values[:]
        for data in user_buckets:
            data_set = {
                'name': data['wish_name'],
                'picture': data['wish_pic'],
                'date': data['date'],
                'tags': data['tags'],
                'dateDiff': (datetime.strptime(data['date'], "%Y-%m-%d").date() - datetime.now().date()).days,
                'complete': data['complete']
            }
            values.append(data_set)
    else:
        results = buckets.find()
        del values[:]
        count = results.count()
        whole_numbers = range(0, count)
        if count == 0:
            return
        if count > 6:
            count = 6
        count = sample(whole_numbers, count)
        for i in range(0, len(count)):
            data_set = {
                'name': results[count[i]]['wish_name'],
                'picture': results[count[i]]['wish_pic'],
                'date': results[count[i]]['date'],
                'tags': results[count[i]]['tags'],
                'userName': results[count[i]]['user_name'].capitalize(),
                'dateDiff': (datetime.strptime(results[count[i]]['date'], "%Y-%m-%d").date()
                             - datetime.now().date()).days,
                'complete': results[count[i]]['complete']
            }
            values.append(data_set)


@app.route('/')
def index():
    if 'username' in session:
        get_buckets(True)
        return render_template('dashboard.html', result=values)

    else:
        get_buckets(False)
        return render_template('index.html', result=values, valueCount=len(values))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        login_user = users.find_one({'_id': request.form['userName'].lower()})

        if login_user is not None:
            if hashpw(request.form['passWord'].encode('utf-8'), login_user['password'].encode('utf-8')) == \
                    login_user['password'].encode('utf-8'):
                session['username'] = request.form['userName'].capitalize()
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
        existing_user = users.find_one({'_id': request.form['userName'].lower()})

        if existing_user is None:
            hash_pass = hashpw(request.form['passWord'].encode('utf-8'), gensalt())
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
                '_id': request.form['userName'].lower(),
                'name': request.form['userName'].lower(),
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
        if request.form['update'] == "0":
            tags = request.form['bucketTags']
            tags = tags.split("    ;")
            for i in range(0, len(tags)):
                tags[i] = tags[i].lower()
            # noinspection PyShadowingNames
            file_image = request.files['imageFile']
            result = allowed_check(file_image.filename)
            if not result:
                message = "Incorrect file type. Please input correct file('png', 'jpg', 'gif', 'jpeg')..."
                flash(message, category='submit')
                return redirect(url_for('index'))

            hash_obj = sha512(session['username'].lower() + request.form['wishName'].lower())
            hash_obj = hash_obj.hexdigest()
            existing_bucket = buckets.find_one({'hash_obj': hash_obj})

            if existing_bucket is None:
                file_name = secure_filename(file_image.filename)
                object_id = file_system.put(file_image, content_type=file_image.content_type, filename=file_name)

                data_set = {
                    'hash_obj': hash_obj,
                    'user_name': session['username'].lower(),
                    'wish_name': request.form['wishName'],
                    'wish_pic': file_name,
                    'objectId': str(object_id),
                    'date': request.form['date'],
                    'tags': tags,
                    'complete': "F"
                }
                current_user = users.find_one({'_id': session['username'].lower()})
                count = int(current_user['count'])
                users.update({'_id': session['username'].lower()}, {'$set': {'count': str(count + 1)}}, upsert=True)
                buckets.insert_one(data_set)
                for tag in tags:
                    all_tags.update({'_id': tag}, {'$addToSet': {'name': hash_obj}}, upsert=True)

            else:
                message = "Bucket already exists. Enter a new bucket name..."
                flash(message, category='submit')
                return redirect(url_for('index'))

        else:
            old_name = request.form['oldValue'].lower()
            new_name = request.form['wishName'].lower()
            tags = request.form['bucketTags']
            tags = tags.split('    ;')
            for i in range(0, len(tags)):
                tags[i] = tags[i].lower()
            old_tags = request.form['old_tags']
            old_tags = old_tags.split('    ;')
            for i in range(0, len(old_tags)):
                old_tags[i] = old_tags[i].lower();

            if old_name == new_name:
                hash_obj = sha512(session['username'].lower() + request.form['wishName'].lower())
                hash_obj = hash_obj.hexdigest()

                buckets.update({'hash_obj': hash_obj}, {'$set': {'date': request.form['date'], 'tags': tags}},
                               upsert=True)
                for tag in old_tags:
                    all_tags.update({'_id': tag}, {'$pull': {'name': hash_obj}}, upsert=True)
                for tag in tags:
                    all_tags.update({'_id': tag}, {'$addToSet': {'name': hash_obj}}, upsert=True)
            else:

                hash_obj = sha512(session['username'].lower() + request.form['wishName'].lower())
                hash_obj = hash_obj.hexdigest()
                old_hash = sha512(session['username'].lower() + request.form['oldValue'].lower())
                old_hash = old_hash.hexdigest()
                existing_bucket = buckets.find_one({'hash_obj': hash_obj})

                if existing_bucket is None:
                    buckets.update({'hash_obj': old_hash}, {'$set': {'wish_name': request.form['wishName'],
                                                                     'date': request.form['date'], 'tags': tags,
                                                                     'hash_obj': hash_obj}}, upsert=True)
                    for tag in old_tags:
                        all_tags.update({'_id': tag}, {'$pull': {'name': old_hash}}, upsert=True)
                    for tag in tags:
                        all_tags.update({'_id': tag}, {'$addToSet': {'name': hash_obj}}, upsert=True)

                else:
                    message = "Bucket already exists. Enter a new bucket name..."
                    flash(message, category='submit')
                    return redirect(url_for('index'))

    return redirect(url_for('index'))


@app.route('/complete', methods=['POST', 'GET'])
def complete():
    if request.method == "POST":
        bucket_name = request.form['complete'].lower()
        hash_obj = sha512(session['username'].lower() + bucket_name)
        hash_obj = hash_obj.hexdigest()
        buckets.update({'hash_obj': hash_obj}, {'$set': {'complete': "T"}}, upsert=True)

    return redirect(url_for('index'))


@app.route('/delete', methods=['POST', 'GET'])
def delete():
    if request.method == "POST":
        bucket_name = request.form['bucketName'].lower()
        tags = request.form['allTags']
        tags = tags.split('    ;')
        hash_obj = sha512(session['username'].lower() + bucket_name)
        hash_obj = hash_obj.hexdigest()

        buckets.delete_one({'hash_obj': hash_obj})
        for tag in tags:
            all_tags.update({'_id': tag.lower()}, {'$pull': {'name': hash_obj}}, upsert=True)

        current_user = users.find_one({'_id': session['username'].lower()})
        count = int(current_user['count'])
        users.update({'_id': session['username'].lower()}, {'$set': {'count': str(count - 1)}}, upsert=True)

    return redirect(url_for('index'))


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == "POST":
        global search_value
        search_value = request.form['searchInput'].split(" ")
        del bucket_results[:]
        result_search = []
        for i in range(0, len(search_value)):
            for j in range(i, len(search_value)):
                search_string = ""
                for k in range(i, j + 1):
                    search_string += search_value[k]
                    if k != j:
                        search_string += " "
                result_search.append(search_string)

        for searchTag in result_search:

            tags_array = all_tags.find_one({'_id': searchTag.lower()})
            if tags_array is not None:
                tags_array = tags_array['name']
                for tag in tags_array:
                    bucket = buckets.find_one({'hash_obj': tag})
                    data_set = {
                        'wishName': bucket['wish_name'],
                        'picture': bucket['wish_pic'],
                        'date': bucket['date'],
                        'userName': bucket['user_name'].capitalize(),
                        'tags': bucket['tags'],
                        'complete': bucket['complete']
                    }
                    if data_set not in bucket_results:
                        bucket_results.append(data_set)

        return render_template('search.html', search_tag=search_value, values=bucket_results)

    return redirect(url_for('index'))


@app.route('/home', methods=["GET", "POST"])
def home():
    return redirect(url_for('index'))


@app.route('/add_favourites', methods=["GET", "POST"])
def add_favourites():
    if request.method == "POST":
        user_name = request.form['searchUser'].lower()
        bucket_name = request.form['searchBucket'].lower()

        hash_obj = sha512(user_name + bucket_name)
        hash_obj = hash_obj.hexdigest()

        favourites = users.find_one({'_id': session['username'].lower()})
        favourites = favourites['favourites']
        if hash_obj not in favourites:
            message = "Added to favourites..."
            flash(message, category='favourite')
            users.update({'_id': session['username'].lower()}, {'$addToSet': {'favourites': hash_obj}}, upsert=True)
        else:
            message = "Already added to favourites..."
            flash(message, category='favourite')
        return render_template('search.html', search_tag=search_value.capitalize(), values=bucket_results)

    return redirect(url_for('index'))


@app.errorhandler(404)
def abort(e):
    return render_template('404.html')


@app.route('/images/<filename>')
def file_image(filename):
    thing = file_system.get_last_version(filename=filename)
    response = make_response(thing.read())
    response.mimetype = thing.content_type
    return response


if __name__ == '__main__':
    app.secret_key = 'someKey'
    app.run(debug=True)
