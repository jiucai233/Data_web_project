from flask import Flask, request, render_template

app = Flask(__name__)

import sqlite3

# 连接到 SQLite 数据库文件
def user_db_connection():
    conn = sqlite3.connect('users.db')
    return conn




@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn=user_db_connection()
        cursor=conn.cursor()
        # 查询数据库中是否存在该用户
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # 登录成功
            return render_template('login.html', message="登录成功！")
        else:
            # 登录失败
            return render_template('login.html', message="用户名或密码错误！")
    else:
        # 显示登录页面
        return render_template('login.html')


# 路由处理注册请求
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # 处理表单提交
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        conn=user_db_connection
        cursor=conn.cursor()
        # 查询数据库中是否已存在该用户名
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            conn.close()
            return render_template('signup.html', message="用户名已存在，请选择其他用户名！")
        else:
            if password == confirm_password:
                # 插入新用户信息到数据库
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                conn.close()
                return render_template('signup.html', message="注册成功！")
            else:
                conn.close()
                return render_template('signup.html', message="密码和确认密码不一致！")
        
    else:
        # 显示注册页面
        return render_template('signup.html')



if __name__ == '__main__':
    app.run(debug=True)
