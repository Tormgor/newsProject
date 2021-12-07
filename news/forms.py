from django import forms
from .models import Post, Author, Category


class BasePostForm(forms.ModelForm):
    header = forms.CharField(label="Заголовок", widget=forms.TextInput(attrs={"style": "width:100%"}))
    text = forms.CharField(label="Текст", widget=forms.Textarea(attrs={"style": "width:100%"}))

    class Meta:
        model = Post
        fields = ['header', 'text']


class CreatePostForm(BasePostForm):
    category = forms.ModelMultipleChoiceField(label="Категория", queryset=Category.objects.all(), widget=forms.SelectMultiple(attrs={"style": "width:100%"}))

    class Meta:
        model = Post
        fields = ['header', 'text', 'category']
