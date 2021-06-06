from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.db.models import Sum, Avg
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

# Create your views here.

from .models import User, Topic, Category, Torrent, Rate, Reply,DownloadRecord,rateStatistic,temp

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

def setUid(uid):
    tmp = temp.objects.first()
    tmp.uid = uid
    tmp.save()

def getUid():
    return temp.objects.first().uid


LEVELS=[
    {"up": 100000000, "ratio": 1},
    {"up": 100000, "ratio": 0.25},
    {"up": 3500, "ratio": 0.2},
    {"up": 200, "ratio": 0.1},
    {"up": 10, "ratio": 0},
    {"up": 0, "ratio": 0},
]

def updatePrivilege(user):
    up=user.totUp
    down=user.totDown
    ratio=up/down if down>0 else 0
    privilege=user.privilege-1
    for i in range(privilege,0,-1):
        if up>=LEVELS[i]["up"] and ratio>=LEVELS[i]["ratio"]:
            user.privilege=i
    user.save()

@csrf_exempt
def search(request):
    try:
        data = json.loads(request.body)
        topics=Topic.objects.filter(title__contains=data['searchstring'])
        topics=list(topics.order_by('time').values())[::-1]
        return MessageResponse('success',{'topics': topics, 'totPage': 1})
    except:
        return MessageResponse('method_error',{})


@csrf_exempt
def login(request):
    if request.method == 'GET':
        setUid(0)
        return MessageResponse('success',{})
    elif request.method == 'POST':
        data = json.loads(request.body)
        name = data['uname']
        password = data['password']
        try:
            user = User.objects.get(name=name)
            if user.password == password:
                setUid(user.id)
                return MessageResponse('success', {})
                # return CookieRedirect('/select', user.id)
            # return MessageResponse('success',{'uid':user.id})
            else:
                return MessageResponse('user_error', {})
        except:
            return MessageResponse('user_error', {})

@csrf_exempt
def account(request):
    uid=getUid()
    try:
        user = User.objects.get(id=uid)
    except:
        return MessageResponse("user_error",{})
    return MessageResponse('success',{
        'name': user.name,
        'totUp': user.totUp,
        'totDown': user.totDown,
        'privilege': user.privilege,
    })


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
    try:
        data = json.loads(request.body)
        categories = data['categories']
        page=data['page']
        print(categories)
        topics = Topic.objects.filter(torrent__category__name__in=categories).distinct()
        # topics = Topic.objects.filter(torrent__category__in=[1,2]).distinct()
        # topics = Topic.objects.filter(torrent__in=[8,9]).distinct()
        # print(Topic.objects.all().values())
        # print(topics.values())
        totPage=((topics.count()-1)//10)+1
        # topics=list(topics.order_by('time')[(page-1)*10:page*10].values())[::-1]
        topics=list(topics.order_by('time').values())[::-1]
        print(categories)
        return MessageResponse('success',{'topics': topics, 'totPage': totPage})
    except:
        return MessageResponse('method_error',{})



@csrf_exempt
def torrent(request, torrent_id):
    # uid = request.get_signed_cookie('user', salt='bt')
    uid=getUid()
    torrent = Torrent.objects.get(id=torrent_id)
    try:
        user = User.objects.get(id=uid)
    except:
        return MessageResponse("user_error",{})

    try:
        if request.method == "POST":
            data = json.loads(request.body)
            if data['method'] == 'rate':
                if Rate.objects.filter(user_id=uid,torrent_id=torrent_id).exists():
                    rate=Rate.objects.get(user_id=uid,torrent_id=torrent_id)
                    rate.content=data['content']
                    rate.score=data['score']
                    rate.time=timezone.now()
                    rate.save()

                else:
                    rate = Rate(content=data['content'], score=data['score'], torrent=torrent, user=user)
                    rate.save()

            elif data['method'] == 'download':
                if {'id':uid} not in list(torrent.downloadUsers.values('id')):
                    downloadRecord=DownloadRecord(user=user,torrent=torrent)
                    downloadRecord.save()
                    updatePrivilege(user)
                # return CookieResponse({'result': 'success'}, uid)
                # return MessageResponse('success',{})

        rates = Rate.objects.filter(torrent=torrent_id)
        ratestats=[{"minimum":None,"maximum":None,"average":None,"min7":None,"max7":None,"avg7":None}]
        if rates.exists():
            ratestats=list( rateStatistic.objects.filter(torrent_id=torrent_id).values())
        print(rates.values())
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
    except:
        return MessageResponse('method_error',{})


@csrf_exempt
def topic(request, topic_id):
    # uid = request.get_signed_cookie('user', salt='bt')
    uid=getUid()
    topic = Topic.objects.get(id=topic_id)
    try:
        user = User.objects.get(id=uid)
    except:
        return MessageResponse("user_error",{})
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            # if data['method'] == 'reply':
            reply = Reply(content=data['content'], user=user, topic=topic)
            reply.save()
            # elif data['method'] == 'detail':
            #     torrent_id = data['torrent_id']
            #     # return CookieRedirect('/torrents/' + str(torrent_id), uid)
            # return MessageResponse('success',{})

        dict = {
            'title': topic.title,
            'content': topic.content,
            'time': topic.time,
            'publishedByUser': topic.user.name,
            'torrents': list(Torrent.objects.filter(inTopics=topic_id,permission__gte=user.privilege).values('id','name', 'score')),
            'replies': list(Reply.objects.filter(topic=topic_id).order_by('time').values('user__name', 'content', 'time'))
        }
        # return CookieResponse(dict, uid)
        return MessageResponse('success',dict)
    except:
        return MessageResponse('method_error',{})


@csrf_exempt
def upload(request):
    # uid = request.get_signed_cookie('user', salt='bt')
    uid=getUid()
    try:
        user = User.objects.get(id=uid)
    except:
        return MessageResponse("user_error",{})
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            torrent = Torrent(name=data['name'],link=data['link'], permission=6-data['permission'], size=float( data['size']), uploadUser=user)
            torrent.save()
            categories=Category.objects.filter(name__in=data['categories']).values('id')
            categories=[rec['id'] for rec in categories]
            print(categories)
            torrent.category.add(*categories)
            torrent.save()
            user.totUp+=user.totUp+float(data['size'])
            user.save()
            updatePrivilege(user)
            # return CookieResponse({'result': 'success'}, uid)
            # return MessageResponse('success', {})

        categories = list(Category.objects.all().values('name'))
        categories = [item['name'] for item in categories]
        # response = JsonResponse({'topics': topics})
        # response.set_signed_cookie('user', uid, max_age=60 * 60 * 12, salt='bt')
        # return response
        return MessageResponse('success',{'categories': categories})
    except:
        return MessageResponse('method_error',{})



@csrf_exempt
def post(request):
    # uid = request.get_signed_cookie('user', salt='bt')
    uid=getUid()
    try:
        user = User.objects.get(id=uid)
    except:
        return MessageResponse("user_error",{})
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            topic = Topic(title=data['title'], content=data['content'], user=user)
            topic.save()
            torrent_ids=list(map(int,str(data['torrent_ids']).split(',')))
            topic.torrent_set.add(*torrent_ids)
            topic.save()
            return MessageResponse('success', {})
            # return CookieResponse({'result': 'success'}, uid)

        # return CookieResponse({}, uid)
        return MessageResponse('success',{})
    except:
        return MessageResponse('method_error',{})
