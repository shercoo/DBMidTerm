from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.db.models import Sum, Avg
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.

from .models import User, Topic, Category, Torrent, Rate, Reply,DownloadRecord,rateStatistic

CODE = {
    "success": 200,
    "database_error": 300,
    "user_error": 400,
    "method_error": 600,
    "parameter_error": 700,
}

def CookieResponse(dict, uid):
    response = JsonResponse(dict)
    response.set_signed_cookie('user', uid, max_age=60 * 60 * 12, salt='bt')
    return response


def CookieRedirect(path, uid):
    response = HttpResponseRedirect(path)
    response.set_signed_cookie('user', uid, max_age=60 * 60 * 12, salt='bt')
    return response

def MessageResponse(msg,dict):
    dict['msg']=msg
    return JsonResponse({'code':CODE[msg],'data':dict})

@csrf_exempt
def login(request):
    if request.method == 'GET':
        users = User.objects.all()
        # template=loader.get_template('btForum/login.html')
        # context={'users':users}
        # return HttpResponse(template.render(context,request))
        # return JsonResponse({'users': list(users.values())})
        return MessageResponse('success',{})
    elif request.method == 'POST':
        data = json.loads(request.body)
        name = data['uname']
        password = data['password']
        try:
            user = User.objects.get(name=name)
            if user.password == password:
                return CookieRedirect('/select', user.id)
            # return MessageResponse('success',{'uid':user.id})
            else:
                return MessageResponse('user_error', {})
        except:
            return MessageResponse('user_error', {})


@csrf_exempt
def select(request):
    categories = list(Category.objects.all().values('name'))
    categories = [item['name'] for item in categories]
    # response = JsonResponse({'topics': topics})
    # response.set_signed_cookie('user', uid, max_age=60 * 60 * 12, salt='bt')
    # return response
    return MessageResponse('success',{'categories': categories})

@csrf_exempt
def topics(request):
    uid = request.get_signed_cookie('user', salt='bt')
    user = User.objects.get(id=uid)
    # if request.method == 'POST':
    data = json.loads(request.body)
    categories = data['categories']
    print(categories)
    topics = list(Topic.objects.filter(torrent__category__in=categories).values().distinct().order_by('time'))
    return MessageResponse('success',{'topics': topics})



@csrf_exempt
def torrent(request, torrent_id):
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
                downloadRecord=DownloadRecord(user=user,torrent=torrent)
                downloadRecord.save()
            # return CookieResponse({'result': 'success'}, uid)
            return MessageResponse('success',{})

    rates = Rate.objects.filter(torrent=torrent_id)
    ratestats=list( rateStatistic.objects.filter(torrent_id=torrent_id).values())
    print(ratestats)
    dict = {
        'name': torrent.name,
        'link': torrent.link,
        'time': torrent.time,
        'count': torrent.count,
        'size': torrent.size,
        'ratestats': ratestats,
        'uploadByUser': torrent.uploadUser.name,
        'categories': list(Category.objects.filter(torrent=torrent_id).values()),
        'rates': list(rates.values('score', 'content', 'user__name'))
    }
    # return CookieResponse(dict, uid)
    return MessageResponse('success',dict)


@csrf_exempt
def topic(request, topic_id):
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
            # return CookieRedirect('/torrents/' + str(torrent_id), uid)
            return MessageResponse('success',{})

    dict = {
        'title': topic.title,
        'content': topic.content,
        'time': topic.time,
        'publishedByUser': topic.user.name,
        'torrents': list(Torrent.objects.filter(inTopics=topic_id,permission__gte=user.privilege).values('id','name', 'score')),
        'replies': list(Reply.objects.filter(topic=topic_id).values('user__name', 'content', 'time'))
    }
    # return CookieResponse(dict, uid)
    return MessageResponse('success',dict)


@csrf_exempt
def upload(request):
    uid = request.get_signed_cookie('user', salt='bt')
    user = User.objects.get(id=uid)
    if request.method == 'POST':
        data = json.loads(request.body)
        torrent = Torrent(link=data['link'], permission=data['permission'], size=data['size'], uploadUser=user)
        torrent.save()
        torrent.category.add(*data['categories'])
        torrent.save()
        # return CookieResponse({'result': 'success'}, uid)
        return MessageResponse('success', {})

    # return CookieResponse({}, uid)
    return MessageResponse('success',{})


@csrf_exempt
def post(request):
    uid = request.get_signed_cookie('user', salt='bt')
    user = User.objects.get(id=uid)
    if request.method == 'POST':
        data = json.loads(request.body)
        topic = Topic(title=data['title'], content=data['content'], user=user)
        topic.save()
        topic.torrent_set.add(*data['torrent_ids'])
        topic.save()
        return MessageResponse('success', {})
        # return CookieResponse({'result': 'success'}, uid)

    # return CookieResponse({}, uid)
    return MessageResponse('success',{})
