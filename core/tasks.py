from celery import shared_task
from django.core.cache import cache
from django.core.mail import send_mail
from questions.models import Question, Tag, Answer
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
import json
from django.conf import settings
from core.models import Profile
import requests

@shared_task
def update_popular_tags_cache():
    three_months_ago = timezone.now() - timedelta(days=90)
    
    popular_tags = Tag.objects.filter(
        questions__created_at__gte=three_months_ago
    ).annotate(
        q_count=Count('questions')
    ).order_by('-q_count')[:10]
    
    cache.set('popular_tags', list(popular_tags), timeout=3600)

@shared_task
def update_best_members_cache():
    best_members = Profile.objects.annotate(
        total_rating=Coalesce(Sum('user__answers__rating'), 0) + Coalesce(Sum('user__questions__rating'), 0)
    ).order_by('-total_rating')[:5]
    
    cache.set('best_members', list(best_members), timeout=60 * 60)
    return "Updated best members cache."

@shared_task
def send_new_answer_notification(question_id, answer_text, author_id, answer_id):
    payload = {
        'answer_id': answer_id,
        'text': answer_text,
        'author_id': author_id
    }

    command = {
        "method": "publish",
        "params": {
            "channel": f"questions:{question_id}",
            "data": payload
        }
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'apikey {settings.CENTRIFUGO_API_KEY}'
    }

    try:
        requests.post(settings.CENTRIFUGO_URL, json=command, headers=headers, timeout=2)
    except requests.exceptions.RequestException as e:
        print(f"Centrifugo Error: {e}")
        
    return True

@shared_task
def send_email_notification(question_title, user_email):
    subject = f"Somebody answered your question {question_title}"
    message = f"Somebody answered your question {question_title}"
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )