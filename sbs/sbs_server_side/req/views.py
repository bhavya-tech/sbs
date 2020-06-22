from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from datetime import datetime, date, time
from req.models import Request
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict

def viewRequests(request):
    cleanExpiredRequests()

    dateReq = None
    if request.method == 'GET':
        dateReq = date.today()
    else:
        if 'date' in request.POST:
            try:
                dateReq =  datetime.datetime.strptime(request.POST['date'], "%d/%m/%Y")
            except ValueError:
                dateReq = date.today()
        else:
            dateReq = date.today()

    pendingReq = defaultdict(list)
    pendingReq = dict(getPendingRequest(dateReq))

    return  render(request, 'pendingrequest.html',{'pendingReq':pendingReq})


def getPendingRequest(dateReq):

    request_query_set = None
    request_query_set = Request.objects.filter(date = dateReq).order_by('room','from_ts')
    req_room_dict = defaultdict(list)
    pendingReq = defaultdict(list)

    for req in request_query_set:
        req_room_dict[req.room].append(req)

    for room_key,req_list in req_room_dict.items():
        req_append = []
        to = time(23,59)
        for req in req_list:
            to = req.to_ts
            if req.from_ts < to: 
                req_append.append(req)
            else:
                pendingReq[room_key].append(req_append)
                req_append = []
        pendingReq[room_key].append(req_append)


    return pendingReq

@csrf_exempt
def makeRequest(request):

    req = Request()

    # Take data for request
    req.room = request.POST['room']
    req.date =  datetime.strptime(request.POST['date'], "%d/%m/%Y")
    req.to_ts =  datetime.strptime(request.POST['to'], '%H:%M').time()
    req.from_ts = datetime.strptime(request.POST['from'], '%H:%M').time()
    req.details = request.POST['details']
    req.event = request.POST['event']
    user = request.POST.get('user')
    req.requested_by = user.username


    # Check over lapping request left
    if overlapping(req):
        return redirect('home:homePage', req_status = 2)    # Overlapped request

    req.save()
    return redirect('home:homePage', req_status = 1) #request successfully made

def overlapping(req = Request()):

    if Request.objects.filter(from_ts__lte = req.from_ts, to_ts__gte = req.to_ts, requested_by = req.requested_by, room = req.room).exists():
        return True
    else:
        return False

def cleanExpiredRequests():
    Request.objects.filter(date__lt = date.today(), from_ts__lt = datetime.now().strftime("%H:%M"))