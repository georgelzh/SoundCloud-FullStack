#!python3 
# Flask-Python + MongoDB Audio Streaming
# Author: Zhihong Li(zhihongli@bennington.edu)
# Date: July, 2nd, 2020


# db
from flask_pymongo import PyMongo
from bson import ObjectId
from gridfs import GridFS, GridFSBucket, NoFile

# flask
import os
from flask import Flask, send_file,request, make_response, \
                        redirect, stream_with_context, \
                        render_template, url_for, current_app, \
                        jsonify
# registration package
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.wsgi import wrap_file
from werkzeug.exceptions import abort


app = Flask(__name__)   #static_folder="music" if needed
app.secret_key="dev"

app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 # 10 mb maximize size upload file

mongo = PyMongo(app, uri="mongodb://root:root@mongo:27017/soundcloud?authSource=admin")

# config

storage_bucket = GridFSBucket(mongo.db)
storage = GridFS(mongo.db, "fs")


@app.before_request
def load_logged_in_user():
    username = session.get('username')
    if username is None:
        g.user = None
    else:
        user = mongo.db.users.find_one({"username": username})
        key_to_extract = ["_id", "username"]
        g.user = {key: user[key] for key in key_to_extract}

@app.after_request
def after_request(response):
    """
    In order for clients to know that partial content is supported by the 
    server, the server needs to add the following header to the response —
    "Accept-Ranges": "bytes" This implies that server is capable of serving 
    partial content, specified as a range of bytes. To add this header to 
    responses, one can use the following decoration —
    """
    response.headers.add('Accept-Ranges', 'bytes')
    return response


