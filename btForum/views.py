from django.shortcuts import render
from django.http import HttpRequest,HttpResponse,HttpResponseRedirect,JsonResponse
from django.template import loader
import json

# Create your views here.

from .models import User,Topic,Category,Torrent

def login(request):
    if request.method=='GET':
        users=User.objects.all()
        # template=loader.get_template('btForum/login.html')
        # context={'users':users}
        # return HttpResponse(template.render(context,request))
        return JsonResponse({'users':list(users.values())})
    elif request.method=='POST':
        data=json.loads(request.body)
        name=data['uname']
        password=data['password']
        print(name)
        print(password)
        if User.objects.get(name=name).password==password:
            response=HttpResponseRedirect('/select')
            response.set_signed_cookie('user', name, max_age=60 * 60 * 12,salt='bt')
            return response


def select(request):
    categorys=Category.objects.all().values('id')
    print(categorys)
    name=request.get_signed_cookie('user',salt='bt')
    print("select:::"+name)
    user=User.objects.get(name=name)
    if request.method=='POST':
        data=json.loads(request.body)
        categorys=data['categorys']
    topics=list( Topic.objects.filter(torrent__category__in=[1]).values().distinct())
    response=JsonResponse({'topics':topics})
    response.set_signed_cookie('user',name,max_age=60*60*12,salt='bt')
    return response

