from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def home_page(request):
    if request.method=='POST':
        code=request.POST['code']
        return redirect("meeting/?roomID="+code)
    return render(request,'home.html')

def video_call(request):
    return render(request,'mainp.html',{'name':request.user.first_name})