from flask import Flask, render_template, flash, redirect, url_for, request
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
import os, math, shutil, sqlite3, unicodedata, re, json, subprocess, shlex, time
import subprocess
from gevent.subprocess import Popen, DEVNULL, STDOUT
from threading import Timer
import sys
import spotipy
import spotipy.util as util
import webbrowser
from spotipy.oauth2 import SpotifyOAuth
import pprint as pprint

app = Flask(__name__)
app.config['SECRET_KEY'] = ('This is a secret key')
socketio = SocketIO(app)

basic_dir = '/home/chaseUbuntu/' #A basic directory
basedir = os.path.abspath(os.path.dirname(__file__)) #This directory
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class UserOne(db.Model):
    day = db.Column(db.String, primary_key = True)
    song = db.Column(db.String, nullable = False)
    name = db.Column(db.String, nullable = False)
    def __init__(self, day, song, name):
        self.day = day
        self.song = song
        self.name = name

class UserTwo(db.Model):
    day = db.Column(db.String, primary_key = True)
    song = db.Column(db.String, nullable = False)
    name = db.Column(db.String, nullable = False)
    def __init__(self, day, song, name):
        self.day = day
        self.song = song
        self.name = name

db.create_all()
db.session.commit()
#db.engine.execute()
#db.session.query(User).delete()

# db.session.add(UserOne("3", "Kevin"))
# db.session.add(UserTwo("3", "Bill"))
# db.session.query(UserOne)
# db.session.query(UserTwo)
db.session.commit()

global_name = None

def init_spotify():
    scope = "user-read-playback-state,user-modify-playback-state"
    username = 'azsxdc8'
    try:
        token = util.prompt_for_user_token(username, scope)
    except:
        os.remove(f".cache-{username}")
        token = util.prompt_for_user_token(username, scope)

    spotifyObject = spotipy.Spotify(auth=token)
    print("Verified!")

    #client_id='c7ec55a031484c48b6cf1232ceab4b26'
    #client_secret='702bbf9215be476f8f5154ce39c97ddc'

@app.route('/')
def begin():
    init_spotify()

    return redirect(url_for('login'))

@app.route('/login', methods = ['GET', 'POST'])
def login():

    if request.method == "POST":
        details = request.form;
        username = str(details['username'])
        password = str(details['password'])
        global_name = username
        if(username == "tom" or username == "chase" and password == "test"):
            return redirect(url_for('home', name = username))
    return render_template('login.html')

@app.route('/home', methods = ['GET', 'POST'])
def home():
    print(global_name)
    name = request.args['name']
    query = db.engine.execute("SELECT * from user_one")
    temp_list = []
    for val in query:
        temp = {'day' : val[0], "song" : val[1], "name" : val[2]}
        temp_list.append(temp)
    query = db.engine.execute("SELECT * from user_two")
    for val in query:
        temp = {'day' : val[0], "song" : val[1], "name" : val[2]}
        temp_list.append(temp)
    return render_template('home.html', name = name, vals = temp_list)

@app.route('/sockets', methods = ['GET', 'POST'])
def sockets():
    return render_template('sockets.html')


def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    if(global_name == 'chase'):
        db.session.add(UserOne(json['day'], json['song'], json['name']))
    else:
        db.session.add(UserTwo(json['day'], json['song'], json['name']))
    db.session.commit()

    socketio.emit('update table', json, callback=messageReceived)
    
if __name__ == '__main__':
    #app.run()
    socketio.run(app, host='0.0.0.0', port=5000, debug = True)