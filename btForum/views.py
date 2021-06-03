from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.db.models import Sum, Avg
import json

# Create your views here.

from .models import User, Topic, Category, Torrent, Rate, Reply


def CookieResponse(dict, uid):
    response = JsonResponse(dict)
    response.set_signed_cookie('user', uid, max_age=60 * 60 * 12, salt='bt')
    return response


def CookieRedirect(path, uid):
    response = HttpResponseRedirect(path)
    response.set_signed_cookie('user', uid, max_age=60 * 60 * 12, salt='bt')
    return response


def login(request):
    if request.method == 'GET':
        users = User.objects.all()
        # template=loader.get_template('btForum/login.html')
        # context={'users':users}
        # return HttpResponse(template.render(context,request))
        return JsonResponse({'users': list(users.values())})
    elif request.method == 'POST':
        data = json.loads(request.body)
        name = data['uname']
        password = data['password']
        user = User.objects.get(name=name)
        if user.password == password:
            return CookieRedirect('/select', user.id)


def select(request):
    categorys = list(Category.objects.all().values('id'))
    categorys = [item['id'] for item in categorys]
    uid = request.get_signed_cookie('user', salt='bt')
    user = User.objects.get(id=uid)
    if request.method == 'POST':
        data = json.loads(request.body)
        categorys = data['categorys']
    print(categorys)
    topics = list(Topic.objects.filter(torrent__category__in=categorys).values().distinct())
    response = JsonResponse({'topics': topics})
    response.set_signed_cookie('user', uid, max_age=60 * 60 * 12, salt='bt')
    return response


def torrents(request, torrent_id):
    uid = request.get_signed_cookie('user', salt='bt')
    torrent = Torrent.objects.get(id=torrent_id)
    user = User.objects.get(id=uid)
    if request.method == "POST":
        data = json.loads(request.body)
        if data['method'] == 'rate':
            rate = Rate(content=data['content'], score=data['score'], torrent=torrent, user=user)
            rate.save()

        elif data['method'] == 'download':
            if uid not in list(torrent.downloadUsers.values('id')):
                torrent = Torrent.objects.get(torrent_id)
                torrent.downloadUsers.add(uid)
                torrent.count = torrent.count + 1
                torrent.save()
                user = User.objects.get(uid)
                user.totDown = user.totDown + torrent.size
                user.save()
            return CookieResponse({'result': 'success'}, uid)

    rates = Rate.objects.filter(torrent=torrent_id)
    score = rates.aggregate(avg=Avg('score'))['avg']
    torrent.score = score
    torrent.save()
    dict = {
        'name': torrent.name,
        'link': torrent.link,
        'time': torrent.time,
        'count': torrent.count,
        'size': torrent.size,
        'score': torrent.score,
        'uploadByUser': torrent.uploadUser.name,
        'categories': list(Category.objects.filter(torrent=torrent_id).values()),
        'rates': list(rates.values('score', 'content', 'user__name'))
    }
    return CookieResponse(dict, uid)


def topics(request, topic_id):
    uid = request.get_signed_cookie('user', salt='bt')
    topic = Topic.objects.get(id=topic_id)
    user = User.objects.get(id=uid)
    if request.method == 'POST':
        data = json.loads(request.body)
        if data['method'] == 'reply':
            reply = Reply(content=data['content'], user=user, topic=topic)
            reply.save()
        elif data['method'] == 'detail':
            torrent_id = data['torrent_id']
            return CookieRedirect('/torrents/' + str(torrent_id), uid)

    dict = {
        'title': topic.title,
        'content': topic.content,
        'time': topic.time,
        'publishedByUser': topic.user.name,
        'torrents': list(Torrent.objects.filter(inTopics=topic_id,permission__gte=user.privilege).values('id','name', 'score')),
        'replies': list(Reply.objects.filter(topic=topic_id).values('user__name', 'content', 'time'))
    }
    return CookieResponse(dict, uid)


def upload(request):
    uid = request.get_signed_cookie('user', salt='bt')
    user = User.objects.get(id=uid)
    if request.method == 'POST':
        data = json.loads(request.body)
        torrent = Torrent(link=data['link'], permission=data['permission'], size=data['size'], uploadUser=user)
        torrent.save()
        torrent.category.add(*data['categories'])
        torrent.save()
        return CookieResponse({'result': 'success'}, uid)

    return CookieResponse({}, uid)


def post(request):
    uid = request.get_signed_cookie('user', salt='bt')
    user = User.objects.get(id=uid)
    if request.method == 'POST':
        data = json.loads(request.body)
        topic = Topic(title=data['title'], content=data['content'], user=user)
        topic.save()
        topic.torrent_set.add(*data['torrent_ids'])
        topic.save()
        return CookieResponse({'result': 'success'}, uid)

    return CookieResponse({}, uid)
