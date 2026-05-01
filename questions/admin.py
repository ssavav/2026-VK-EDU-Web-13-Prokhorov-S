from django.contrib import admin
from .models import Question, Answer, Tag, QuestionLike, AnswerLike

class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 1

    raw_id_fields = ('author',) 

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'rating')
    list_filter = ('created_at',)
    search_fields = ('title', 'text', 'author__username')
    inlines = [AnswerInline]
    raw_id_fields = ('author',)
    filter_horizontal = ('tags',)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'author', 'created_at', 'is_correct')
    list_filter = ('is_correct', 'created_at')
    search_fields = ('text', 'author__username', 'question__title')
    raw_id_fields = ('author', 'question')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'value')
    raw_id_fields = ('user', 'question')

@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'answer', 'value')
    raw_id_fields = ('user', 'answer')