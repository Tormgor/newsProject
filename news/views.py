from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Post, Author, Category, CategorySubscribers, PostCategory
from .filters import PostFilter
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from .forms import CreatePostForm, BasePostForm
from .tasks import new_post_notification
from django.shortcuts import redirect
from django.views.decorators.cache import cache_page


class PostList(ListView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'postList'
    queryset = Post.objects.order_by('-created')
    paginate_by = 4

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        return context


class SearchList(PostList):
    template_name = 'search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context


class PostView(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'postView'

    def get_object(self, *args, **kwargs):
        obj = cache.get(f'post-{self.kwargs["pk"]}', None)

        if not obj:
            obj = super().get_object(**kwargs)
            cache.set(f'post-{self.kwargs["pk"]}', obj)
        return obj


class PostCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',
                           'news.change_post')
    template_name = 'add.html'
    form_class = CreatePostForm

    def post(self, request, *args, **kwargs):
        post = Post(
            id_author=Author.objects.get(id_user=request.user),
            header=request.POST['header'],
            text=request.POST['text']
        )
        post.save()

        for id in request.POST.getlist('category'):
            postCategory = PostCategory(id_post=post, id_category=Category.objects.get(pk=id))
            postCategory.save()

        subject = f'{post.created.strftime("%Y-%M-%d")} вами создана новая новость!'
        content = render_to_string('post_created.html', {'post': post, })
        email = request.user.email

        # Отправка уведомлений о новой статье через Celery
        new_post_notification.delay(subject, email, content)

        return redirect('/news/')


class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    template_name = 'edit.html'
    form_class = BasePostForm

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class PostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    template_name = 'delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'


class SubscriptionView(ListView):
    model = Category
    template_name = 'subscriptions.html'
    context_object_name = 'subscriptionView'
    queryset = Category.objects.order_by('name')
    paginate_by = 4


@login_required
def add_subscribe(request):
    user = request.user
    category = Category.objects.get(pk=request.POST['id_cat'])
    subscribe = CategorySubscribers(id_user=user, id_category=category)
    subscribe.save()

    return redirect('/subscriptions')

