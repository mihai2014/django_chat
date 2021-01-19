from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import SelectGroup


def chat(request):
    #return render(request, 'chat/chat.html', {})
    
    return render(request, 'account/base.html', {'chat':"True", "form_group": SelectGroup})

def index(request):
    #if str(request.user) != "AnonymousUser":
    #    print(request.user)
    #return render(request, 'home.html', {})
    return render(request, 'account/base.html', {'chat':"False"})
    #return HttpResponseRedirect('/accounts/login')

