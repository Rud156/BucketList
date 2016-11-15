from gridfs import GridFS
from pymongo import MongoClient
# from bottle import route, run, template, response
from flask import Flask, make_response

client = MongoClient('localhost:27017')
db = client.BucketList
users = db.allUsers
file_system = GridFS(db)


'''@route('/static/img/gridfs/<filename>')
def gridfs_img(filename):
    # http://localhost:8080/static/img/gridfs/6788333-fairy-tail-wallpaper.jpg
    thing = file_system.get_last_version(filename=filename)
    response.content_type = 'image/jpeg'
    return thing

run(host='localhost', port=8080) '''


app = Flask(__name__)


@app.route('/static/img/gridfs/<filename>')
def file_image(filename):
    print "Calling Function"
    thing = file_system.get_last_version(filename=filename)
    response = make_response(thing.read())
    response.mimetype = thing.content_type
    return response

app.run()
