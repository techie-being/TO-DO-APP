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