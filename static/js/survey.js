let questionCount = 0;

function addQuestion() {
    questionCount++;
    const questionContainer = document.getElementById('questions-container');
    const questionDiv = document.createElement('div');
    questionDiv.className = 'question';
    questionDiv.innerHTML = `
        <h3>问题 ${questionCount}</h3>
        <textarea rows="2" cols="50" placeholder="请输入问题内容"></textarea>
        <div class="options">
            <input type="radio" name="question${questionCount}-type" value="单选" checked> 单选
            <input type="radio" name="question${questionCount}-type" value="多选"> 多选
            <input type="radio" name="question${questionCount}-type" value="文本框"> 文本框
        </div>
        <button onclick="addOption(this)">添加选项</button>
    `;
    questionContainer.appendChild(questionDiv);
}

function addOption(btn) {
    const optionContainer = btn.previousElementSibling;
    const optionInput = document.createElement('input');
    optionInput.type = 'text';
    optionInput.placeholder = '选项内容';
    optionContainer.appendChild(optionInput);
}

function saveSurvey() {
    const questions = document.getElementsByClassName('question');
    const surveyData = [];
    for (const question of questions) {
        const questionText = question.querySelector('textarea').value;
        const questionType = question.querySelector('input[name^="question"]:checked').value;
        const options = [];
        if (questionType !== '文本框') {
            const optionInputs = question.querySelectorAll('.options input[type="text"]');
            optionInputs.forEach(input => {
                if (input.value.trim() !== '') {
                    options.push(input.value.trim());
                }
            });
        }
        surveyData.push({ question: questionText, type: questionType, options: options });
    }
    console.log(surveyData);
}
// const addQuestionButton = document.getElementById('addQuestionButton');
// const questionContainer = document.getElementById('questionContainer');

// addQuestionButton.addEventListener('click', () => {
//   const newQuestionBox = document.createElement('div'); // Create question box element
//   newQuestionBox.innerHTML = '<label>Question:</label><input type="text">'; // Add question text input
//   questionContainer.appendChild(newQuestionBox); // Append question box to container
// });
