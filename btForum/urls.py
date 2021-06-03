from django.urls import path

from . import views


urlpatterns = [
    path('login/', views.login, name='login'),
    path('select/', views.select, name='select'),
    path('torrents/<int:torrent_id>/', views.torrents, name='torrents'),
    path('topics/<int:topic_id>/', views.topics, name='topics'),
    path('post/', views.post, name='post'),
    path('upload/', views.upload, name='upload'),
]