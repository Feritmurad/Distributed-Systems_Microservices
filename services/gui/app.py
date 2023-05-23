from flask import Flask, render_template, redirect, request, url_for, Response
import requests
import json

app = Flask(__name__)


# The Username & Password of the currently logged-in User
username = None
password = None

session_data = dict()


def save_to_session(key, value):
    session_data[key] = value


def load_from_session(key):
    return session_data.pop(key) if key in session_data else None  # Pop to ensure that it is only used once


@app.route("/")
def feed():
    # ================================
    # FEATURE 9 (feed)
    #
    # Get the feed of the last N activities of your friends.
    # ================================

    global username

    N = 10

    feed = []
    feed_playlist = []
    feed_friends = []
    if username is not None:
        try:
            responseplaylists = requests.get("http://playlists:5000/playlists/activities/?username=" + username)
            if responseplaylists.status_code == 200:
                temp_list = responseplaylists.json()
                feed_playlist = temp_list 
        except requests.exceptions.ConnectionError as e:
            # Handle the connection error when 'friends' host cannot be reached
            print("Error: Connection to 'playlists' host failed.",flush=True)
        try:
            responsefriends = requests.get("http://friends:5000/friends/activities/?username=" + username)
            if responsefriends.status_code == 200:
                temp_list = responsefriends.json()
                feed_friends = temp_list
        except requests.exceptions.ConnectionError as e:
            # Handle the connection error when 'friends' host cannot be reached
            print("Error: Connection to 'friends' host failed.",flush=True)
            
        temp_list = feed_friends + feed_playlist
        feed = sorted(temp_list, key=lambda x: x[1], reverse=False)
        feed = feed[:N]
    else:
        feed = []

    print(feed,flush=True)
    return render_template('feed.html', username=username, password=password, feed=feed)


@app.route("/catalogue")
def catalogue():
    songs = requests.get("http://songs:5000/songs").json()

    return render_template('catalogue.html', username=username, password=password, songs=songs)


@app.route("/login")
def login_page():

    success = load_from_session('success')
    return render_template('login.html', username=username, password=password, success=success)


@app.route("/login", methods=['POST'])
def actual_login():
    req_username, req_password = request.form['username'], request.form['password']

    # ================================
    # FEATURE 2 (login)
    #
    # send the username and password to the microservice
    # microservice returns True if correct combination, False if otherwise.
    # Also pay attention to the status code returned by the microservice.
    # ================================
    try:
        response = requests.post("http://users:5000/users/login/?username=" + req_username + "&password=" + req_password)

        if response.status_code == 200 : success = response.json()  # TODO: call
    except requests.exceptions.ConnectionError as e:
        # Handle the connection error when 'friends' host cannot be reached
        print("Error: Connection to 'users' host failed.",flush=True)

    save_to_session('success', success)
    if success:
        global username, password

        username = req_username
        password = req_password

    return redirect('/login')


@app.route("/register")
def register_page():
    success = load_from_session('success')
    return render_template('register.html', username=username, password=password, success=success)


@app.route("/register", methods=['POST'])
def actual_register():

    req_username, req_password = request.form['username'], request.form['password']

    # ================================
    # FEATURE 1 (register)
    #
    # send the username and password to the microservice
    # microservice returns True if registration is succesful, False if otherwise.
    #
    # Registration is successful if a user with the same username doesn't exist yet.
    # ===============================+

    try:
        response = requests.post("http://users:5000/users/register/?username=" + req_username + "&password=" + req_password)
        
        if response.status_code == 200 : success = response.json()  # TODO: call
    except requests.exceptions.ConnectionError as e:
            # Handle the connection error when 'friends' host cannot be reached
            print("Error: Connection to 'users' host failed.",flush=True)
    
    save_to_session('success', success)

    if success:
        global username, password

        username = req_username
        password = req_password

    return redirect('/register')


@app.route("/friends")
def friends():
    success = load_from_session('success')

    global username

    # ================================
    # FEATURE 4
    #
    # Get a list of friends for the currently logged-in user
    # ================================
    

    friend_list = [] # TODO: call
    if username is not None:
        try:
            response = requests.get("http://friends:5000/friends/?username=" + username)
            if response.status_code == 200:
                temp_list = response.json()
                friend_list = [item for sublist in temp_list for item in sublist] # TODO: call
        except requests.exceptions.ConnectionError as e:
            # Handle the connection error when 'friends' host cannot be reached
            print("Error: Connection to 'friends' host failed.",flush=True)


       
    else:
        friend_list = []
    return render_template('friends.html', username=username, password=password, success=success, friend_list=friend_list)


@app.route("/add_friend", methods=['POST'])
def add_friend():

    # ==============================
    # FEATURE 3
    #
    # send the username of the current user and the username of the added friend to the microservice
    # microservice returns True if the friend request is successful (the friend exists & is not already friends), False if otherwise
    # ==============================

    global username
    req_username = request.form['username']
    try:
        response = requests.post("http://friends:5000/friends/add/?username1=" + username + "&username2=" + req_username)


        if response.status_code == 200 : success = response.json()  # TODO: call
        else:
            message = 'Failed to add friend'
            status = 400
            headers = {'Content-Type': 'text/plain'}
            return Response(message, status=status, headers=headers)
    except requests.exceptions.ConnectionError as e:
            # Handle the connection error when 'friends' host cannot be reached
            print("Error: Connection to 'friends' host failed.",flush=True)
    
    save_to_session('success', success)

    return redirect('/friends')


