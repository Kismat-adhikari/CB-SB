from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_socketio import SocketIO, join_room, leave_room, send, emit
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'my-secret-key-here'  # Change this to a secure secret key

# Initialize Flask-SocketIO
socketio = SocketIO(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Ensure the instance folder exists
os.makedirs('instance', exist_ok=True)
USER_FILE = 'instance/user.txt'
MESSAGE_FILE = 'instance/messages.txt'
FOLLOW_FILE = 'instance/follows.txt'
NOTIFICATION_FILE = 'instance/notifications.txt'

# File initialization functions
def init_user_file():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, 'w') as f:
            pass

def init_message_file():
    if not os.path.exists(MESSAGE_FILE):
        with open(MESSAGE_FILE, 'w') as f:
            pass

def init_follow_file():
    if not os.path.exists(FOLLOW_FILE):
        with open(FOLLOW_FILE, 'w') as f:
            pass

def init_notification_file():
    if not os.path.exists(NOTIFICATION_FILE):
        with open(NOTIFICATION_FILE, 'w') as f:
            pass

# User management functions
def get_users():
    try:
        with open(USER_FILE, 'r') as f:
            return [line.strip().split(',') for line in f.readlines()]
    except FileNotFoundError:
        return []

def save_user(user_data):
    with open(USER_FILE, 'a') as f:
        f.write(','.join(user_data) + '\n')

# Message management functions
def get_messages(room):
    try:
        with open(MESSAGE_FILE, 'r') as f:
            return [line.strip().split('|') for line in f.readlines() if line.startswith(room)]
    except FileNotFoundError:
        return []

def save_message(room, sender, message):
    with open(MESSAGE_FILE, 'a') as f:
        f.write(f'{room}|{sender}|{message}\n')

# Follow management functions
def get_followers(username):
    try:
        with open(FOLLOW_FILE, 'r') as f:
            return [line.strip().split(',')[0] for line in f.readlines() if line.strip().split(',')[1] == username]
    except FileNotFoundError:
        return []

def get_following(username):
    try:
        with open(FOLLOW_FILE, 'r') as f:
            return [line.strip().split(',')[1] for line in f.readlines() if line.strip().split(',')[0] == username]
    except FileNotFoundError:
        return []

def is_following(follower, following):
    try:
        with open(FOLLOW_FILE, 'r') as f:
            return any(line.strip() == f"{follower},{following}" for line in f.readlines())
    except FileNotFoundError:
        return False

def add_follower(follower, following):
    if not is_following(follower, following):
        with open(FOLLOW_FILE, 'a') as f:
            f.write(f"{follower},{following}\n")
        return True
    return False

def remove_follower(follower, following):
    try:
        with open(FOLLOW_FILE, 'r') as f:
            lines = f.readlines()
        
        with open(FOLLOW_FILE, 'w') as f:
            for line in lines:
                if line.strip() != f"{follower},{following}":
                    f.write(line)
        return True
    except FileNotFoundError:
        return False

# Updated Notification functions
def get_notifications(username, unread_only=False):
    try:
        with open(NOTIFICATION_FILE, 'r') as f:
            notifications = [line.strip().split('|') for line in f.readlines() 
                           if line.strip().split('|')[0] == username]
            if unread_only:
                return [notif for notif in notifications if len(notif) > 3 and notif[3] == 'unread']
            return notifications
    except FileNotFoundError:
        return []

def save_notification(username, message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(NOTIFICATION_FILE, 'a') as f:
        f.write(f"{username}|{message}|{timestamp}|unread\n")

def mark_notifications_as_read(username):
    try:
        with open(NOTIFICATION_FILE, 'r') as f:
            lines = f.readlines()
        
        with open(NOTIFICATION_FILE, 'w') as f:
            for line in lines:
                parts = line.strip().split('|')
                if parts[0] == username and len(parts) > 3 and parts[3] == 'unread':
                    # Replace unread with read
                    f.write(f"{parts[0]}|{parts[1]}|{parts[2]}|read\n")
                else:
                    f.write(line)
        return True
    except FileNotFoundError:
        return False

# Routes
@app.route('/')
def index():
    if 'email' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        display_name = request.form['display_name']
        cook_type = request.form['cook_type']
        age = request.form['age']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        users = get_users()

        if any(user[1] == username for user in users):
            flash('Username already exists')
            return redirect(url_for('signup'))

        if any(user[6] == email for user in users):
            flash('Email already exists')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)
        user_data = [full_name, username, display_name, cook_type, age, phone, email, hashed_password]
        save_user(user_data)

        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form['email_or_username']
        password = request.form['password']

        users = get_users()
        user = next((user for user in users if user[6] == login_input or user[1] == login_input), None)

        if user and check_password_hash(user[7], password):
            session['email'] = user[6]
            session['username'] = user[1]
            flash('Login successful!')
            return redirect(url_for('profile'))

        flash('Incorrect email/username or password')
        return redirect(url_for('login'))

    return render_template('login.html')

