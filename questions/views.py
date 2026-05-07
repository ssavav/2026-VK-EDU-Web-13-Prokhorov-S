from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Question, Tag
from .utils import paginate 
from .forms import AskForm, AnswerForm

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