@app.route('/playlists')
def playlists():
    global username

    my_playlists = []
    shared_with_me = []

    if username is not None:
        # ================================
        # FEATURE
        #
        # Get all playlists you created and all playlist that are shared with you. (list of id, title pairs)
        # ================================
        try:
            response_my = requests.get("http://playlists:5000/playlists/?username=" + username)
            response_shared = requests.get("http://playlists:5000/playlists/shared/?username=" + username)

            my_playlists = []  # TODO: call
            shared_with_me = []  # TODO: call
            if response_my.status_code == 200 and response_shared.status_code == 200  :
                my_playlists = response_my.json()
                shared_with_me = response_shared.json()
            else:
                message = 'Failed to get playlist'
                status = 400
                headers = {'Content-Type': 'text/plain'}
                return Response(message, status=status, headers=headers)
        except requests.exceptions.ConnectionError as e:
            # Handle the connection error when 'friends' host cannot be reached
            print("Error: Connection to 'playlists' host failed.",flush=True)
        

        

    return render_template('playlists.html', username=username, password=password, my_playlists=my_playlists, shared_with_me=shared_with_me)


@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    # ================================
    # FEATURE 5
    #
    # Create a playlist by sending the owner and the title to the microservice.
    # ================================
    global username
    title = request.form['title']
    try:
        response = requests.post("http://playlists:5000/playlists/add/?title=" + title + "&username=" + username)


        if response.status_code == 200 : pass  # TODO: call
        else:
            message = 'Failed to add playlist'
            status = 400
            headers = {'Content-Type': 'text/plain'}
            return Response(message, status=status, headers=headers)
    
    except requests.exceptions.ConnectionError as e:
            # Handle the connection error when 'friends' host cannot be reached
            print("Error: Connection to 'playlists' host failed.",flush=True)

    return redirect('/playlists')


@app.route('/playlists/<int:playlist_id>')
def a_playlist(playlist_id):
    # ================================
    # FEATURE 7
    #
    # List all songs within a playlist
    # ================================
    try:
        response = requests.get("http://playlists:5000/playlists/songs/?playlist_id=" + str(playlist_id))
        
        songs = [] # TODO: call
        if response.status_code == 200:
                temp_list = response.json()
                print(temp_list,flush = True)
                songs = [(x[0], x[1]) for x in temp_list] # TODO: call
                print(songs,flush = True)

        else:
            message = 'Failed to get songs'
            status = 400
            headers = {'Content-Type': 'text/plain'}
            return Response(message, status=status, headers=headers)
    except requests.exceptions.ConnectionError as e:
            # Handle the connection error when 'friends' host cannot be reached
            print("Error: Connection to 'playlists' host failed.",flush=True)


    return render_template('a_playlist.html', username=username, password=password, songs=songs, playlist_id=playlist_id)


@app.route('/add_song_to/<int:playlist_id>', methods=["POST"])
def add_song_to_playlist(playlist_id):
    # ================================
    # FEATURE 6
    #
    # Add a song (represented by a title & artist) to a playlist (represented by an id)
    # ================================
    title, artist = request.form['title'], request.form['artist']
    global username

    try:
        response = requests.post("http://playlists:5000/playlists/add_song/?playlist_id=" + str(playlist_id) + "&title=" + title + "&artist=" + artist + "&username=" + username)

        if response.status_code == 200 : success = response.json() 
        else:
            message = 'Failed to add song'
            status = 400
            headers = {'Content-Type': 'text/plain'}
            return Response(message, status=status, headers=headers)
    except requests.exceptions.ConnectionError as e:
            # Handle the connection error when 'friends' host cannot be reached
            print("Error: Connection to 'playlists' host failed.",flush=True)

    ######################################### TODO FIX ALWAYS 200 even when not pushed

    # TODO: call
    return redirect(f'/playlists/{playlist_id}')


@app.route('/invite_user_to/<int:playlist_id>', methods=["POST"])
def invite_user_to_playlist(playlist_id):
    # ================================
    # FEATURE 8
    #
    # Share a playlist (represented by an id) with a user.
    # ================================
    recipient = request.form['user']

    try:
        response = requests.post("http://playlists:5000/playlists/share/?playlist_id=" + str(playlist_id) + "&username=" + recipient)

        if response.status_code == 200 : success = response.json()  # TODO: call
        else:
            message = 'Failed to share playlist with ' + recipient
            status = 400
            headers = {'Content-Type': 'text/plain'}
            return Response(message, status=status, headers=headers)
    except requests.exceptions.ConnectionError as e:
            # Handle the connection error when 'friends' host cannot be reached
            print("Error: Connection to 'playlists' host failed.",flush=True)

    ######################################### TODO FIX ALWAYS 200 even when not pushed
    return redirect(f'/playlists/{playlist_id}')


@app.route("/logout")
def logout():
    global username, password

    username = None
    password = None
    return redirect('/')
