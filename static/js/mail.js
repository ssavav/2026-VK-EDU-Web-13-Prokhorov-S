document.addEventListener("DOMContentLoaded", () => {
    const wsSettingsConfig = document.getElementById('ws-settings');
    if (!wsSettingsConfig) return;
    
    const wsSettings = JSON.parse(wsSettingsConfig.textContent);
    
    const questionId = wsSettings.questionId;
    const currentPage = wsSettings.currentPage;

    const centrifuge = new Centrifuge('ws://localhost:8001/connection/websocket', {
        token: wsSettings.token
    });

    centrifuge.on('connecting', function (ctx) {
        console.log(`connecting: ${ctx.code}, ${ctx.reason}`);
    }).on('connected', function (ctx) {
        console.log(`connected over ${ctx.transport}`);
    }).on('disconnected', function (ctx) {
        console.log(`disconnected: ${ctx.code}, ${ctx.reason}`);
    }).connect();

    const channel = `questions:${questionId}`;
    const sub = centrifuge.newSubscription(channel);
    
    sub.on('publication', function (ctx) {
        const data = ctx.data;
        
        const noAnswersAlert = document.querySelector('.alert-no-answers');
        if (noAnswersAlert) {
            noAnswersAlert.remove();
        }

        const avatarUrl = data.avatar_url ? data.avatar_url : "/static/img/avatar.jpg";
        
        const answerHTML = `
            <div id="answer-${data.answer_id}">
                <div class="question-card p-3 mb-3">
                    <div class="row">
                        <div class="col-2 col-md-1">
                            <img src="${avatarUrl}" alt="avatar" class="avatar-img mb-2">
                            <div class="d-flex align-items-center mt-2">
                                <button type="button" class="btn btn-outline-success btn-sm px-1 py-0 fw-bold vote-answer-btn" 
                                    data-id="${data.answer_id}" data-action="like">&#9650;</button>
                                
                                <span class="fw-bold mx-1 my-1 fs-5" id="rating-answer-${data.answer_id}">0</span>

                                <button type="button" class="btn btn-outline-danger btn-sm px-1 py-0 fw-bold vote-answer-btn" 
                                    data-id="${data.answer_id}" data-action="dislike">&#9660;</button>
                            </div>
                        </div>
                        <div class="col-10 col-md-11">
                            <p class="mb-2">${data.text}</p>
                
                            <div class="form-check mt-3">
                                <input class="form-check-input mark-correct-checkbox" type="checkbox" value="" 
                                    id="correctAnswer${data.answer_id}" 
                                    data-answer-id="${data.answer_id}" 
                                    data-question-id="${questionId}">
                                <label class="form-check-label text-success fw-bold" for="correctAnswer${data.answer_id}">
                                    Correct answer!
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        formContainer = document.querySelector('.ans-list');
        formContainer.insertAdjacentHTML('beforebegin', answerHTML);
    });
    
    sub.subscribe();
});