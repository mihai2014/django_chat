from django.shortcuts import render
from django.http import HttpResponseRedirect

from django.contrib.sessions.backends.db import SessionStore

def chat(request):
    return render(request, 'account/base.html', {'chat':"True", 'user': request.user})

def index(request):
    #if str(request.user) != "AnonymousUser":
    #    print(request.user)
    #return render(request, 'home.html', {})
    return render(request, 'account/base.html', {'chat':"welcome"})
    #return HttpResponseRedirect('/accounts/login')

    