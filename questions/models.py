from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.contrib.postgres.indexes import GinIndex

class Tag(models.Model):
    name = models.SlugField(max_length=50, unique=True, verbose_name='Название')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class QuestionManager(models.Manager):
    def new(self):
        return self.order_by('-created_at').select_related('author').prefetch_related('tags')

    def hot(self):
        return self.order_by('-rating').select_related('author').prefetch_related('tags')
    
    def by_tag(self, tag_name):
        return self.new().filter(tags__name=tag_name)

class Question(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions', verbose_name='Автор')
    title = models.SlugField(max_length=255, verbose_name='Заголовок')
    text = models.TextField(max_length=1000, verbose_name='Текст вопроса')
    tags = models.ManyToManyField(Tag, related_name='questions', verbose_name='Теги')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')

    search_vector = SearchVectorField(null=True, blank=True) 

    objects = QuestionManager()

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        indexes = [
            GinIndex(fields=['search_vector'], name='search_vector_idx')
        ]

    def update_rating(self):
        total = self.likes.aggregate(Sum('value'))['value__sum']
        self.rating = total or 0
        self.save(update_fields=['rating'])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Question.objects.filter(pk=self.pk).update(
            search_vector=SearchVector('title', weight='A') + SearchVector('text', weight='B')
        )

class Answer(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers', verbose_name='Автор')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='Вопрос')
    text = models.TextField(max_length=1000, verbose_name='Текст ответа')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    is_correct = models.BooleanField(default=False, verbose_name='Верен')

    def __str__(self):
        return f"Ответ {self.author} на вопрос {self.question.id}"
    
    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def update_rating(self):
        total = self.likes.aggregate(Sum('value'))['value__sum']
        self.rating = total or 0
        self.save(update_fields=['rating'])

class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='likes', verbose_name='Вопрос')
    value = models.SmallIntegerField(choices=[(1, 'Like'), (-1, 'Dislike')], verbose_name='Значение')

    class Meta:
        unique_together = ('user', 'question')
        verbose_name = 'Оценка вопроса'
        verbose_name_plural = 'Оценки вопроса'

class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='likes', verbose_name='Ответ')
    value = models.SmallIntegerField(choices=[(1, 'Like'), (-1, 'Dislike')], verbose_name='Значение')

    class Meta:
        unique_together = ('user', 'answer')
        verbose_name = 'Оценка ответа'
        verbose_name_plural = 'Оценки ответа'