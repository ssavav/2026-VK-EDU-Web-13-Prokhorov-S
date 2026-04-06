from django.shortcuts import render
from .utils import paginate 

QUESTIONS =[
    {
        'id': i,
        'title': f'Question {i}',
        'text': f'This is question number {i}.',
        'tags': ['black-jack', 'bender']
    } for i in range(1, 30)
]

ANSWERS =[
    {
        'id': i,
        'text': f"""This is answer {i} for question, Lorem ipsum dolor sit amet, 
        consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore
        et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation""",
    } for i in range(1, 5)
]

def index(request):
    page = paginate(QUESTIONS, request, per_page=3)

    context = {'questions': page}
    return render(request, 'questions/index.html', context)

def hot(request):
    page = paginate(QUESTIONS[:15], request, per_page=3)
    return render(request, 'questions/hot.html', {'questions': page})

def tag(request, tag_name):
    page = paginate(QUESTIONS, request, per_page=3)
    return render(request, 'questions/tag.html', {'questions': page, 'tag_name': tag_name})

def question(request, question_id):
    single_question = next((q for q in QUESTIONS if q['id'] == question_id), QUESTIONS[0])
    
    context = {
        'question': single_question,
        'answers': ANSWERS,
    }
    return render(request, 'questions/question.html', context)

def ask(request):
    return render(request, 'questions/ask.html')