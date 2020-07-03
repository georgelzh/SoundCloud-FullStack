import os
from flask import Flask, Response, send_file,\
                        send_from_directory, stream_with_context, \
                        render_template

app = Flask(__name__)

"""
In order for clients to know that partial content is supported by the 
server, the server needs to add the following header to the response —
"Accept-Ranges": "bytes" This implies that server is capable of serving 
partial content, specified as a range of bytes. To add this header to 
responses, one can use the following decoration —
"""

app_dir_path = app.instance_path
app.config["music"] = os.path.join(app_dir_path, "music")

@app.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response

@app.route('/music/<music_name>')
def return_music(music_name):
    return send_file("./music/{0}".format(music_name)) # "./music/better_now.mp3" 

@app.route('/')
def hello():
    return render_template("index.html")


@app.route('/song')
def music_player(): 
    #TODO support how to support partly serving
    #TODO: to render music with partly serving
    return render_template("test.html", name = "george", song = "../music/better_now.mp3")

if __name__ == "__main__":
    # for testing purpose, we gonna drop the table,

    app.run(host="0.0.0.0", port=5421)





"""
///////////////return static file stored on the server

# setup the music folder directory, path is absolute path

@app.route('/music/<music_name>')
def return_music(music_name):
    return send_file("./music/{0}".format(name)) # "./music/better_now.mp3" 
    # here it will retrieve data from the folder, TODO: handle non-exist file



///////////stream data and pass down as mp3 audio to the web method
///////////return a song by the response object, passing down the audio data.

TODO: try just return the whole music and see what happens
TODO: find a way to return this to a jinja render if possible


read_byte_range = 1024

@app.route('/song')
def music_player():
    @stream_with_context
    def generate():
        with open("better_now.mp3", "rb") as fmp3:
            data = fmp3.read(read_byte_range)
            while data:
                yield data
                data = fmp3.read(read_byte_range)
    # return render_template("test.html", name = "george", song = generate())
    # return render_template("test.html", song = generate())
    # return render_template("test.html", name = "george", song = Response(generate(), mimetype = "audio/mpeg"))
    return Response(generate(), mimetype = "audio/mpeg")
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

mimetype
https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
https://www.iana.org/assignments/media-types/media-types.xhtml


Uploading/Streaming Audio using NodeJS + Express + MongoDB/GridFS
https://medium.com/@richard534/uploading-streaming-audio-using-nodejs-express-mongodb-gridfs-b031a0bcb20f


Audio liveStream with Python & Flask
https://stackoverflow.com/questions/51079338/audio-livestreaming-with-python-flask


HTTP 206(Partial Content) for Flask/Python
https://blog.asgaard.co.uk/2012/08/03/http-206-partial-content-for-flask-python

Sending files with Flask | Learning Flask - with  flask.send_from_directory function
customize app.config['directory_name'] then use it
https://pythonise.com/series/learning-flask/sending-files-with-flask


*****save and retrieve files in a mongodb with flask-python web app****
https://www.youtube.com/watch?v=DsgAuceHha4

Other people's Application:
Open source, web-based music player for the cloud.
https://github.com/jakubroztocil/cloudtunes

souncCloud architecture development history
https://developers.soundcloud.com/blog/evolution-of-soundclouds-architecture

more Flask Tutorial:
https://pythonprogramming.net/flask-send-file-tutorial/

"""

