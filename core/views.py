from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, RegisterForm, ProfileSettingsForm

def login(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            auth_login(request, user)

            next_url = request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure()
            ):
                return redirect(next_url)
            return redirect('index')
    else:
        form = LoginForm()

    return render(request, 'core/login.html', {'form': form})


def signup(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()

    return render(request, 'core/signup.html', {'form': form})


@login_required(login_url='login')
def profile(request):
    if request.method == 'POST':
        form = ProfileSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('settings') 
    else:
        form = ProfileSettingsForm(instance=request.user)

    return render(request, 'core/profile.html', {'form': form})


def logout_view(request):
    auth_logout(request)
    next_page = request.META.get('HTTP_REFERER', '/')
    return redirect(next_page)