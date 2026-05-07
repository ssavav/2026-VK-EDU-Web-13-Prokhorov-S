from django import forms
from .models import Question, Answer, Tag

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