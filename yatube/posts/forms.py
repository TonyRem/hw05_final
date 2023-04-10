from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
            'image': 'Картинка'
        }
        widgets = {'text': forms.Textarea(attrs={'rows': 3})}


class SearchForm(forms.Form):
    query = forms.CharField()


class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = Comment
        fields = ('text',)
