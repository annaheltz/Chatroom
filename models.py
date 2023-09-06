from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, column

# note this should only be created once per project
# to define models in multiple files, put this in one file, and import db into each model, as we import it in flaskr.py
db = SQLAlchemy()

#all chat refs to a chatroom
chats = db.Table('chats', 
    db.Column('chatroom_id', db.Integer, db.ForeignKey('chatroom.id')),
    db.Column('chat_id', db.Integer, db.ForeignKey('chat.id'))
)


class User(db.Model): 
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.Text, nullable = False)
    password = db.Column(db.Text, nullable = False)

    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def __repr__(self):
        return '<user{}>'.format(self.id)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    message = db.Column(db.Text, nullable = False)
    room_id = db.Column(db.Integer, db.ForeignKey('chatroom.id'))

    def __init__(self, message, room_id):
        self.message = message
        self.room_id = room_id

    def __repr__(self):
        return '<chat{}>'.format(self.id)

class Chatroom(db.Model): 
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Text, nullable = False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    
    #ref to all of chat room chats
    myChats = db.relationship('Chat', secondary='chats', primaryjoin='Chatroom.id==chats.c.chatroom_id', secondaryjoin='Chat.id==chats.c.chat_id', backref=db.backref('room', lazy='dynamic'),lazy = 'dynamic')

    def __init__(self, name, creator_id):
        self.name = name
        self.creator_id = creator_id

        def __repr__(self):
            return '<chatroom{}>'.format(self.id)
