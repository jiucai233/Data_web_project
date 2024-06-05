from flask import Flask, jsonify, render_template,request,send_file,make_response, session, flash, redirect,url_for
import sqlite3
import random
import csv
import io

app = Flask(__name__)
app.secret_key = '1248higrpe9v'
db_path='user.db'


def get_db_connection():
    conn = sqlite3.connect('user.db')
    return conn

def get_survey():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM survey')
    survey = cursor.fetchall()
    conn.close()
    return survey


def get_db():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/questionnaires/random')
def get_random_questionnaires():
    conn = get_db()
    cursor = conn.execute('SELECT * FROM survey')
    questionnaires = cursor.fetchall()
    random_questionnaires = random.sample(questionnaires, len(questionnaires))
    response = make_response(jsonify([dict(ix) for ix in random_questionnaires]))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

@app.route('/api/questionnaires/ordered')
def get_ordered_questionnaires():
    conn = get_db()
    cursor = conn.execute('SELECT * FROM survey ORDER BY survey_id DESC')  # 使用正确的列名
    ordered_questionnaires = cursor.fetchall()
    response = make_response(jsonify([dict(ix) for ix in ordered_questionnaires]))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

@app.route('/questionnaire/<int:id>')
def questionnaire_detail(id):
    conn = get_db()
    cursor = conn.execute('SELECT * FROM survey WHERE survey_id = ?', (id,))
    survey = cursor.fetchone()
    cursor = conn.execute('SELECT ques_id, ques_content FROM question WHERE survey_id = ?', (id,))
    questions = cursor.fetchall()

    question_details = []
    for question in questions:
        cursor = conn.execute('SELECT sel_id, content, type FROM selection WHERE ques_id = ? AND survey_id = ?', (question[0], id,))
        selections = cursor.fetchall()
        question_details.append((question, selections))
        


    if survey:
        return render_template('questionnaire_detail.html', survey=survey, question_details=question_details)
    else:
        return "Questionnaire not found", 404

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    for key, value in data.items():
        if key != 'survey_id':  # Skip survey_id as it's not a question
            ques_id = int(key.replace('question', ''))
            cursor.execute('INSERT INTO result (survey_id, ques_id, ques_result) VALUES (?, ?, ?)', (data['survey_id'], ques_id, value))
    conn.commit()
    response = jsonify({"status": "success"})
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

@app.route('/download_results/<int:survey_id>')
def download_results(survey_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT question.ques_content, selection.content AS selected_option
        FROM result
        JOIN question ON result.ques_id = question.ques_id
        JOIN selection ON result.ques_result = selection.sel_id
        WHERE result.survey_id = ?
    ''', (survey_id,))
    results = cursor.fetchall()

    # Create a CSV file in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Question', 'Selected Option'])
    for row in results:
        writer.writerow(row)

    output.seek(0)
    response = send_file(io.BytesIO(output.getvalue().encode('utf-8')), mimetype='text/csv; charset=utf-8', as_attachment=True, download_name=f'survey_{survey_id}_results.csv')
    response.headers['Content-Disposition'] = f'attachment; filename=survey_{survey_id}_results.csv'
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    return response

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn=get_db()
        cursor=conn.cursor()
        cursor = cursor.execute("SELECT * FROM user WHERE user_name=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()
        islogin = 0
        if user:
            session['username'] = username
            islogin = 1
            return render_template('index.html',islogin=islogin)
            
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
        conn=get_db()
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM user WHERE user_name=?", (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            conn.close()
            return render_template('signup.html', message="User name already exists, please select another user name!")
        else:
            if password == confirm_password:
                cursor.execute("INSERT INTO user (user_name, password) VALUES (?, ?)", (username, password))
                conn.commit()
                conn.close()
                flash('You were successfully signed up')
                return render_template('login.html')
            else:
                conn.close()
                return render_template('signup.html', message="The password and confirmation password do not match!")
        
    else:
        return render_template('signup.html')
from flask import render_template, redirect, url_for, session

@app.route('/logout')
def logout():
    session.pop('username', None)
    return render_template('logout.html')

@app.route('/survey', methods=['GET','POST'])
def survey():
    if request.method == 'POST':
        survey_data = request.json
        survey_name = survey_data['survey_name']
        survey_lan = survey_data['survey_lan']
        user_id = session["username"]
        ques_id=1

        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Insert survey data into database with a placeholder ques_id
        cursor.execute('INSERT INTO survey (user_id, survey_name, survey_lan, ques_id) VALUES (?, ?, ?, ?)', (user_id, survey_name, survey_lan, ques_id))
        survey_id = cursor.lastrowid  # Get the last inserted survey ID

        first_ques_id = None  # Placeholder for the first question ID

        for question in survey_data['questions']:
            cursor.execute('INSERT INTO question (ques_content, survey_id) VALUES (?, ?)', (question['ques_content'], survey_id))
            ques_id = cursor.lastrowid  # Get the last inserted question ID

            if first_ques_id is None:
                first_ques_id = ques_id  # Set the first question ID
                ques_id+=1

            for option in question['options']:
                cursor.execute('INSERT INTO selection (survey_id, ques_id, content, type) VALUES (?, ?, ?, ?)', (survey_id, ques_id, option['content'], option['type']))

        # Update the survey with the first question ID
        if first_ques_id is not None:
            cursor.execute('UPDATE survey SET ques_id = ? WHERE survey_id = ?', (first_ques_id, survey_id))

        conn.commit()
        conn.close()

        return jsonify({'message': 'Survey data saved successfully.'})
    else:
        return render_template('survey.html')
    
@app.route('/aboutus')
def abtus():
    return render_template('abtus.html')

if __name__ == '__main__':
    app.run(debug=True)
