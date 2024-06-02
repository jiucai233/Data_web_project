from flask import Flask, jsonify, render_template,request
import sqlite3
import random

app = Flask(__name__)
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
    db = sqlite3.connect('user.db')
    return db

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/questionnaires/random')
def get_random_questionnaires():
    conn = get_db()
    cursor = conn.execute('SELECT survey.survey_id, survey.survey_name, user.user_name FROM survey JOIN user ON survey.user_id = user.user_id')
    questionnaires = cursor.fetchall()
    random_questionnaires = random.sample(questionnaires, len(questionnaires))
    return jsonify(random_questionnaires)

@app.route('/api/questionnaires/ordered')
def get_ordered_questionnaires():
    conn = get_db()
    cursor = conn.execute('SELECT survey.survey_id, survey.survey_name, user.user_name FROM survey JOIN user ON survey.user_id = user.user_id ORDER BY survey.survey_id ASC')
    ordered_questionnaires = cursor.fetchall()
    return jsonify(ordered_questionnaires)

@app.route('/questionnaire/<int:id>')
def questionnaire_detail(id):
    conn = get_db()
    cursor = conn.execute('SELECT survey.survey_name, survey.survey_lan, user.user_name FROM survey JOIN user ON survey.user_id = user.user_id WHERE survey.survey_id = ?', (id,))
    survey = cursor.fetchone()
    
    cursor = conn.execute('SELECT ques_id, ques_content FROM question WHERE survey_id = ?', (id,))
    questions = cursor.fetchall()
    
    question_details = []
    for question in questions:
        cursor = conn.execute('SELECT sel_id, content FROM selection WHERE ques_id = ?', (question[0],))
        selections = cursor.fetchall()
        question_details.append((question, selections))
    
    if survey:
        return render_template('questionnaire_detail.html', survey=survey, question_details=question_details)
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

@app.route('/survey', methods=['GET','POST'])
def survey():
    if request.method == 'POST':
        survey_data = request.json
        survey_name = survey_data['survey_name']
        survey_lan = survey_data['survey_lan']
        user_id = 1  # Example user ID, replace with actual value
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
