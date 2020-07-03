# python3 
# Flask-Python + MongoDB Audio Streaming
# Author: Zhihong Li(zhihongli@bennington.edu)
# Date: July, 2nd, 2020

import os
from flask_pymongo import PyMongo
from flask import Flask, Response, send_file,\
                        send_from_directory, stream_with_context, \
                        render_template, url_for, redirect


app = Flask(__name__)

# config
app_dir_path = app.instance_path
mongo = PyMongo(app, uri="mongodb://localhost:27017/soundcloud")

"""
In order for clients to know that partial content is supported by the 
server, the server needs to add the following header to the response —
"Accept-Ranges": "bytes" This implies that server is capable of serving 
partial content, specified as a range of bytes. To add this header to 
responses, one can use the following decoration —
"""
@app.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response


@app.route('/')
def hello():
    return render_template("index.html")


@app.route('/music/<music_name>')
# last TODO: need to protect this folder make sure there's login needed
def return_music(music_name):
    try:
        return send_from_directory(app.config['music'], music_name, as_attachment=True)
    except Exception as e:
        # return 404 if music not found
        return e, 404


@app.route('/<string:username>')
def show_profile(username):
    user = mongo.db.users.find_one({"name": username})
    if user == None:
        return redirect('/')
    return render_template("test.html", name = user['name'], song = "none") 
    # upload music how to render lots of music?


@app.route('/<string:username>/upload', methods = ['GET', 'POST'])
def upload(username):
    user = mongo.db.users.find_one({"name": username})
    if user == None:
        return redirect('/')
    return render_template("test.html", name = username, song = "")


if __name__ == "__main__":
    # for testing purpose, we gonna drop all collections before the program starts
    # mongo.db.drop_collection("user")
    # mongo.db.drop_collection("fs.chunks")
    # mongo.db.drop_collection("fs.files")

    app.run(host="0.0.0.0")
    print("hello")

"""
reference:
flask doc
https://flask.palletsprojects.com/

build a simple blog with flask
https://flask.palletsprojects.com/en/1.1.x/tutorial/#tutorial

stream at certain spot as needed - particial stream
https://medium.com/@richard534/uploading-streaming-audio-using-nodejs-express-mongodb-gridfs-b031a0bcb20f

stream audio flask
https://gist.github.com/hosackm/289814198f43976aff9b


generator python
https://www.youtube.com/watch?v=bD05uGo_sVI

mimetype
https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
https://www.iana.org/assignments/media-types/media-types.xhtml


Uploading/Streaming Audio using NodeJS + Express + MongoDB/GridFS
https://medium.com/@richard534/uploading-streaming-audio-using-nodejs-express-mongodb-gridfs-b031a0bcb20f


Audio liveStream with Python & Flask
https://stackoverflow.com/questions/51079338/audio-livestreaming-with-python-flask


HTTP 206(Partial Content) for Flask/Python
https://blog.asgaard.co.uk/2012/08/03/http-206-partial-content-for-flask-python

serve partial content flask code repo
https://gist.github.com/singhpratyush/


Sending files with Flask | Learning Flask - with  flask.send_from_directory function
customize app.config['directory_name'] then use it
https://pythonise.com/series/learning-flask/sending-files-with-flask


*****save and retrieve files in a mongodb with flask-python web app****
https://www.youtube.com/watch?v=DsgAuceHha4

# difference between pymongo and flask-pymongo libraries
https://stackoverflow.com/questions/31748141/difference-between-pymongo-and-flask-pymongo-libraries

flask-pymongo doc
https://flask-pymongo.readthedocs.io/en/latest/

flask-pymongo insert
https://www.youtube.com/watch?v=4o7C4JMGLe4

Mongodb-Flask libraries
https://stackoverflow.com/questions/41514896/how-can-i-use-mongodb-with-flask/41519867

The Taste of Media Streaming with Flask
https://codeburst.io/the-taste-of-media-streaming-with-flask-cdce35908a50





Other people's Application:
Open source, web-based music player for the cloud.
https://github.com/jakubroztocil/cloudtunes

souncCloud architecture development history
https://developers.soundcloud.com/blog/evolution-of-soundclouds-architecture

more Flask Tutorial:
https://pythonprogramming.net/flask-send-file-tutorial/


write music player with flask-python when music is stored statically
https://blog.csdn.net/qq_41706810/article/details/105824365

html music player
https://blog.csdn.net/mianbaolixiang/article/details/90515139?utm_medium=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-2.nonecase&depth_1-utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-2.nonecase


"""

