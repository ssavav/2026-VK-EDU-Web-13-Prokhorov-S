function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', () => {
    const questionVoteBtns = document.querySelectorAll('.vote-question-btn');

    questionVoteBtns.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            if (this.hasAttribute('disabled')) return;

            const questionId = this.dataset.id;
            const action = this.dataset.action;
            const ratingSpan = document.getElementById(`rating-question-${questionId}`);

            fetch('/vote_question/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    question_id: questionId,
                    action: action
                })
            })
            .then(response => {
                return response.json().then(data => ({status: response.status, body: data}));
            })
            .then(result => {
                if (result.status === 200) {
                    ratingSpan.textContent = result.body.rating;
                    
                    const btns = document.querySelectorAll(`.vote-question-btn[data-id="${questionId}"]`);
                    btns.forEach(btn => btn.setAttribute('disabled', 'disabled'));
                } else if (result.status === 401) {
                    alert(result.body.message);
                    window.location.href = '/login/';
                } else {
                    alert(result.body.message);
                    const btns = document.querySelectorAll(`.vote-question-btn[data-id="${questionId}"]`);
                    btns.forEach(btn => btn.setAttribute('disabled', 'disabled'));
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
    const answerVoteBtns = document.querySelectorAll('.vote-answer-btn');

    answerVoteBtns.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            if (this.hasAttribute('disabled')) return;

            const answerId = this.dataset.id;
            const action = this.dataset.action;
            const ratingSpan = document.getElementById(`rating-answer-${answerId}`);

            fetch('/vote_answer/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    answer_id: answerId,
                    action: action
                })
            })
            .then(response => response.json().then(data => ({status: response.status, body: data})))
            .then(result => {
                if (result.status === 200) {
                    ratingSpan.textContent = result.body.rating;
                    const btns = document.querySelectorAll(`.vote-answer-btn[data-id="${answerId}"]`);
                    btns.forEach(btn => btn.setAttribute('disabled', 'disabled'));
                } else if (result.status === 401) {
                    alert(result.body.message);
                    window.location.href = '/login/';
                } else {
                    alert(result.body.message);
                    const btns = document.querySelectorAll(`.vote-answer-btn[data-id="${answerId}"]`);
                    btns.forEach(btn => btn.setAttribute('disabled', 'disabled'));
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    const correctCheckboxes = document.querySelectorAll('.mark-correct-checkbox');

    correctCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function(e) {
            const answerId = this.dataset.answerId;
            const questionId = this.dataset.questionId;
            const isChecked = this.checked;

            fetch('/mark_correct/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    question_id: questionId,
                    answer_id: answerId
                })
            })
            .then(response => response.json().then(data => ({status: response.status, body: data})))
            .then(result => {
                if (result.status === 200) {
                    if (result.body.is_correct) {
                        correctCheckboxes.forEach(cb => {
                            if (cb !== checkbox) {
                                cb.checked = false;
                            }
                        });
                    }
                } else {
                    alert(result.body.message);
                    this.checked = !isChecked;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.checked = !isChecked;
            });
        });
    });

});

