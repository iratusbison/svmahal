from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views, get_user
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .models import TSUser


def index(request):
    return render(request, 'core/index.html')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .models import TSUser

def login(request):
    if request.method == 'POST':
        auth_logout(request)
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            # Access the associated TSUser object directly from the authenticated user
            try:
                tsuser = user.tsuser
                request.session['ts_user'] = {
                    'major': tsuser.major_string(),
                    'role': tsuser.role_string(),
                    'major_short': tsuser.major,
                    'role_short': tsuser.role,
                    'is_admin': tsuser.is_admin(),
                }

                auth_login(request, user)
                return redirect('/dashboard/')
            except TSUser.DoesNotExist:
                return render(request, 'core/login.html', {'error': True})
        else:
            return render(request, 'core/login.html', {'error': True})
    else:
        if request.user.is_authenticated:
            return redirect('/dashboard/')
        return render(request, 'core/login.html')


def logout(request):
    auth_logout(request)
    return redirect('/')


@login_required(login_url='/login')
def dashboard(request):

    
    return render(request, 'core/dashboard.html')

@login_required(login_url='/login')
def profile(request):
    # TODO create profile template
    return render(request, 'core/dashboard.html')

