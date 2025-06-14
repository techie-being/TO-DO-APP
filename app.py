from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'secret123'

def init_db():
    # Create tables if they don't exist
    with sqlite3.connect('todo.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                content TEXT NOT NULL,
                done INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')
    with sqlite3.connect('todo.db') as conn:
        tasks = conn.execute('SELECT * FROM tasks WHERE user_id=?', (session['user_id'],)).fetchall()
    return render_template('index.html', tasks=tasks)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect('todo.db') as conn:
            user = conn.execute('SELECT * FROM users WHERE email=? AND password=?', (email, password)).fetchone()

        if user:
            session['user_id'] = user[0]
            flash('Login successful!', 'success')
            return redirect('/')
        else:
            flash('Invalid credentials', 'error')
            return redirect('/login')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first = request.form['first_name']
        last = request.form['last_name']
        email = request.form['email']
        password = request.form['password']

        try:
            with sqlite3.connect('todo.db') as conn:
                conn.execute("INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
                             (first, last, email, password))
            flash("Registration successful! You can now login.", "success")
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash("Email already registered!", "error")
            return redirect('/register')

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully', 'success')
    return redirect('/login')

@app.route('/add', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect('/login')

    content = request.form['content']
    with sqlite3.connect('todo.db') as conn:
        conn.execute('INSERT INTO tasks (user_id, content) VALUES (?, ?)', (session['user_id'], content))
    return redirect('/')

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    if 'user_id' not in session:
        return redirect('/login')

    with sqlite3.connect('todo.db') as conn:
        conn.execute('DELETE FROM tasks WHERE id=? AND user_id=?', (task_id, session['user_id']))
    return redirect('/')



@app.route('/toggle/<int:task_id>')
def toggle_task(task_id):
    with sqlite3.connect('todo.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT done FROM tasks WHERE id=?', (task_id,))
        current_status = cur.fetchone()[0]
        new_status = 0 if current_status == 1 else 1
        cur.execute('UPDATE tasks SET done=? WHERE id=?', (new_status, task_id))
        conn.commit()
    return redirect('/')



@app.route('/initdb')
def manual_init():
    init_db()
    return "Database initialized!"


init_db()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))