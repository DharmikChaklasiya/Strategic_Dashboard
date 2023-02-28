from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

def userLogin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/dashboard")
        else:
            var = 'True'
            return render(request, 'registration/login.html', {'var': var})
    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    return redirect("/")

def Registeruser(request):
    if request.method == "POST":
        user=User.objects.create_user(username= request.POST.get('username'),email=request.POST.get('email'),password=request.POST.get('password'))
        user.save()
        return render(request, 'registration/login.html')
    return render(request, 'registration/register.html')
