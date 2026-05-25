import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Max, Sum, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.contrib.postgres.search import SearchVector
from core.models import Profile
from questions.models import Question, Answer, Tag, QuestionLike, AnswerLike
from faker import Faker

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def handle(self, *args, **kwargs):
        User.objects.all().delete()
        Tag.objects.all().delete()
        ratio = kwargs['ratio']
        fake = Faker()

        users_count = ratio
        questions_count = ratio * 10
        answers_count = ratio * 100
        tags_count = ratio
        likes_count = ratio * 200

        BATCH_SIZE = 10000 

        tag_offset = Tag.objects.aggregate(Max('id'))['id__max'] or 0
        user_offset = User.objects.aggregate(Max('id'))['id__max'] or 0

        tags = [Tag(name=f"{fake.word()}_{tag_offset + i}") for i in range(tags_count)]
        Tag.objects.bulk_create(tags, batch_size=BATCH_SIZE)
        self.stdout.write(f"Успешно создано {tags_count} тегов")
        all_tag_ids = list(Tag.objects.values_list('id', flat=True))

        users = [
            User(
                username=f"{fake.user_name()}_{user_offset + i}",
                email=fake.email(),
                password="pbkdf2_sha256$260000$supersecret"
            ) for i in range(users_count)
        ]
        User.objects.bulk_create(users, batch_size=BATCH_SIZE)
        self.stdout.write(f"Успешно создано {users_count} пользователей")
        
        all_user_ids = list(User.objects.values_list('id', flat=True))
        
        new_users_without_profile = User.objects.filter(profile__isnull=True).values_list('id', flat=True)
        profiles = [Profile(user_id=uid) for uid in new_users_without_profile]
        Profile.objects.bulk_create(profiles, batch_size=BATCH_SIZE)
        self.stdout.write(f"Успешно создано {users_count} профилей")

        questions = [
            Question(
                author_id=random.choice(all_user_ids),
                title=fake.sentence()[:255],
                text=fake.text(),
            ) for _ in range(questions_count)
        ]
        created_questions = Question.objects.bulk_create(questions, batch_size=BATCH_SIZE)
        self.stdout.write(f"Успешно создано {questions_count} вопросов")

        new_question_ids = [q.id for q in created_questions]
        all_question_ids = list(Question.objects.values_list('id', flat=True))

        ThroughModel = Question.tags.through
        m2m_tags = []
        for q_id in new_question_ids:
            selected_tags = random.sample(all_tag_ids, k=random.randint(1, 3))
            for t_id in selected_tags:
                m2m_tags.append(ThroughModel(question_id=q_id, tag_id=t_id))
        ThroughModel.objects.bulk_create(m2m_tags, batch_size=BATCH_SIZE)

        answers = [
            Answer(
                author_id=random.choice(all_user_ids),
                question_id=random.choice(all_question_ids),
                text=fake.text(),
                is_correct=random.choice([True, False, False, False])
            ) for _ in range(answers_count)
        ]
        created_answers = Answer.objects.bulk_create(answers, batch_size=BATCH_SIZE)
        self.stdout.write(f"Успешно создано {answers_count} ответов")
        all_answer_ids = list(Answer.objects.values_list('id', flat=True))

        existing_q_likes = set()
        q_likes = []
        while len(q_likes) < (likes_count // 2):
            u_id = random.choice(all_user_ids)
            q_id = random.choice(all_question_ids)
            if (u_id, q_id) not in existing_q_likes:
                existing_q_likes.add((u_id, q_id))
                q_likes.append(QuestionLike(user_id=u_id, question_id=q_id, value=random.choice([1, -1])))
        QuestionLike.objects.bulk_create(q_likes, batch_size=BATCH_SIZE, ignore_conflicts=True)

        existing_a_likes = set()
        a_likes = []
        while len(a_likes) < (likes_count // 2):
            u_id = random.choice(all_user_ids)
            a_id = random.choice(all_answer_ids)
            if (u_id, a_id) not in existing_a_likes:
                existing_a_likes.add((u_id, a_id))
                a_likes.append(AnswerLike(user_id=u_id, answer_id=a_id, value=random.choice([1, -1])))
        AnswerLike.objects.bulk_create(a_likes, batch_size=BATCH_SIZE, ignore_conflicts=True)

        self.stdout.write(f"Успешно создано {likes_count} оценок вопросов")
        q_likes = QuestionLike.objects.filter(question=OuterRef('pk')).values('question').annotate(total=Sum('value')).values('total')
        Question.objects.update(rating=Coalesce(Subquery(q_likes), 0))

        a_likes = AnswerLike.objects.filter(answer=OuterRef('pk')).values('answer').annotate(total=Sum('value')).values('total')
        Answer.objects.update(rating=Coalesce(Subquery(a_likes), 0))

        Question.objects.update(search_vector=SearchVector('title', weight='A') + SearchVector('text', weight='B'))

        self.stdout.write("Заполнение успешно окончено")