# Updated notification routes
@app.route('/notifications')
def notifications():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    notifications = get_notifications(username)
    
    # Mark all notifications as read
    mark_notifications_as_read(username)
    
    # Format notifications for the template
    formatted_notifications = []
    for notification in notifications:
        formatted_notifications.append({
            'message': notification[1],
            'timestamp': notification[2] if len(notification) > 2 else None,
            'read': len(notification) > 3 and notification[3] == 'read'
        })
    
    return render_template('notifications.html', notifications=formatted_notifications)

@app.route('/api/notifications')
def get_user_notifications():
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    username = session['username']
    unread_notifications = get_notifications(username, unread_only=True)
    
    formatted_notifications = []
    for notification in unread_notifications:
        formatted_notifications.append({
            'message': notification[1],
            'timestamp': notification[2] if len(notification) > 2 else None
        })
    
    return jsonify({
        'success': True,
        'notifications': formatted_notifications
    })

@app.route('/profile')
@app.route('/profile/<username>')
def profile(username=None):
    if 'email' not in session:
        return redirect(url_for('login'))

    users = get_users()

    if username is None:
        user = next((user for user in users if user[6] == session['email']), None)
        is_own_profile = True
    else:
        user = next((user for user in users if user[1] == username), None)
        if user:
            is_own_profile = (user[6] == session['email'])
        else:
            return "User not found", 404

    if user:
        followers = get_followers(user[1])
        following = get_following(user[1])
        is_following_user = is_following(session['username'], user[1]) if not is_own_profile else False
        
        return render_template('profile.html', 
                             user=user, 
                             is_own_profile=is_own_profile,
                             followers_count=len(followers),
                             following_count=len(following),
                             is_following=is_following_user)

    return "User not found", 404

@app.route('/follow/<username>', methods=['POST'])
def follow_user(username):
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})

    current_user = session['username']
    
    if current_user == username:
        return jsonify({'success': False, 'message': 'You cannot follow yourself'})

    if add_follower(current_user, username):
        followers_count = len(get_followers(username))
        following_count = len(get_following(username))
        
        # Add notification
        notification_message = f"{current_user} started following you"
        save_notification(username, notification_message)
        
        # Emit notification update
        socketio.emit('notification_update', {
            'username': username,
            'message': notification_message
        }, broadcast=True)
        
        # Emit follow update
        socketio.emit('follow_update', {
            'follower': current_user,
            'following': username,
            'action': 'follow',
            'followers_count': followers_count,
            'following_count': following_count
        }, broadcast=True)
        
        return jsonify({
            'success': True,
            'message': f'You are now following {username}',
            'followers_count': followers_count,
            'following_count': following_count
        })
    
    return jsonify({'success': False, 'message': 'Already following'})

@app.route('/unfollow/<username>', methods=['POST'])
def unfollow_user(username):
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})

    current_user = session['username']
    
    if remove_follower(current_user, username):
        followers_count = len(get_followers(username))
        following_count = len(get_following(username))
        
        socketio.emit('follow_update', {
            'follower': current_user,
            'following': username,
            'action': 'unfollow',
            'followers_count': followers_count,
            'following_count': following_count
        }, broadcast=True)
        
        return jsonify({
            'success': True,
            'message': f'You have unfollowed {username}',
            'followers_count': followers_count,
            'following_count': following_count
        })
    
    return jsonify({'success': False, 'message': 'Not following'})

@app.route('/message')
def message_list():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    current_username = session['username']
    users_with_messages = {}
    
    try:
        with open(MESSAGE_FILE, 'r') as f:
            for line in f:
                room, sender, message = line.strip().split('|')
                user1, user2 = room.split('_')
                
                other_user = user2 if current_username == user1 else user1
                if current_username in (user1, user2):
                    users_with_messages[other_user] = {
                        'username': other_user,
                        'last_message': message
                    }
    except FileNotFoundError:
        pass
    
    users = list(users_with_messages.values())
    return render_template('message.html', users=users)

@app.route('/message/<username>', methods=['GET'])
def message_user(username):
    if 'email' not in session:
        return redirect(url_for('login'))

    current_username = session['username']
    room = f"{current_username}_{username}" if current_username < username else f"{username}_{current_username}"
    messages = get_messages(room)

    return render_template('chat.html', username=username, room=room, messages=messages)

@app.route('/get_follow_counts/<username>')
def get_follow_counts(username):
    followers = get_followers(username)
    following = get_following(username)
    return jsonify({
        'followers_count': len(followers),
        'following_count': len(following)
    })

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

# SocketIO Events
@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(f"{username} has left the room.", to=room)

@socketio.on('send_message')
def handle_message(data):
    room = data['room']
    message = data['message']
    sender = session['username']
    save_message(room, sender, message)
    send(f"{sender}: {message}", to=room)

if __name__ == '__main__':
    init_user_file()
    init_message_file()
    init_follow_file()
    init_notification_file()
    socketio.run(app, debug=True)