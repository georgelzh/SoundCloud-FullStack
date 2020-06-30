from flask import Flask, Response

read_byte_range = 1024

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello"


@app.route('/song')
def music_player():
    def generate():
        with open("better_now.mp3", "rb") as fmp3:
            data = fmp3.read(read_byte_range)
            while data:
                yield data
                data = fmp3.read(read_byte_range)
    return Response(generate(), mimetype = "audio/mpeg")


if __name__ == "__main__":
    app.run()


"""
reference:

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


"""