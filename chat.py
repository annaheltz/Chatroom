import json
import os
from flask import Flask, request, session, jsonify, redirect, url_for, abort, render_template, flash
from models import db, User, Chatroom, Chat
app = Flask(__name__)

if __name__ == "__main__":
	app.run()


# Load default config and override config from an environment variable
app.config.update(dict(
	DEBUG=True,
	SECRET_KEY='development key',
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'chat.db')
))
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

db.init_app(app)

@app.cli.command('initdb')
def initdb_command():
	"""Creates the database tables."""
	db.drop_all()
	db.create_all()
	print('Intialized Database')

@app.route('/')
def login():#automatically go to entrypage
	return render_template('entryPage.html')

#login/createaccount

@app.route('/entryPage<what>')
def entryPageMethods(what):
	if what == "login": #go to login
		return render_template('loginUser.html')
	else: #what = signup, go to create account
		return render_template('createAccount.html')

@app.route('/createAccount<what>', methods = ["GET", "POST"])
def createAccountFunction(what): 
	if what == "create": #create account and add to database
	
		username = request.form['Username']
		password = request.form['Password']

		user = User(username, password)

		db.session.add(user)
		db.session.commit()

		session['user_id'] = user.id
		chatrooms = Chatroom.query.all()

		return render_template('loggedInUser.html', chatrooms = chatrooms, user = user.id)

	else: #return to entry page
		return render_template('entryPage.html')


@app.route('/loginUser<what>', methods = ["GET", "POST"])
def loginFunction(what):
	if what == "login":
		username = request.form['Username']
		password = request.form['Password']
		chatrooms = Chatroom.query.all()
		user = User.query.filter_by(username=request.form['Username']).first()

		if user is None:  #user name is not in database
			return render_template('loginUser.html')

		elif password != user.password: #incorrect password
			return render_template('loginUser.html')

		else: #correct user and pass
			flash('A user was logged in')
			session['user_id'] = user.id
			return render_template('loggedInUser.html', chatrooms = chatrooms, user = user.id)

	else: #return to entry page
		return render_template('entryPage.html')


#chatroom creation and stuff

@app.route('/createChatroom<what>', methods = ['GET', 'POST'])
def createRoomFunction(what):

	if what == 'create': #add a new room to the database
		name = request.form['Roomname']
		chatroom = Chatroom(name, session['user_id'])
		#room = db.query.filter_by(name = name)
		#if room is None:
			#dont add, else add
		db.session.add(chatroom)
		db.session.commit()
		chatrooms = Chatroom.query.all()
		return render_template('loggedInUser.html', chatrooms = chatrooms, user = session['user_id'])

	else:#logout
		return render_template('entryPage.html')

@app.route('/loggedInUser<what><chatroom_id>', methods=['GET', 'POST'])
def loggedInFunction(what, chatroom_id): 

	if what == 'create': #go to create room
		return render_template('createChatroom.html')

	elif what == 'delete': #delete a room from the database
		session['deletedRoom'] = chatroom_id
		deleteRoom = Chatroom.query.get_or_404(chatroom_id)
		db.session.delete(deleteRoom)
		db.session.commit()
		chatrooms = Chatroom.query.all()
		what = ""
		return render_template('loggedInUser.html', chatrooms = chatrooms, user = session['user_id'], what = "")

	elif what == 'join': #join a room
		session['chatroom_id'] = chatroom_id
		myRoomChats = Chatroom.query.filter_by(id = session['chatroom_id']).first().myChats.all()
		name = Chatroom.query.filter_by(id = session['chatroom_id']).first().name
		return render_template('chatroom.html', oldChats = myRoomChats, name = name, chatroom_id = session['chatroom_id'])

	elif what =="logout": #go to entry page
		return render_template('entryPage.html')

	else: #this was trying to fix an error but it didnt fix it lol
		chatrooms = Chatroom.query.all()
		what = ""
		return render_template('loggedInUser.html', chatrooms = chatrooms, user = session['user_id'])


@app.route('/chatroom<what>', methods=['GET', 'POST'])
def chatroomFunction(what):
	if what == "logout": #go to entry page
		return render_template('entryPage.html')

	elif what =="delete": #chat room was deleted so we need to go back to loggedInUser
		chatrooms = Chatroom.query.all()
		return render_template('loggedInUser.html', chatrooms = chatrooms, user = session['user_id'])

	else: #leave chat room
		chatrooms = Chatroom.query.all()
		return render_template('loggedInUser.html', chatrooms = chatrooms, user = session['user_id'])


#this fetches a chat that is entered on the form
@app.route("/new_chat", methods=["POST"])
def add():
	chat = Chat(request.form["chat"], session['chatroom_id'])
	db.session.add(chat)
	db.session.commit()

	whatRoom = Chatroom.query.filter_by(id = session['chatroom_id']).first()
	whatRoom.myChats.append(chat)
	db.session.commit()
	
	newChat = []
	newChat.append(chat.message)
	return json.dumps(newChat)

#need to have it only fetch messages from the room that they are in 
#this fetches to see if someone else typed a new message
@app.route("/chats")
def get_items():
	if room_exists(session['chatroom_id']):
		whatRoom = Chatroom.query.filter_by(id = session['chatroom_id']).first()
		allChats = []
		for chat in whatRoom.myChats:
			allChats.append(chat.message)
		db.session.commit()
		return json.dumps(allChats), 202	
	else: 
		empty = []
		return json.dumps(empty), 404

#this function will check if they are in a room that has been deleted, if they are we need to tell them that their room has been deleted
def room_exists(chatRoom_id):
    room = Chatroom.query.filter_by(id=chatRoom_id).first()
    if room:
        return True
    else:
        return False
