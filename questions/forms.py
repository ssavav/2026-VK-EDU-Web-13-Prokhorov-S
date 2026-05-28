from django import forms
from .models import Question, Answer, Tag, QuestionLike, AnswerLike

class AskForm(forms.ModelForm):
    tags_input = forms.CharField(
        label='Tags', 
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control ask-area', 
            'placeholder': 'Enter your tags here...(comma-separated listing)'
        })
    )

    class Meta:
        model = Question
        fields = ['title', 'text']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control ask-area', 
                'placeholder': 'Enter title here...(max. 255 characters)'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control ask-area', 
                'rows': 15,
                'placeholder': 'Enter your question here...'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        question = super().save(commit=False)
        question.author = self.author
        
        if commit:
            question.save()
            tags_str = self.cleaned_data.get('tags_input', '')
            if tags_str:
                tag_names =[t.strip() for t in tags_str.split(',') if t.strip()]
                tag_objs =[]
                for name in tag_names:
                    tag_obj, created = Tag.objects.get_or_create(name=name)
                    tag_objs.append(tag_obj)
                question.tags.set(tag_objs)
                
        return question
    
    def clean_tags_input(self):
        tags_str = self.cleaned_data.get('tags_input', '')
        if tags_str:
            tag_names = [t.strip() for t in tags_str.split(',') if t.strip()]
            for name in tag_names:
                if len(name) > 50:
                    raise forms.ValidationError(f"Tag is too long (max. 50 chars)")
        return tags_str


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control answer-area', 'rows': 5, 'placeholder': 'Enter your answer here...(max. 1000 characters)'}),
        }

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author', None)
        self.question_obj = kwargs.pop('question_obj', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        answer = super().save(commit=False)
        answer.author = self.author
        answer.question = self.question_obj
        if commit:
            answer.save()
        return answer

class QuestionVoteForm(forms.Form):
    question_id = forms.ModelChoiceField(queryset=Question.objects.all())
    action = forms.ChoiceField(choices=[('like', 'like'), ('dislike', 'dislike')])

    def save(self, user):
        question = self.cleaned_data['question_id']
        value = 1 if self.cleaned_data['action'] == 'like' else -1

        vote, created = QuestionLike.objects.get_or_create(
            user=user, question=question, defaults={'value': value}
        )
        
        if not created and vote.value != value:
            vote.value = value
            vote.save(update_fields=['value'])
        elif not created and vote.value == value:
            vote.delete()
            
        question.update_rating()
        return question.rating

class AnswerVoteForm(forms.Form):
    answer_id = forms.ModelChoiceField(queryset=Answer.objects.all())
    action = forms.ChoiceField(choices=[('like', 'like'), ('dislike', 'dislike')])

    def save(self, user):
        answer = self.cleaned_data['answer_id']
        value = 1 if self.cleaned_data['action'] == 'like' else -1

        vote, created = AnswerLike.objects.get_or_create(
            user=user, answer=answer, defaults={'value': value}
        )
        
        if not created and vote.value != value:
            vote.value = value
            vote.save(update_fields=['value'])
        elif not created and vote.value == value:
            vote.delete()
            
        answer.update_rating()
        return answer.rating

class MarkCorrectForm(forms.Form):
    question_id = forms.ModelChoiceField(queryset=Question.objects.all())
    answer_id = forms.ModelChoiceField(queryset=Answer.objects.all())

    def save(self, user):
        question = self.cleaned_data['question_id']
        answer = self.cleaned_data['answer_id']

        if user != question.author:
            raise forms.ValidationError("Permission denied: You are not the author.")
        if answer.question != question:
            raise forms.ValidationError("Answer does not belong to this question.")

        answer.is_correct = not answer.is_correct
        answer.save(update_fields=['is_correct'])
        return answer.is_correct