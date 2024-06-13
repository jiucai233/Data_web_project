// submit_survey.js

async function submitForm(event) {
    event.preventDefault();

    const form = document.getElementById('questionnaire-form');
    const formData = new FormData(form);
    const jsonData = {};

    formData.forEach((value, key) => {
        if (key in jsonData) {
            if (!Array.isArray(jsonData[key])) {
                jsonData[key] = [jsonData[key]];
            }
            jsonData[key].push(value);
        } else {
            jsonData[key] = value;
        }
    });

    try {
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true; // 禁用提交按钮

        const response = await fetch('/submit_survey', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(jsonData),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const responseData = await response.json();
        alert(responseData.message);
        window.location.href = '/';
    } catch (error) {
        console.error('Error submitting form:', error);
        alert('Error submitting survey. Please try again later.');
        window.location.href = '/';
    } finally {
        submitButton.disabled = false; // 恢复提交按钮
    }
}

document.getElementById('questionnaire-form').addEventListener('submit', submitForm);
