from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login

from .forms import LoginForm, UserRegistrationForm


def user_login(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        cd = form.cleaned_data
        user = authenticate(request,
                            username=cd['username'],
                            password=cd['password'])

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("inventory:categories")
            else:
                return HttpResponse('Disabled account')
        else:
            return HttpResponse('Invalid logins')
    return render(request, 'registration/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(
                user_form.cleaned_data['password']
            )
            new_user.save()

            return render(request,
                          'users/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'users/register.html',
                  {'user_form': user_form})
