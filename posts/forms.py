from django import forms
from django.forms.widgets import Textarea

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text']
        widgets = {'text': Textarea(attrs={'placeholder': 'Введите текст'})}
        error_messages = {'text': {'required': 'Пост обязательно должен '
                                               'содержать текст!'}}

    def clean_text(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError('Пост не должен быть пустым!')
        return data
