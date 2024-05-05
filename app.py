from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_survey', methods=['POST'])
def save_survey():
    data = request.get_json()
    # 在这里处理保存问卷数据的逻辑
    print(data)
    return jsonify({'message': 'Survey data saved successfully'})

if __name__ == '__main__':
    app.run(debug=True)