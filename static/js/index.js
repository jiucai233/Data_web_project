document.addEventListener('DOMContentLoaded', function() {
    const randomBtn = document.getElementById('random-btn');
    const orderedBtn = document.getElementById('ordered-btn');
    const questionnaireContainer = document.getElementById('questionnaire-container');

    randomBtn.addEventListener('click', () => {
        fetch('/api/questionnaires/random')
            .then(response => response.json())
            .then(data => {
                questionnaireContainer.innerHTML = data.map(q => `<p class="questionnaire"><a href="/questionnaire/${q.survey_id}">The survey ${q.survey_name}</a> by ${q.user_id} <a href="/download_results/${q.survey_id}">download</a></p>`).join('');
            })
            .catch(error => console.error('Error fetching random questionnaires:', error));
    });

    orderedBtn.addEventListener('click', () => {
        fetch('/api/questionnaires/ordered')
            .then(response => response.json())
            .then(data => {
                questionnaireContainer.innerHTML = data.map(q => `<p class="questionnaire"><a href="/questionnaire/${q.survey_id}">The survey ${q.survey_name}</a> by ${q.user_id} <a href="/download_results/${q.survey_id}">download</a></p>`).join('');
            })
            .catch(error => console.error('Error fetching ordered questionnaires:', error));
    });

    fetch('/api/questionnaires/ordered')
        .then(response => response.json())
        .then(data => {
            questionnaireContainer.innerHTML = data.map(q => `<p class="questionnaire"><a href="/questionnaire/${q.survey_id}">The survey ${q.survey_name}</a> by ${q.user_id} <a href="/download_results/${q.survey_id}">download</a></p>`).join('');
        })
        .catch(error => console.error('Error fetching default ordered questionnaires:', error));
});
