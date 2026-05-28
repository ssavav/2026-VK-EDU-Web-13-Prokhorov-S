from django.core.cache import cache
from questions.models import Tag
from core.models import Profile
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from core.tasks import update_popular_tags_cache, update_best_members_cache

def sidebar_data(request):
    popular_tags = cache.get('popular_tags')
    
    if not popular_tags:
        popular_tags = Tag.objects.annotate(q_count=Count('questions')).order_by('-q_count')[:10]
        cache.set('popular_tags', list(popular_tags), timeout=60 * 15)
        update_popular_tags_cache.delay()

    best_members = cache.get('best_members')
    
    if not best_members:
        best_members = Profile.objects.annotate(
            total_rating=Coalesce(Sum('user__answers__rating'), 0) + Coalesce(Sum('user__questions__rating'), 0)
        ).order_by('-total_rating')[:5]
        cache.set('best_members', list(best_members), timeout=60 * 15)
        update_best_members_cache.delay()

    return {
        'popular_tags': popular_tags,
        'best_members': best_members
    }