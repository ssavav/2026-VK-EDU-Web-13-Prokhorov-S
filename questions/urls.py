from django.urls import path
from . import views

urlpatterns =[
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('ask/', views.ask, name='ask'),
    path('vote_question/', views.vote_question, name='vote_question'),
    path('vote_answer/', views.vote_answer, name='vote_answer'),
    path('mark_correct/', views.mark_correct, name='mark_correct'),
    path('search/', views.search_suggestions, name='search_suggestions'),
]