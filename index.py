from flask import Flask, jsonify, render_template
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

if __name__ == '__main__':
    app.run(debug=True)
