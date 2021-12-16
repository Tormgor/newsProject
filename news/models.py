from django.db import models
from django.contrib.auth.models import User
from django.core.cache import cache


class Author(models.Model):
    id_user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        result = 0
        user = self.id_user

        post_list = Post.objects.filter(id_author=self, type=Post.article)

        post_rating_list = post_list.values("rating")
        result = 3 * (sum(item["rating"] for item in post_rating_list))

        comment_rating_list = Comment.objects.filter(id_user=user).values("rating")
        result += sum(item["rating"] for item in comment_rating_list)

        for post in post_list:
            comment_in_post = Comment.objects.filter(id_post=post).values("rating")
            result += sum(item["rating"] for item in comment_in_post)

        self.rating = result
        self.save()

    def __str__(self):
        return self.id_user.username


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    subscribers = models.ManyToManyField(User, through="CategorySubscribers")

    def __str__(self):
        return self.name

    @property
    def is_subscribed(self):
        return CategorySubscribers.objects.filter(id_category=self.pk).exists()


class CategorySubscribers(models.Model):
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Post(models.Model):
    article = "AR"
    news = "NW"
    POST_TYPE = [(article, 'Статья'), (news, 'Новость')]

    id_author = models.ForeignKey(Author, on_delete=models.CASCADE)
    type = models.CharField(max_length=2, choices=POST_TYPE, default=article)
    created = models.DateTimeField(auto_now_add=True)
    id_post_category = models.ManyToManyField(Category, through="PostCategory")
    header = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        result = self.text[:124] + "..."
        return result

    def get_absolute_url(self):
        return f'/post/{self.id}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'post-{self.pk}')


class PostCategory(models.Model):
    id_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    id_category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    id_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    rating = models.IntegerField()

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()
