from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Question, Tag, QuestionLike, AnswerLike, Answer
from .utils import paginate 
from .forms import AskForm, AnswerForm, QuestionVoteForm, AnswerVoteForm, MarkCorrectForm
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST

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
            url = reverse('question', args=[question_id])
            return redirect(f"{url}#answer-{answer.id}")
    else:
        form = AnswerForm()

    return render(request, 'questions/question.html', {
        'question': question_obj, 
        'answers': page,
        'form': form
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

    question_id = form.cleaned_data['question_id']
    action = form.cleaned_data['action']
    
    question = get_object_or_404(Question, id=question_id)
    value = 1 if action == 'like' else -1

    existing_vote = QuestionLike.objects.filter(user=request.user, question=question).first()
    if existing_vote:
        return JsonResponse({'message': 'You have already voted for this question'}, status=403)

    QuestionLike.objects.create(user=request.user, question=question, value=value)
    question.rating += value
    question.save()

    return JsonResponse({'rating': question.rating})

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

    answer_id = form.cleaned_data['answer_id']
    action = form.cleaned_data['action']

    answer = get_object_or_404(Answer, id=answer_id)
    value = 1 if action == 'like' else -1

    existing_vote = AnswerLike.objects.filter(user=request.user, answer=answer).first()
    if existing_vote:
        return JsonResponse({'message': 'You have already voted for this answer'}, status=403)

    AnswerLike.objects.create(user=request.user, answer=answer, value=value)
    answer.rating += value
    answer.save()

    return JsonResponse({'rating': answer.rating})

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

    question_id = form.cleaned_data['question_id']
    answer_id = form.cleaned_data['answer_id']

    question = get_object_or_404(Question, id=question_id)
    answer = get_object_or_404(Answer, id=answer_id)

    if request.user != question.author:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    if answer.question != question:
        return JsonResponse({'message': 'Answer does not belong to this question'}, status=400)

    answer.is_correct = not answer.is_correct
    answer.save()

    return JsonResponse({'is_correct': answer.is_correct})