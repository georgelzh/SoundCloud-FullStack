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


app = Flask(__name__)   #static_folder="music"


# config
mongo = PyMongo(app, uri="mongodb://localhost:27017/soundcloud")
storage_bucket = GridFSBucket(mongo.db)
storage = GridFS(mongo.db, "fs")

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = mongo.db.users.fine_one({"_id": ObjectId(user_id)})


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


@app.route('/')
def return_index():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        if mongo.db.users.find_one({"username": username}) is not None:
            error = "username already exists, please change another one."
            flash(error)
            return render_template("register.html")
        else:
            empty_tracks = {}
            mongo.db.users.insert_one({"username": username, "password": generate_password_hash(password),\
                                            "email": email, "tracks": empty_tracks})
            return redirect('login')
    elif request.method == "GET":
        return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']        
        user = mongo.db.users.find_one({"username": username})
        if user is None:
            error = "user does not exists"
            flash(error)
            return render_template("login.html")
        if check_password_hash(user['password'], password) == False:
            error = "incorrect password, please try again"
            flash(error)
            return render_template("login.html")
        else:
            session.clear()
            session['user_id'] = user['_id']
            return redirect(url_for('/{0}'.format(username)))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('/'))

@app.route('/music/<music_file_id>')
# last TODO: need to protect this folder make sure there's login needed
def return_music(music_file_id, cache_for=31536000):
    try:
        # package the response
        audio_file_obj = storage.get(ObjectId(music_file_id))
        # audio_file_obj = storage.get_version("better_now.mp3") # this also works, but i'd like to send via objectID
        data = wrap_file(request.environ, audio_file_obj, buffer_size=1024 * 255) # wrap it for response class set up
        resp = current_app.response_class(data, mimetype=audio_file_obj.content_type , direct_passthrough=True) # flask.Response class
        resp.content_length = audio_file_obj.length
        resp.last_modified = audio_file_obj.upload_date
        resp.set_etag(audio_file_obj.md5)
        resp.cache_control.max_age = cache_for  # time the client is able to cache 
        resp.cache_control.public = True
        resp.make_conditional(request) # what does this line do?
        #print(request) # <Request 'http://127.0.0.1:5000/music/sd' [GET]>
        return resp
        # return mongo.send_file("better_now.mp3")
    except Exception as e:
        # return 404 if music not found
        return e, 404


@app.route('/<string:username>/')
def show_profile(username):
    user = mongo.db.users.find_one({"username": username})
    if user == None:
        return redirect('/')
    else:
        # retrieve all tracks from the artist
        sound_track_list = []
        for track_title, file_ids in user['tracks'].items():
            # when the user owns exactly one soundtrack for a name
            if type(file_ids) == ObjectId:
                sound_track_list.append([track_title, file_ids])
            # when use owns more than one soundtrack that shares the same track name
            else:
                for file_id in file_ids:
                    sound_track_list.append([track_title, file_id])
        # display track_list via jinja
        host = request.host_url
        print(host)
        return render_template("test.html", username = user['username'], host=host, sound_track_list = sound_track_list)
        # return "ok"
        # upload music how to render lots of music?


# for music retrieval via the html jinja 
# wonder if there is a way to direct the user from the html to my endpoint?
# if yes, then this endpoint will not be needed
@app.route('/<string:username>/<string:music_file_obj_id>')
def redirect_to_music_file(username, music_file_obj_id):
    if username != None and music_file_obj_id != None:
        return redirect("/music/" + music_file_obj_id)


@app.route('/upload', methods = ['GET'])
def load_upload_page():
        # verify user then enable the upload function, otherwise redirect it to home
        # user = mongo.db.users.find_one({"username": username})
        # if user == None:
        #     return redirect('/')
    return render_template("upload.html")


@app.route('/upload', methods=['POST'])
def upload_file():
    # verify user
    if request.method == "POST":
        music_file = "failed to upload"
        track_titile = request.form.get("track title")
        username = request.form.get("username")

        # print(request.files)    #ImmutableMultiDict([('music_file', <FileStorage: 'better_now.mp3' ('audio/mpeg')>)])
        if "music_file" in request.files:
            user_obj = mongo.db.users.find_one({"username": username})
            # dict {'_id': ObjectId('5eff9054e0e083d4b506fde0'), 'name': 'george', 'tracks': {}}
            if user_obj == None:
                return "failed to upload, username is not found", 404
            else:
                # upload
                music_file = request.files['music_file']
                music_file_obj_id = mongo.save_file(filename=track_titile, 
                                    fileobj=music_file, artist = username, user_id = user_obj["_id"])
                
                # update user tracks in mongo
                tracks = user_obj['tracks']
                
                # this code below solves the problem of user uploading the same music_file
                # insert the new song into hashtable/"tracks"
                # if the song name has already exists in the tracks,
                # then convert it into a list and append the ObjectId to the new list
                if track_titile in tracks:
                    tracks[track_titile] = list(tracks[track_titile])
                    tracks[track_titile].append(music_file_obj_id)

                    # update tracks data in the database
                    tracks[track_titile] = music_file_obj_id
                    mongo.db.users.find_one_and_update(
                        {"username": "george"},
                        {"$set": {
                            "tracks": tracks
                        }},
                        upsert = True)
                else:
                    tracks[track_titile] = music_file_obj_id
                    mongo.db.users.find_one_and_update(
                        {"username": "george"},
                        {"$set": {
                            "tracks": tracks
                        }})

        if music_file == "failed to upload":
            return music_file, 400
        else:
            return "successfully upload track '{0}' for {1}!".format(track_titile, username)

"""
Require Authentication in Other Views¶
Creating, editing, and deleting blog posts will require a user to be logged in. 
A decorator can be used to check this for each view it’s applied to.

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


This decorator returns a new view function that wraps the original view it’s applied to. 
The new function checks if a user is loaded and redirects to the login page otherwise. 
If a user is loaded the original view is called and continues normally. You’ll use this 
decorator when writing the blog views.
"""
if __name__ == "__main__":
    # for testing purpose, we gonna drop all collections before the program starts
    # mongo.db.drop_collection("user")
    # mongo.db.drop_collection("fs.chunks")
    # mongo.db.drop_collection("fs.files")

    app.run(host="0.0.0.0", debug=True)




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


"""





