from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Importing database helper functions
from db import query_db, insert_db, init_db_command

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = query_db('SELECT * FROM users WHERE email = ?', (email,), one=True)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('profile'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if 'user_id' not in session:
        flash("You need to login to view messages.")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Handle sending a new message
        to_user = request.form.get('to_user')
        message = request.form.get('message')
        from_user = session['user_id']
        
        if not to_user or not message:
            flash("All fields are required to send a message.")
            return redirect(url_for('messages'))
        
        # Insert the new message into the database
        insert_db('INSERT INTO messages (fromUserId, toUserId, message) VALUES (?, ?, ?)', (from_user, to_user, message))
        flash('Message sent successfully!')
    
    # Retrieve all messages to and from the logged-in user
    messages_received = query_db('SELECT m.*, u.name as from_user_name FROM messages m JOIN users u ON m.fromUserId = u.id WHERE m.toUserId = ?', [session['user_id']])
    messages_sent = query_db('SELECT m.*, u.name as to_user_name FROM messages m JOIN users u ON m.toUserId = u.id WHERE m.fromUserId = ?', [session['user_id']])
    
    return render_template('messages.html', messages_received=messages_received, messages_sent=messages_sent)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        dob = request.form['dob']

        try:
            insert_db('INSERT INTO users (name, email, password, dob) VALUES (?, ?, ?, ?)', (name, email, password, dob))
            flash('Account created successfully! Please log in.')
        except sqlite3.IntegrityError:
            flash('Email already registered')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = query_db('SELECT * FROM users WHERE id = ?', [session['user_id']], one=True)
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        init_db_command()
    app.run(debug=True)
