let questionCount = 0;

function addQuestion() {
    questionCount++;
    const questionContainer = document.getElementById('questions-container');
    const questionDiv = document.createElement('div');
    questionDiv.className = 'question';
    questionDiv.innerHTML = `
        <h3>Question ${questionCount}</h3>
        <textarea rows="2" cols="50" class="shadow-input" placeholder="Please input your question"></textarea>
        <div class="options">
            <div class="button-container">
                <button type="button" class="blue_button" onclick="addOption(this, 'text')">Text</button>
                <button type="button" class="blue_button" onclick="addOption(this, 'paragraph')">Paragraph</button>
                <button type="button" class="blue_button" onclick="addOption(this, 'multiple')">Multiple Choice</button>
                <button type="button" class="blue_button" onclick="addOption(this, 'single')">Single Choice</button>
            </div>
        </div>
    `;
    questionContainer.appendChild(questionDiv);
}

function adjustWidth(el) {
    // Create a temporary element to measure the width of the input content
    const tempEl = document.createElement('span');
    tempEl.style.visibility = 'hidden';
    tempEl.style.position = 'absolute';
    tempEl.style.whiteSpace = 'nowrap';
    tempEl.innerText = el.value || el.placeholder;

    document.body.appendChild(tempEl);
    const width = tempEl.offsetWidth;
    document.body.removeChild(tempEl);

    // Set the width of the input element based on the temporary element's width
    el.style.width = `${width + 10}px`;
}
function addOption(button, type) {
    const optionsContainer = button.parentElement.parentElement;

    let newOption;
    switch(type) {
        case 'text':
            newOption = document.createElement('div');
            newOption.innerHTML = '<input type="text" class="shadow-input" placeholder="Single text"> <button class="button-82-pushable" role="button" onclick="removeOption(this)"><span class="button-82-shadow"></span><span class="button-82-edge"></span><span class="button-82-front text">delete</span></button>';
            break;
        case 'paragraph':
            newOption = document.createElement('div');
            newOption.innerHTML = '<textarea rows="3" class="shadow-input" placeholder="Paragraph"></textarea> <button class="button-82-pushable" role="button" onclick="removeOption(this)"><span class="button-82-shadow"></span><span class="button-82-edge"></span><span class="button-82-front text">delete</span></button>';
            break;
        case 'multiple':
            newOption = document.createElement('div');
            newOption.innerHTML = '<input type="checkbox" name="multiple-choice"> <input type="text" class="shadow-input" placeholder="Click to edit the multiple-choice" style="display:inline-block;" oninput="adjustWidth(this)"> <button class="button-82-pushable" role="button" onclick="removeOption(this)"><span class="button-82-shadow"></span><span class="button-82-edge"></span><span class="button-82-front text">delete</span></button>';
            break;
        case 'single':
            newOption = document.createElement('div');
            newOption.innerHTML = '<input type="radio" name="single-choice"> <input type="text" class="shadow-input" placeholder="Click to edit the single-choice" style="display:inline-block;" oninput="adjustWidth(this)"> <button class="button-82-pushable" role="button" onclick="removeOption(this)"><span class="button-82-shadow"></span><span class="button-82-edge"></span><span class="button-82-front text">delete</span></button>';
            break;
        default:
            break;
    }
    if (newOption) {
        newOption.style.display = 'block'; // Make sure the choice will be a block
        newOption.style.marginBottom = '10px'; // Add the space
        optionsContainer.appendChild(newOption);
        console.log("add");
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
            const input = optionElement.querySelector('input[type="text"]');
            const textarea = optionElement.querySelector('textarea');
            const checkbox = optionElement.querySelector('input[type="checkbox"]');
            const radio = optionElement.querySelector('input[type="radio"]');
            let content = '';
            let type = '';

            if (input && !radio && !checkbox) {
                content = input.value;
                type = 'text';
            } else if (textarea) {
                content = textarea.value;
                type = 'paragraph';
            } else if (checkbox) {
                content = input ? input.value : '';
                type = 'multiple';
            } else if (radio) {
                content = input ? input.value : '';
                type = 'single';
            } else {
                continue;
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

    fetch('/survey', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(surveyData),
    })
    .then(response => {
        if (response.ok) {
            console.log('Survey data saved successfully.');
            alert("Survey data saved successfully！");
            window.location.href = '/';
        } else {
            console.error('Failed to save survey data.');
            alert("You have not logged in! Please log in first.");
            window.location.href = '/';
        }
    })
    .catch(error => {
        console.error('Error saving survey data:', error);
    });
}
