from django.contrib.auth.models import User, Group
from django.apps import apps
from django.views.generic.edit import CreateView
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .forms import BaseRegisterForm


class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/news/'


@login_required
def become_author(request):
    user = request.user
    authors = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors.user_set.add(user)
        author = apps.get_model('news', 'Author')()
        author.id_user = user
        author.save()

    return redirect('/')