def login_required(view):
    """
    Require Authentication in Other Views¶
    Creating, editing, and deleting blog posts will require a user to be logged in. 
    A decorator can be used to check this for each view it’s applied to.

    This decorator returns a new view function that wraps the original view it’s applied to. 
    The new function checks if a user is loaded and redirects to the login page otherwise. 
    If a user is loaded the original view is called and continues normally. You’ll use this 
    decorator when writing the blog views.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect("/login")
        return view(**kwargs)
    return wrapped_view

@app.route('/')
def show_index():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        confirm_password = request.form['password_confirm']
        email = request.form['email']
        
        if username == None or password == None or confirm_password == None or email == None:
            error = "Please fill in all the blank required"
            flash(error)
            return render_template("register.html")
        if password != confirm_password:
            error = "password do not match each other"
            flash(error)
            return render_template("register.html")
        elif mongo.db.users.find_one({"username": username}) is not None:
            error = "username already exists, please change another one."
            flash(error)
            return render_template("register.html")
        else:
            mongo.db.users.insert_one({"username": username, "password": generate_password_hash(password), "email": email})
            success = "successful register!"
            flash(success)
            return render_template("register.html")
    elif request.method == "GET":
        return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        user = mongo.db.users.find_one({"username": username})
        if user is None:
            error = "user does not exists"
            flash(error)
            return render_template("login.html") #, error = error
        if check_password_hash(user['password'], password) == False:
            error = "incorrect password, please try again"
            flash(error)
            return render_template("login.html", error = error)
        else:
            session.clear()
            session['username'] = user['username']
            return redirect(url_for('show_profile', username = username))
    if request.method == 'GET':
        if "username" in session:
            return redirect(url_for('show_profile', username = session['username']))
        return render_template("login.html")


@app.route('/logout')
@login_required
def logout():
    session.clear()
    success = "successfully loged out"
    flash(success)
    return redirect('/')


@app.route('/music/<music_file_id>')
def fetch_music(music_file_id, cache_for=31536000):
    try:
        # package the response
        audio_file_obj = storage.get(ObjectId(music_file_id))
        # audio_file_obj = storage.get_version("better_now.mp3") # this also works, but i'd like to send via objectID
        data = wrap_file(request.environ, audio_file_obj, buffer_size=1024 * 255) # wrap it for response class set up
        resp = current_app.response_class(data, mimetype=audio_file_obj.content_type , direct_passthrough=True) # flask.Response class
        resp.content_length = audio_file_obj.length
        resp.last_modified = audio_file_obj.upload_date
        # resp.set_etag(audio_file_obj.md5)   # this line is now causing issue with playing mp3 on web app. maybe its out of date function.
        resp.cache_control.max_age = cache_for  # time the client is able to cache 
        resp.cache_control.public = True
        resp.make_conditional(request)
        return resp
    except Exception as e:
        # return 404 if music not found
        return e, 404


@app.route('/upload', methods = ['GET', 'POST'])
@login_required
def upload():
    if request.method == 'GET':
        return render_template('upload.html')

    if request.method == "POST":
        music_file = "failed to upload"

        track_titile = request.form.get("track title")
        
        if "music_file" in request.files:
            # upload
            music_file = request.files['music_file']            
            if music_file == "failed to upload" or music_file == None:
                return music_file, 400
            
            mongo.save_file(filename=track_titile, 
                                fileobj=music_file, artist_name = g.user['username'], artist_id = g.user["_id"])
        flash("successfully uploaded track '{0}'".format(track_titile))
        return redirect('/profile/{0}'.format(g.user['username']))


@app.route('/delete/<music_file_id>', methods=['POST'])
@login_required
def delete(music_file_id):
    music_file_id = ObjectId(music_file_id)
    if music_file_id is None or storage.exists(music_file_id) != True:
        flash("music_file does not exist")
        return redirect('/profile/{0}'.format(g.user['username']))
    else:
        music_file_info = mongo.db.fs.files.find_one({"_id": music_file_id})
        if music_file_info['artist_id'] != g.user['_id']:
            flash("you can not delete track that does not belong to you")
            return redirect('/')
        else:
            storage.delete(music_file_id)
            flash("successfully deleted the track '{0}'".format(music_file_info['filename']))
            return redirect('/profile/{0}'.format(g.user['username']))


@app.route('/profile/<string:username>')
@app.route('/profile/<string:username>/')
def show_profile(username):
    username = username.lower()
    user = mongo.db.users.find_one({"username": username})
    if user == None:
        return redirect('/')
    # retrieve all tracks from the artist
    tracks = mongo.db.fs.files.find({"artist_name": username})
    # display track_list via jinja
    return render_template("profile.html", username = username, tracks = tracks)

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'GET':
        return render_template("account.html")
    elif request.method == 'POST':
        form = request.form['form']
        # if change email form is submitted
        if form == "change_email":
            new_email = request.form['new_email']
            pwd = request.form['pwd']
            user = mongo.db.users.find_one({"_id": g.user['_id']})
            if check_password_hash(user['password'], pwd) == True:
                mongo.db.users.find_one_and_update({"username": g.user['username']},
                            { "$set": {"email": new_email} }, upsert=True)
                flash("successfully updated your email address!")
                return redirect('/account')
            else:
                flash("incorrect password, please try again")
                return render_template("account.html")
        # if change_pwd form is submitted
        if form == "change_pwd":
            old_pwd = request.form['old_pwd']
            new_pwd = request.form['new_pwd']
            user = mongo.db.users.find_one({"_id": g.user['_id']})
            if check_password_hash(user['password'], old_pwd) == True:
                mongo.db.users.find_one_and_update({"username": g.user['username']},
                            { "$set": {"password": generate_password_hash(new_pwd)} }, upsert=True)
                flash("successfully updated your password!")
                return redirect('/account')
            else:
                flash("incorrect password, please try again")
                return render_template("account.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)


"""
security can be improved. 
For eg: session and g.user should only store user['_id'] and user['username'] nothing else
print(g.user)
{'_id': ObjectId('5f052dddefc9b24cb4e2b85a'), 'username': 'george', 
'password': 'pbkdf2:sha256:150000$vemmVBEU$de9aa3ce6bf464af89b064843729ad2356ff6532c8b37dbd6b86560e71c45106', 
'email': 'hello@bennington.edu', 'tracks': {}}
"""

"""
connect files with authentication

mongo = PyMongo(app, uri="mongodb://root:xx@34.72.14.239:27017/soundcloud?authSource=admin")

