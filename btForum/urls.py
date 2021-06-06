from django.urls import path

from . import views


urlpatterns = [
    path('login/', views.login, name='login'),
    path('select/', views.select, name='select'),
    path('torrent/<int:torrent_id>/', views.torrent, name='torrent'),
    path('topic/<int:topic_id>/', views.topic, name='topic'),
    path('post/', views.post, name='post'),
    path('upload/', views.upload, name='upload'),
    path('topics/', views.topics, name='topics'),
    path('account/', views.account, name='account'),
    path('search/', views.search, name='search'),
]