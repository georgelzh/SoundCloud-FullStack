from pymongo import MongoClient
import gridfs 


# connect to db and fs
client = MongoClient()
db = client.test
fs = gridfs.GridFS(db)


# upload
a = fs.put(b"hello world")
# a == ObjectId('5efab5f4eccfc803a60c82dc')


# read
fs.get(a).read()
# b'hello world'
# get() returns a file-like object, so we get the file’s contents by calling read().


# add attributes to the file as keyword arguments
"""
In addition to putting a str as a GridFS file, we can also put any file-like object
(an object with a read() method). GridFS will handle reading the file in chunk-sized 
segments automatically. We can also add additional attributes to the file as keyword 
arguments:
"""

b = fs.put(fs.get(a), filename="foo", author = '5efab5f4eccfc803a60c82dc')
out = fs.get(b)
out.read()
# b'hello world'

# access to attributes
o.filename # 'foo'
o.author #'5efab5f4eccfc803a60c82dc'
o.upload_date




"""
reference: 

pymongo gridfs example
https://pymongo.readthedocs.io/en/stable/examples/gridfs.html

gridfs example with python
https://psabhay.com/posts/mongodb/mongodb-gridfs-using-python/

pymongo gridfs doc
https://pymongo.readthedocs.io/en/stable/api/gridfs/index.html

"""
