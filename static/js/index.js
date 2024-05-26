document.addEventListener('DOMContentLoaded', function() {
    const randomBtn = document.getElementById('random-btn');
    const orderedBtn = document.getElementById('ordered-btn');
    const questionnaireContainer = document.getElementById('questionnaire-container');

    randomBtn.addEventListener('click', () => {
        fetch('/api/questionnaires/random')
            .then(response => response.json())
            .then(data => {
                questionnaireContainer.innerHTML = data.map(q => `<p><a href="/questionnaire/${q[1]}">${q[2]}</a></p>`).join(''); 
            })
            .catch(error => console.error('Error fetching random questionnaires:', error));
    });

    orderedBtn.addEventListener('click', () => {
        fetch('/api/questionnaires/ordered')
            .then(response => response.json())
            .then(data => {
                questionnaireContainer.innerHTML = data.map(q => `<p><a href="/questionnaire/${q[1]}">${q[2]}</a></p>`).join(''); 
            })
            .catch(error => console.error('Error fetching ordered questionnaires:', error));
    });

    // 默认按时间顺序加载问卷
    fetch('/api/questionnaires/ordered')
        .then(response => response.json())
        .then(data => {
            questionnaireContainer.innerHTML = data.map(q => `<p><a href="/questionnaire/${q[1]}">${q[2]}</a></p>`).join(''); 
        })
        .catch(error => console.error('Error fetching default ordered questionnaires:', error));
});
