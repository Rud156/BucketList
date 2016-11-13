from flask import Flask, render_template, url_for, request, session, redirect, flash, Markup
from flask_pymongo import PyMongo
import bcrypt


app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'BucketList'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/BucketList'
mongo = PyMongo(app)


@app.route('/')
def index():
    if 'username' in session:
        return render_template('dashboard.html')

    else:
        return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.allUsers
    login_user = users.find_one({'_id': request.form['userName']})

    if login_user is not None:
        if bcrypt.hashpw(request.form['passWord'].encode('utf-8'), login_user['password'].encode('utf-8')) == \
                login_user['password'].encode('utf-8'):
            session['username'] = request.form['userName']
            session['picture'] = login_user['picture']
            return redirect(url_for('index'))

    message = Markup("Invalid username or password...")
    flash(message, category='login')
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        users = mongo.db.allUsers
        existing_user = users.find_one({'name': request.form['userName']})

        if existing_user is None:
            hash_pass = bcrypt.hashpw(request.form['passWord'].encode('utf-8'), bcrypt.gensalt())
            data_set = {
                '_id': request.form['userName'],
                'name': request.form['userName'],
                'password': hash_pass,
                'picture': request.form['userPic']
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


if __name__ == '__main__':
    app.secret_key = 'someKey'
    app.run(debug=True)
