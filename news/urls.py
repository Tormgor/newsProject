from django.urls import path
from .views import *

urlpatterns = [
    path('', PostList.as_view()),
    path('search', SearchList.as_view()),
    path('<int:pk>', PostView.as_view()),
    path('add', PostCreateView.as_view()),
    path('edit/<int:pk>', PostUpdateView.as_view()),
    path('delete/<int:pk>', PostDeleteView.as_view()),
    path('subscriptions', SubscriptionView.as_view()),
    path('subscribe', add_subscribe),
]
