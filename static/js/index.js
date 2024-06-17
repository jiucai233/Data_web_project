document.addEventListener('DOMContentLoaded', function() {
    const randomBtn = document.getElementById('random-btn');
    const orderedBtn = document.getElementById('ordered-btn');
    const questionnaireContainer = document.getElementById('questionnaire-container');

    function createQuestionnaireHTML(data) {
        return data.map(q => `
            <p class="questionnaire">
                <a href="/questionnaire/${q.survey_id}">${q.survey_name}</a> by ${q.user_id}
                <button class="green_button">
                    <a href="/download_results/${q.survey_id}" style="color: white; text-decoration: none;">download</a>
                </button>
            </p>
        `).join('');
    }

    randomBtn.addEventListener('click', () => {
        fetch('/api/questionnaires/random')
            .then(response => response.json())
            .then(data => {
                questionnaireContainer.innerHTML = createQuestionnaireHTML(data);
            })
            .catch(error => console.error('Error fetching random questionnaires:', error));
    });

    orderedBtn.addEventListener('click', () => {
        fetch('/api/questionnaires/ordered')
            .then(response => response.json())
            .then(data => {
                questionnaireContainer.innerHTML = createQuestionnaireHTML(data);
            })
            .catch(error => console.error('Error fetching ordered questionnaires:', error));
    });

    // Load default ordered questionnaires
    fetch('/api/questionnaires/ordered')
        .then(response => response.json())
        .then(data => {
            questionnaireContainer.innerHTML = createQuestionnaireHTML(data);
        })
        .catch(error => console.error('Error fetching default ordered questionnaires:', error));
});
