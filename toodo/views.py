from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'toodo/home.html')

def signupuser(request):
    if request.method == 'GET':
        return render(request, 'toodo/signupuser.html', {'form':UserCreationForm()})
    else:
        # create new User
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodo')
            except IntegrityError:
                return render(request, 'toodo/signupuser.html', {'form':UserCreationForm(), 'error': 'Username unavailbable. Please choose new username'})
        else:
            return render(request, 'toodo/signupuser.html', {'form':UserCreationForm(), 'error': 'Passwords did not match'})
            #return error message

def loginuser(request):
    if request.method == 'GET':
        return render(request, 'toodo/loginuser.html', {'form':AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'], )
        if user == None:
            return render(request, 'toodo/loginuser.html', {'form':AuthenticationForm(), 'error': 'Invalid Username/Password. Please try again'})
        else:
            login(request, user)
            return redirect('currenttodo')

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

@login_required
def currenttodo(request):
    todos = Todo.objects.filter(user=request.user, date_completed__isnull=True)
    return render(request, 'toodo/currenttodo.html', {'todos':todos})

@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'toodo/createtodo.html', {'form':TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodo')
        except ValueError:
            return render(request, 'toodo/createtodo.html', {'form':TodoForm(), 'error': 'Bad Data passed in'})

@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'toodo/viewtodo.html', {'todo':todo, 'form':form})
    else:
        try:
            form = TodoForm(request.POST,instance=todo)
            form.save()
            return redirect('currenttodo')
        except ValueError:
            return render(request, 'toodo/viewtodo.html', {'todo':todo, 'form':form, 'error': 'Try Again'})

@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.date_completed= timezone.now()
        todo.save()
        return redirect('currenttodo')

@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodo')

@login_required
def completedtodo(request):
    todos = Todo.objects.filter(user=request.user, date_completed__isnull=False).order_by('-date_completed')
    return render(request, 'toodo/completedtodo.html', {'todos':todos})
