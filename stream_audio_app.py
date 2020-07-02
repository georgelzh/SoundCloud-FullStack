from flask import Flask, Response, send_file,\
                        send_from_directory, stream_with_context, \
                        render_template

read_byte_range = 1024

app = Flask(__name__)


"""
In order for clients to know that partial content is supported by the 
server, the server needs to add the following header to the response —
"Accept-Ranges": "bytes" This implies that server is capable of serving 
partial content, specified as a range of bytes. To add this header to 
responses, one can use the following decoration —
"""
app.config["music"] = '/home/zhihongli/Desktop/SoundCloud-FullStack/music'

@app.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response


@app.route('/music/<music_name>')
def return_music(music_name):
    # TODO
    # make sure the music beind quried exists.
    # otherwise, return nothing. or maybe 404 not found

    # use send_from_directory
    # return send_file("./music/{0}".format(name))
    return send_from_directory(app.config['music'], music_name, as_attachment=True)

@app.route('/')
def hello():
    return "Hello"



@app.route('/song')
def music_player(): 
    #TODO support how to support partly serving
    #TODO: to render music with partly serving
    return render_template("test.html", name = "george", song = "../music/better_now.mp3")


"""
return a song by the response object, passing down the audio data.

TODO: try just return the whole music and see what happens
TODO: find a way to return this to a jinja render if possible

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


if __name__ == "__main__":
    app.run()


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


save and retrieve files in a mongodb with flask-python
https://www.youtube.com/watch?v=DsgAuceHha4

Other people's Application:
Open source, web-based music player for the cloud.
https://github.com/jakubroztocil/cloudtunes

souncCloud architecture development history
https://developers.soundcloud.com/blog/evolution-of-soundclouds-architecture

"""