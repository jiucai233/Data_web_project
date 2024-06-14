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
# Initialize answer_list function
def initialize_answer_list(rows, cols):
    """Initialize a nested list with specified dimensions."""
    return [['0' for _ in range(cols)] for _ in range(rows)]

# Correctly merge result_list into answer_list
def correct_merge(result_list):
    # 确定 answer_list 的尺寸
    max_row = max(row for _, row, _ in result_list)
    max_col = max(col for _, _, col in result_list)
    
    # 初始化 answer_list
    answer_list = initialize_answer_list(max_row, max_col)

    # 使用 result_list 更新 answer_list
    for value, row, col in result_list:
        answer_list[row-1][col-1] = value


    return answer_list




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
        print(question_details)
    


    if survey:
        return render_template('questionnaire_detail.html', survey=survey, question_details=question_details)
    else:
        return "Questionnaire not found", 404

@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    try:
        data = request.json
        survey_id = data.get('survey_id')

        # 连接到 SQLite 数据库
        conn = sqlite3.connect('user.db')
        cursor = conn.cursor()

        # 查询给定 survey_id 的最后一个 result_id，如果没有记录则从 1 开始
        cursor.execute("SELECT * FROM result WHERE survey_id = ? ORDER BY result_id DESC LIMIT 1;", (survey_id,))
        row = cursor.fetchone()
        if row:
            result_id = row[3] + 1  # 获取最后一个 result_id，并加一
        else:
            result_id = 1  # 如果没有记录，则从 1 开始

        # 处理 data 中的每个问题及其答案
        for question_key, answer in data.items():
            if question_key == 'survey_id':
                continue
            
            if question_key.startswith('question'):
                if '_' in question_key:
                    question_id = int(question_key.split('_')[0].replace('question', ''))
                else:
                    question_id = int(question_key.replace('question', ''))
                
                sel_id_key = f'sel_id_question{question_id}'
                sel_id = data.get(sel_id_key)
                
                if sel_id is None:
                    sel_id = answer
                    answer = 1
                
                if isinstance(answer, list):
                    result = {}
                    for i in range(len(answer)):
                        if answer[i] not in result:
                            result[answer[i]] = sel_id[i]
                        elif isinstance(result[answer[i]], list):
                            result[answer[i]].append(sel_id[i])
                        else:
                            result[answer[i]] = [result[answer[i]], sel_id[i]]
                    
                    for answer_single, sel_id_single in result.items():
                        if isinstance(sel_id_single, list):
                            for sel_id_item in sel_id_single:
                                cursor.execute('INSERT INTO result (survey_id, ques_id, sel_id, result, result_id) VALUES (?, ?, ?, ?, ?)',
                                            (survey_id, question_id, sel_id_item, answer_single, result_id))
                        else:
                            cursor.execute('INSERT INTO result (survey_id, ques_id, sel_id, result, result_id) VALUES (?, ?, ?, ?, ?)',
                                        (survey_id, question_id, sel_id_single, answer_single, result_id))
                else:
                    cursor.execute('INSERT INTO result (survey_id, ques_id, sel_id, result, result_id) VALUES (?, ?, ?, ?, ?)',
                                (survey_id, question_id, sel_id, answer, result_id))
        # 提交更改并关闭连接
        conn.commit()
        return jsonify({'message': 'Survey submitted successfully!'})
    
    except Exception as e:
        print(f"Error saving survey results: {e}")
        conn.rollback()
        return jsonify({'error': 'Error saving survey results'}), 500
    
    finally:
        conn.close()
    



@app.route('/download_results/<int:survey_id>')
def download_results(survey_id):
    conn = get_db_connection()

    # Fetch selection_list
    cursor = conn.execute('SELECT content, ques_id, sel_id FROM selection WHERE survey_id = ? ORDER BY sel_id ASC', (survey_id,))
    selection_list = list(cursor.fetchall())

    # Fetch result_list
    cursor = conn.execute('SELECT result, sel_id, result_id FROM result WHERE survey_id = ? ORDER BY result_id, ques_id DESC', (survey_id,))
    result_list = list(cursor.fetchall())

    final_answer_list = correct_merge(result_list)
    max_col = max(col for _, _, col in result_list)
    answer_list = ['question_content','selection_content']
    for i in range(max_col):
        answer_list.append(f'answer{i+1}')
    print(answer_list)
    # 在每个子列表的开头添加 selection_content
    for i in range(len(final_answer_list)):
        selection_content = selection_list[i][0]  # 获取 selection_content
        cursor = conn.execute('SELECT ques_content FROM question WHERE ques_id = ?', (selection_list[i][1],))
        ques_content = cursor.fetchone()  # 获取 ques_content
        final_answer_list[i].insert(0, ques_content[0])
        final_answer_list[i].insert(1, selection_content)
    final_answer_list.insert(0,answer_list)

    # Create a CSV file in memory
    output = io.StringIO()
    writer = csv.writer(output)
    for row in final_answer_list:
        writer.writerow(row)

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv; charset=utf-8',
        as_attachment=True,
        download_name=f'survey_{survey_id}_results.csv'
    )


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
        ques_id = 0
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Insert survey data into database with a placeholder ques_id
        cursor.execute('INSERT INTO survey (user_id, survey_name, survey_lan, ques_id) VALUES (?, ?, ?, ?)', (user_id, survey_name, survey_lan, ques_id))
        survey_id = cursor.lastrowid  # Get the last inserted survey ID

        for question in survey_data['questions']:
            cursor.execute('INSERT INTO question (ques_content, survey_id) VALUES (?, ?)', (question['ques_content'], survey_id))
            ques_id = cursor.lastrowid # Get the last inserted question ID

            for option in question['options']:
                cursor.execute('INSERT INTO selection (survey_id, ques_id, content, type) VALUES (?, ?, ?, ?)', (survey_id, ques_id, option['content'], option['type']))

        conn.commit()
        conn.close()

        return jsonify({'message': 'Survey data saved successfully.'})
    else:
        return render_template('survey.html')

if __name__ == '__main__':
    app.run(debug=True)
