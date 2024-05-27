let questionCount = 0;

function addQuestion() {
    questionCount++;
    const questionContainer = document.getElementById('questions-container');
    const questionDiv = document.createElement('div');
    questionDiv.className = 'question';
    questionDiv.innerHTML = `
        <h3>Question ${questionCount}</h3>
        <textarea rows="2" cols="50" placeholder="Please input your question"></textarea>
        <div class="options">
            <div class="btn-group" role="group" aria-label="Default button group">
                <button type="button" class="btn btn-outline-primary" onclick="addOption(this, 'text')">Text</button>
                <button type="button" class="btn btn-outline-primary" onclick="addOption(this, 'paragraph')">Paragraph</button>
                <button type="button" class="btn btn-outline-primary" onclick="addOption(this, 'multiple')">Multiple Choice</button>
                <button type="button" class="btn btn-outline-primary" onclick="addOption(this, 'single')">Single Choice</button>
                <button type="button" class="btn btn-outline-primary" onclick="addOption(this, 'ranking')">Ranking</button>
            </div>
        </div>
    `;
    questionContainer.appendChild(questionDiv);
}

function addOption(button, type) {
    const optionsContainer = button.parentElement.parentElement;

    let newOption;
    switch(type) {
        case 'text':
            newOption = document.createElement('div');
            newOption.innerHTML = '<input type="text" placeholder="Single text"> <button type="button" class="btn btn-danger" onclick="removeOption(this)">Delete</button>';
            break;
        case 'paragraph':
            newOption = document.createElement('div');
            newOption.innerHTML = '<textarea rows="3" placeholder="Paragraph"></textarea> <button type="button" class="btn btn-danger" onclick="removeOption(this)">Delete</button>';
            break;
        case 'multiple':
            newOption = document.createElement('div');
            newOption.innerHTML = '<input type="checkbox"> <div contenteditable="true" style="display:inline-block;">Click to edit the multiple-choice</div> <button type="button" class="btn btn-danger" onclick="removeOption(this)">Delete</button>';
            break;
        case 'single':
            newOption = document.createElement('div');
            newOption.innerHTML = '<input type="radio" name="multiple-choice"> <div contenteditable="true" style="display:inline-block;">Click to edit the single-choice</div> <button type="button" class="btn btn-danger" onclick="removeOption(this)">Delete</button>';
            break;
        case 'ranking':
            newOption = document.createElement('div');
            newOption.innerHTML = 'Ranking <button type="button" class="btn btn-danger" onclick="removeOption(this)">Delete</button>';
            break;
        default:
            break;
    }
    if (newOption) {
        newOption.style.display = 'block'; // Make sure the choice will be a block
        newOption.style.marginBottom = '10px'; // Add the space
        optionsContainer.appendChild(newOption);
    }
}

function removeOption(button) {
    const optionDiv = button.parentElement;
    optionDiv.remove();
}

function saveSurvey() {
    const surveyName = document.getElementById('survey-name').value;
    const surveyLan = document.getElementById('survey-lan').value;
    const questions = document.getElementsByClassName('question');
    const surveyData = {
        survey_name: surveyName,
        survey_lan: surveyLan,
        questions: []
    };

    for (const question of questions) {
        const questionContent = question.querySelector('textarea').value;
        const options = [];
        const optionElements = question.querySelectorAll('.options > div');

        for (const optionElement of optionElements) {
            const input = optionElement.querySelector('input');
            const textarea = optionElement.querySelector('textarea');
            const editableDiv = optionElement.querySelector('div[contenteditable="true"]');
            let content = '';
            let type = '';

            if (input) {
                content = input.type === 'text' ? input.value : editableDiv.textContent;
                type = input.type === 'text' ? 'text' : 'choice';
            } else if (textarea) {
                content = textarea.value;
                type = 'paragraph';
            } else if (editableDiv) {
                content = editableDiv.textContent;
                type = 'choice';
            }

            options.push({
                content: content,
                type: type
            });
        }

        surveyData.questions.push({
            ques_content: questionContent,
            options: options
        });
    }

    fetch('/saveSurvey', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(surveyData),
    })
    .then(response => {
        if (response.ok) {
            console.log('Survey data saved successfully.');
        } else {
            console.error('Failed to save survey data.');
        }
    })
    .catch(error => {
        console.error('Error saving survey data:', error);
    });
}