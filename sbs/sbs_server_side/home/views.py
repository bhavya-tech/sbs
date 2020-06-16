from django.shortcuts import render

def homePage(request):
    return render(request,'/home_page.html',{})
