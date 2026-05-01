from django.shortcuts import render, get_object_or_404
from .models import Question, Tag
from .utils import paginate 

def index(request):
    questions = Question.objects.new()
    page = paginate(questions, request, per_page=10)
    return render(request, 'questions/index.html', {'questions': page})

def hot(request):
    questions = Question.objects.hot()
    page = paginate(questions, request, per_page=10)
    return render(request, 'questions/hot.html', {'questions': page})

def tag(request, tag_name):

    tag_obj = get_object_or_404(Tag, name=tag_name)
    questions = tag_obj.questions.select_related('author').prefetch_related('tags')
    page = paginate(questions, request, per_page=10)
    return render(request, 'questions/tag.html', {'questions': page, 'tag_name': tag_obj.name})

def question(request, question_id):
    question_obj = get_object_or_404(Question, id=question_id)
    answers = question_obj.answers.select_related('author').order_by('-rating', '-created_at')
    
    page = paginate(answers, request, per_page=10)
    return render(request, 'questions/question.html', {'question': question_obj, 'answers': page})

def ask(request):
    return render(request, 'questions/ask.html')