https://stackoverflow.com/questions/37945262/authentication-failed-when-using-flask-pymongo
app.config['MONGO_HOST'] = '34.72.14.239'
app.config['MONGO_PORT'] = '27017'
app.config['MONGO_DBNAME'] = 'soundcloud'
app.config['MONGO_USERNAME'] = 'root'
app.config['MONGO_PASSWORD'] = 'xxxx'
app.config['MONGO_AUTH_SOURCE'] = 'admin' . # root user is typically defined in admin db
"""

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

mimetype - content-type
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


**************
hash table and chain----------Ideas for database management:

there can be unique collection that only stores hashtable for song collections. 
that will increase query speed since it's a harsh table. we don't need to go 
through the whole database to query a specific song that might be extremly 
hard to find
we just doing simple version for now
https://www.youtube.com/watch?v=shs0KM3wKv8
***********************


//////////////////---------wrap the audio file and customize the http Response
in terms of returning mp3 from mongodb gridfs to the http request
1. need to get the file according to the ObjectId(...) from mongodb Gridfs
2. need to understand http response
3. wrap a file with http response with the specific content-type audio in this case
4. return the response that wraps the audio file

object that gridfs returns when we get the file by ObjectId (GridOut object)
https://api.mongodb.com/python/current/api/gridfs/grid_file.html#gridfs.grid_file.GridOut

Gridfs for file operation
https://api.mongodb.com/python/current/api/gridfs/index.html


for wrap file reference flask-pymongo send_file function
https://github.com/dcrosta/flask-pymongo/blob/master/flask_pymongo/__init__.py

flask Response Object
https://flask.palletsprojects.com/en/1.1.x/api/#response-objects

flask make_response() function for customize the response
https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.make_response

WSGI Respond quick start doc
https://werkzeug.palletsprojects.com/en/1.0.x/quickstart/

Request & Respond object doc
https://werkzeug.palletsprojects.com/en/1.0.x/wrappers/

HTTP conditional requests
https://developer.mozilla.org/en-US/docs/Web/HTTP/Conditional_requests

Create Custom Responses in Flask
https://www.youtube.com/watch?v=gh2HPmpFjn8

Build a Python CRUD REST API in Flask and MongoDB Using Flask-PyMongo Library
https://www.youtube.com/watch?v=HyDACIfdPs0

customize HTTP Response
https://www.youtube.com/watch?v=gh2HPmpFjn8

url_for
https://www.youtube.com/watch?v=ikGWk8L3aWw

Link to Flask static files with url_for
https://stackoverflow.com/questions/16351826/link-to-flask-static-files-with-url-for

Create dynamic URLs in Flask with url_for()
https://stackoverflow.com/questions/7478366/create-dynamic-urls-in-flask-with-url-for


******////////--------create login Blueprints and Views¶
https://flask.palletsprojects.com/en/1.1.x/tutorial/views/

get request host
        # host = request.host_url
        # print(host)

g variable vs session
https://www.reddit.com/r/learnpython/comments/2x4754/flask_should_i_use_the_g_variable_system_of/


Creating a User Login System Using Python, Flask and MongoDB
https://www.youtube.com/watch?v=vVx1737auSE&list=WL&index=76&t=110s

blog update endpoint and template
https://flask.palletsprojects.com/en/1.1.x/tutorial/blog/

{% if g.user['id'] == post['author_id'] %}
    <a class="action" href="{{ url_for('blog.update', id=post['id']) }}">Edit</a>
{% endif %}


http hidden form option
https://stackoverflow.com/questions/45124603/how-to-tell-which-html-form-was-submitted-to-flask



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
https://blog.csdn.net/mianbaoli xiang/article/details/90515139?utm_medium=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-2.nonecase&depth_1-utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-2.nonecase


How to take a subset of a dictionary in Python
https://kite.com/python/answers/how-to-take-a-subset-of-a-dictionary-in-python

# to drop all the data in the databases including files and user info
# mongo.db.drop_collection("user")
# mongo.db.drop_collection("fs.chunks")
# mongo.db.drop_collection("fs.files")

"""



