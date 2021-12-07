import django_filters
from django import forms
from django_filters import FilterSet
from .models import Post, Author


class PostFilter(FilterSet):
    id_author = django_filters.ModelChoiceFilter(label="Автор", queryset=Author.objects.all())
    created = django_filters.DateFilter(label="Дата публикации", lookup_expr='contains', widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Post
        fields = ['id_author', 'created']
