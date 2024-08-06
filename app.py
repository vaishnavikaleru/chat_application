from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


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


