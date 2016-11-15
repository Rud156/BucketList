from flask import Flask, render_template, url_for, request, session, redirect, flash, Markup, make_response
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from gridfs import GridFS
import bcrypt

allowed_extensions = ('png', 'jpg', 'gif', 'jpeg')

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'BucketList'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/BucketList'
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


def get_image(object_id):
    image_file = file_system.get(ObjectId(object_id))
    response = make_response(image_file.read())
    response.mimetype = image_file.content_type
    return response


@app.route('/')
def index():
    if 'username' in session:
        return render_template('dashboard.html')

    else:
        return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    login_user = users.find_one({'_id': request.form['userName']})

    if login_user is not None:
        if bcrypt.hashpw(request.form['passWord'].encode('utf-8'), login_user['password'].encode('utf-8')) == \
                login_user['password'].encode('utf-8'):
            session['username'] = request.form['userName']

            '''image = get_image(login_user['picture'])
            image = convert_image(image.data, image.content_type)
            session['picture'] = '<img class="profilePic" width="250px" src="{}" />'.format(image)'''

            session['picture'] = login_user['pictureName']
            session['quote'] = login_user['quote']
            return redirect(url_for('index'))

    message = Markup("Invalid username or password...")
    flash(message, category='login')
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        existing_user = users.find_one({'name': request.form['userName']})

        if existing_user is None:
            hash_pass = bcrypt.hashpw(request.form['passWord'].encode('utf-8'), bcrypt.gensalt())
            file_image = request.files['file']
            result = allowed_check(file_image.filename)
            if not result:
                message = "Incorrect file type. Please input correct file..."
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
                'pictureName': file_name
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


@app.route('/images/<filename>')
def file_image(filename):
    thing = file_system.get_last_version(filename=filename)
    response = make_response(thing.read())
    response.mimetype = thing.content_type
    return response


if __name__ == '__main__':
    app.secret_key = 'someKey'
    app.run(debug=True)
