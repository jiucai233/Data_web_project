from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)
db_path = 'user.db'

que_id=1
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

@app.route('/')
def home():
    return render_template('survey.html')

@app.route('/survey')
def show_survey():
    return render_template('survey.html')

@app.route('/saveSurvey', methods=['POST'])
def save_survey():
    survey_data = request.json
    survey_name = survey_data['survey_name']
    survey_lan = survey_data['survey_lan']
    user_id = 1  # Example user ID, replace with actual value

    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insert survey data into database with a placeholder ques_id
    cursor.execute('INSERT INTO survey (user_id, survey_name, survey_lan, ques_id) VALUES (?, ?, ?, ?)', (user_id, survey_name, survey_lan, None))
    survey_id = cursor.lastrowid  # Get the last inserted survey ID

    first_ques_id = 'q1'  # Placeholder for the first question ID

    for question in survey_data['questions']:
        cursor.execute('INSERT INTO question (ques_content, survey_id) VALUES (?, ?)', (question['ques_content'], survey_id))
        ques_id = cursor.lastrowid  # Get the last inserted question ID

        if first_ques_id is None:
            first_ques_id = ques_id  # Set the first question ID

        for option in question['options']:
            cursor.execute('INSERT INTO selection (survey_id, ques_id, content, type) VALUES (?, ?, ?, ?)', (survey_id, ques_id, option['content'], option['type']))

    # Update the survey with the first question ID
    if first_ques_id is not None:
        cursor.execute('UPDATE survey SET ques_id = ? WHERE survey_id = ?', (first_ques_id, survey_id))

    conn.commit()
    conn.close()

    return jsonify({'message': 'Survey data saved successfully.'})

if __name__ == '__main__':
    app.run(debug=True)