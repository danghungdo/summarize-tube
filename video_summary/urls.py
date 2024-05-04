from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.user_login, name='login'),
    path('signup', views.user_signup, name='signup'),
    path('logout', views.user_logout, name='logout'),
    path('summarize', views.summarize, name='summarize'),
    path('history', views.history, name='history'),
    path('detail/<int:summary_id>', views.show_detail, name='detail'),
]
