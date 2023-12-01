from django.shortcuts import render,redirect
from django.views.generic import View
from todoapp.forms import UserForm,LoginForm,TodoForm
from django.contrib.auth import authenticate,login,logout
from todoapp.models import Todos
from django.contrib import messages
from django.utils.decorators import method_decorator

def signin_required(fn):
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:
            return redirect("signin")
        else:
            return fn(request,*args,**kwargs)
    return wrapper

def owner_permission(fn):
    def wrapper(request,*args,**kwargs):
        id=kwargs.get("pk")
        obj=Todos.objects.get(id=id)
        if obj.user != request.user:
            logout (request)
            return redirect ("signin")
        else:
            return fn(request,*args,**kwargs)
    return wrapper
# Create your views here.
decs=[signin_required,owner_permission]

class RegistrationView(View):
    def get(self,request,*args,**kwargs):
        form=UserForm()
        return render(request,"register.html",{"form":form})
    def post(self,request,*args,**kwargs):
        form=UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("signin")
        else:
            return render(request,"register.html",{"form":form})
        
class SignInView(View):
    def get(self,request,*args,**kwargs):
        form=LoginForm()
        return render(request,"signin.html",{"form":form})
    def post(self,request,*args,**kwargs):
        form=LoginForm(request.POST)
        if form.is_valid():
            uname=request.POST.get("username")
            pwd=request.POST.get("password")
            usr_object=authenticate(request,username=uname,password=pwd)
            if usr_object:
                login(request,usr_object)
                return redirect("index")
        messages.error(request,"Username or password is incorrect")
        return render(request,"signin.html",{"form":form})
        
@method_decorator(signin_required,name="dispatch")
class LogoutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect("signin")

@method_decorator(signin_required,name="dispatch")
class IndexView(View):
    def get(self,request,*args,**kwargs):
        form=TodoForm()
        qs=Todos.objects.filter(user=request.user)
        pending_count=Todos.objects.filter(status="todo",user=request.user).count()
        progress_count=Todos.objects.filter(status="inprogress",user=request.user).count()
        done_count=Todos.objects.filter(status="completed",user=request.user).count()
        return render(request,"index.html",{
            "form":form,
            "data":qs,
            "pending":pending_count,
            "progress":progress_count,
            "done":done_count
            })
    def post(self,request,*args,**kwargs):
        form=TodoForm(request.POST)
        if form.is_valid():
            form.instance.user=request.user
            form.save()
            return redirect("index")
        else:
            return render(request,"index.html",{"form":form})
        
@method_decorator(decs,name="dispatch")  
class TodoUpdate(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        if "status" in request.GET:
            value=request.GET.get("status")
            if value=="inprogress":
                Todos.objects.filter(id=id).update(status="inprogress")
            elif value=="completed":
                Todos.objects.filter(id=id).update(status="completed")
        return redirect("index")
    
@method_decorator(decs,name="dispatch")
class TodoDeleteView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        Todos.objects.filter(id=id).delete()
        return redirect("index")
