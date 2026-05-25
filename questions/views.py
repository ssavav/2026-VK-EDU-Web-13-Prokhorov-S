from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django import forms
from .models import Question, Tag, QuestionLike, AnswerLike, Answer
from .utils import paginate 
from .forms import AskForm, AnswerForm, QuestionVoteForm, AnswerVoteForm, MarkCorrectForm
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from core.tasks import send_new_answer_notification, send_email_notification
from django.contrib.postgres.search import SearchQuery
import jwt
import time
from django.conf import settings

def index(request):
    questions = Question.objects.new()
    page = paginate(questions, request, per_page=10)
    return render(request, 'questions/index.html', {'questions': page})

def hot(request):
    questions = Question.objects.hot()
    page = paginate(questions, request, per_page=10)
    return render(request, 'questions/hot.html', {'questions': page})

def tag(request, tag_name):
    tag_obj = Tag.objects.filter(name=tag_name).first()
    
    if tag_obj:
        questions = tag_obj.questions.select_related('author').prefetch_related('tags')
    else:
        questions = []

    page = paginate(questions, request, per_page=10)
    
    return render(request, 'questions/tag.html', {
        'questions': page, 
        'tag_name': tag_name
    })

def question(request, question_id):
    question_obj = get_object_or_404(Question, id=question_id)
    answers = question_obj.answers.select_related('author').order_by('-rating', '-created_at')
    page = paginate(answers, request, per_page=30)

    if request.method == 'POST':
            
        form = AnswerForm(request.POST, author=request.user, question_obj=question_obj)
        if form.is_valid():
            answer = form.save()

            send_new_answer_notification.delay(
                question_id=question_id,
                answer_text=answer.text,
                author_id=answer.author.id,
                answer_id=answer.id
            )

            if question_obj.author.email:
                send_email_notification.delay(
                    question_title=question_obj.title,
                    user_email=question_obj.author.email
                )
            url = reverse('question', args=[question_id])
            return redirect(f"{url}#answer-{answer.id}")
    else:
        form = AnswerForm()

    user_id = str(request.user.id) if request.user.is_authenticated else ""

    expiration = int(time.time()) + 3600 

    centrifugo_token = jwt.encode(
        {"sub": user_id, "exp": expiration}, 
        settings.CENTRIFUGO_SECRET_KEY, 
        algorithm="HS256"
    )

    return render(request, 'questions/question.html', {
        'question': question_obj, 
        'answers': page,
        'form': form,
        'centrifugo_token': centrifugo_token
    })

@login_required(login_url='login')
def ask(request):
    if request.method == 'POST':
        form = AskForm(request.POST, author=request.user)
        if form.is_valid():
            question = form.save()
            return redirect('question', question_id=question.id)
    else:
        form = AskForm()
        
    return render(request, 'questions/ask.html', {'form': form})

@require_POST
def vote_question(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    form = QuestionVoteForm(data)
    if not form.is_valid():
        return JsonResponse({'error': 'Invalid data', 'details': form.errors}, status=400)

    rating = form.save(user=request.user)
    return JsonResponse({'rating': rating})

@require_POST
def vote_answer(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    form = AnswerVoteForm(data)
    if not form.is_valid():
        return JsonResponse({'error': 'Invalid data', 'details': form.errors}, status=400)

    rating = form.save(user=request.user)
    return JsonResponse({'rating': rating})

@require_POST
def mark_correct(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    form = MarkCorrectForm(data)
    if not form.is_valid():
        return JsonResponse({'error': 'Invalid data', 'details': form.errors}, status=400)

    try:
        is_correct = form.save(user=request.user)
        return JsonResponse({'is_correct': is_correct})
    except forms.ValidationError as e:
        return JsonResponse({'error': e.message}, status=403)
    

from django.contrib.postgres.search import SearchQuery

def search_suggestions(request):
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})

    search_query = SearchQuery(query)
    questions = Question.objects.filter(search_vector=search_query).order_by('-rating')[:5]
    
    suggestions = [
        {
            'id': q.id,
            'title': q.title,
            'url': reverse('question', args=[q.id])
        } for q in questions
    ]
    
    return JsonResponse({'suggestions': suggestions})