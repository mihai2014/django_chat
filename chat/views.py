from django.shortcuts import render
from django.http import HttpResponseRedirect

#from .forms import SelectGroupForm


n = 0

from django.contrib.sessions.backends.db import SessionStore

def chat(request):
    global n

    s = SessionStore()
    #s['last_login'] = 1376587691
    #s.create()
    #print(s.session_key)
    #s = SessionStore(session_key=s.session_key)
    #s = Session.objects.get(pk='2b1189a188b44ad18c35e113ac6ceead')

    #return render(request, 'chat/chat.html', {})
    #print(request.user)
    #if request.session.has_key('page'):
    #    page = request.session['page']
    #    print('page nr', n)
    #else:        
    #    request.session['page'] = str(n)
    #    n = n + 1 
    #    print(n)

    return render(request, 'account/base.html', {'chat':"True", 'user': request.user})

def index(request):
    #if str(request.user) != "AnonymousUser":
    #    print(request.user)
    #return render(request, 'home.html', {})
    return render(request, 'account/base.html', {'chat':"welcome"})
    #return HttpResponseRedirect('/accounts/login')