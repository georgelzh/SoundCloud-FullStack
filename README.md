# Intro - SoundCloud-FullStack
Inspired by music streaming website such as soundcloud and spotify.
This project is a Fullstack project. I intend to learn the full cycle
development of fullstack enginnering. At the same time, sharpen my 
python, flask, Rest API, Mongodb skills. 

“Learn_partial_content_static_file_stream.py”,  “Music folder”, “template/test.html” & “template/test2.html” are for particle content local(static) file streaming. I played with static streaming in the beginning. 
“Gridfs_usage_playground.py” is for me to learn mongoDB - gridfs. 

Files and folders mentioned above are not required for the project to run. But they can be helpful if you’d like to learn about static file streaming and gridfs.


# what is covered in this project?
Topics related:
front-end - Jinja & HTML/CSS

back-end - python & mongodb

file-storage: mongodb-gridfs

back-end driver - pymongo & flask-pymongo

http & cookies & responses


This project has function such as
1. index page
2. login/logout - with sessions and g.user(flask) / cookies | login logout
3. view your own and others' profiles and listen to soundtracks they uploaded | profile
4. upload & delete music track if the track belongs to you | upload
5. change email addr and password page | account page


# why did I choose mongodb
1. I just learnt mongodb a while ago, and I wanted to practice my mongodb skills.
2. mongodb is a great tools as a No-SQL database and its flexibility to expand and grow
as user base grows is a great features. 
3. Mongodb has exceptional capacity when it comes to scaling. Its built-in helper function
such as sharding, and replications are great.
4. I have just worked with JSON/Python-Dict type data for data management, this is also a 
great opportunity to practice more of json and python. 


## how to run?
1. You need to have your own mongodb server hosted. 
Then you change the configuration of the mongodb server inside main.py
then you are ready for the next step.

2. Go to the parent directory of "SoundCloud-FUllSTACK"
then open linux terminal or mac terminal enter:

export FLASK_APP = SoundCloud-FullSTACK
export FLASK_ENV=development
export FLASK_RUN_PORT=5000
export FLASK_RUN_HOST=0.0.0.0
flask run

# or 
export FLASK_APP = SoundCloud-FUllSTACK
export FLASK_ENV=development
flask run --host 0.0.0.0 --port 5000


# what's next?
1. UI can be a lot more beautiful for both PC and Mobiles
2. add user profile photo for user
3. add comment function
4. add follow/unfollow function
5. add search music function at index page
6. ... and a lot more other features could be built on

# reflection
1. I learnt a lot from this project.
I've also learnt that when I build a project, it's better to just look
one step ahead. And You can always move on to the next step. Don't overthink
how huge the project might be. It only slows your process down. just calm down
and relax when you are stressed. You might find better solution while relaxed.

2. There will be lots of things that you don't know or understand. However, as
you encounter those problems, you can always learn it and find ways to solve it.
Project Based Learning is really helpful. I realize that I can't learn everything
about a project and then to build a project. This process will just be really boring
and unproductive. And I will never learn everything about the world. I just have to learn
as I build. It's a better way to learn. 


3. Solve it indirectly is better than wasting time and having no clue. This doesn't mean
you can should solve everything lazily(unoptimized). However, if you really can't solve 
sth in a smart way at first even after trying, you should solve it indirectly(find ways
to work around it). you might find better solution as you go along later.
Sometimes I just realize that I suddenly understood things that I could not figure out
previously even though I've tried it. This is interesting. Sometimes, I will encounter 
problems that I thought that I can not solve it directly, I solved it indirectly and 
after building more of this project, I realize and found ways to actually solve it directly.
This is a quite interesting phenomenon. I guess we sometimes just can't solve a problem
immediately, however, maybe try to solve it indirectly and you might be able to come back 
and find better solution later. So don't get stuck on it and get frustrated, solve it and
move on. 

4. don't give up. Great things takes time to come to fruition. Give it time and be patient.
move forward step by step. It's okay to take rest and breaks. Don't be too harsh on yourself.
rest can be really helpful for you in the long run. so it's necessary. we are all human.


Stay Hungry, Stay Foolish - Steve Job

Author: Zhihong Li(zhihongli@bennington.edu)

Date: Jul 8th 2020
