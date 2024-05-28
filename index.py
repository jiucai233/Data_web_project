from flask import Flask, jsonify, render_template,request
import sqlite3
import random

app = Flask(__name__)

def get_db():
    db = sqlite3.connect('user.db')
    return db

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/questionnaires/random')
def get_random_questionnaires():
    conn = get_db()
    cursor = conn.execute('SELECT * FROM survey')
    questionnaires = cursor.fetchall()
    random_questionnaires = random.sample(questionnaires, len(questionnaires))
    return jsonify(random_questionnaires)

@app.route('/api/questionnaires/ordered')
def get_ordered_questionnaires():
    conn = get_db()
    cursor = conn.execute('SELECT * FROM survey ORDER BY id ASC')
    ordered_questionnaires = cursor.fetchall()
    return jsonify(ordered_questionnaires)

@app.route('/questionnaire/<int:id>')
def questionnaire_detail(id):
    conn = get_db()
    cursor = conn.execute('SELECT * FROM questions WHERE survey_id = ?', (id,))
    questionnaire = cursor.fetchone()
    if questionnaire:
        return render_template('questionnaire_detail.html', questionnaire=questionnaire)
    else:
        return "Questionnaire not found", 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn=get_db()
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return render_template('login.html', message="Log in successfully!")
        else:
            return render_template('login.html', message="The username or password is incorrect!")
    else:
        return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        conn=get_db
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            conn.close()
            return render_template('signup.html', message="User name already exists, please select another user name!")
        else:
            if password == confirm_password:
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                conn.close()
                return render_template('signup.html', message="Registration was successful!")
            else:
                conn.close()
                return render_template('signup.html', message="The password and confirmation password do not match!")
        
    else:
        return render_template('signup.html')
    
if __name__ == '__main__':
    app.run(debug=True)
