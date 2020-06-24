from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from datetime import datetime, date, time
from req.models import Request
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict
from django.db import models
from home.models import Record
import json

@csrf_exempt
def viewRequests(request):
    cleanExpiredRequests()
    dateReq = None
    if request.method == 'GET':
        dateReq = date.today()
    else:
        if 'date' in request.POST:
            try:
                dateReq = request.POST['date']
            except ValueError:
                dateReq = date.today()
        else: 
            dateReq = date.today()

    pendingReq, pendingReqById = getPendingRequest(dateReq)
    json_pending_req = json.dumps(pendingReqById)

    return render(request,'pendingrequest.html',{
                                                    'pendingReq':pendingReq,
                                                    'date':dateReq,
                                                    'dateCal':dateReq.strftime("%Y-%m-%d"),
                                                    'json_pending_req':json_pending_req,
                                                })

def getPendingRequest(dateReq):

    request_query_set = None
    request_query_set = Request.objects.filter(date = dateReq).order_by('room','from_ts')
    req_room_dict = defaultdict(list)
    pendingReq = defaultdict(list)
    pendingReqById = defaultdict(dict)

    for req in request_query_set:
        req_dict = {}
        req_dict["details"] = req.details
        req_dict["event"] = req.event
        req_dict["requested_by"] = req.requested_by
        pendingReqById.update({req.id:req_dict})     

    for req in request_query_set:
        req_room_dict[req.room].append(req)

    for room_key,req_list in req_room_dict.items():
        req_append = []
        to = time(0)
        for req in req_list:
            to = max(req.to_ts,to)
            if req.from_ts < to: 
                req_append.append(req)
            else:
                pendingReq[room_key].append(req_append)
                req_append = []
        
        if len(req_append) is not 0:
            pendingReq[room_key].append(req_append)

    print(pendingReq)
    return dict(pendingReq), dict(pendingReqById)

@csrf_exempt
def makeRequest(request):

    req = Request()

    # Take data for request
    req.room = request.POST['room']
    req.date = datetime.strptime(request.POST['date'], '%Y-%m-%d')
    req.to_ts =  datetime.strptime(request.POST['to'], '%H:%M').time()
    req.from_ts = datetime.strptime(request.POST['from'], '%H:%M').time()
    req.details = request.POST['details']
    req.event = request.POST['event']
    req.requested_by = request.POST.get('username')
    

    # Check over lapping request left
    if overlapping(req):
        return redirect('home:homePage', req_status = 2)    # Overlapped request

    req.save()
    return redirect('home:homePage', req_status = 1) #request successfully made

@csrf_exempt
def requestAction(request):

    req_id = None
    status = None

    if request.method == 'POST':
        status = request.POST['status']
        req_id = request.POST['id']
    else:
        redirect('req:viewRequests')

    if status is 'reject':
        Request.objects.get(id = req_id).delete()
    else:
        try:
            req = Request.objects.get(id = req_id)
        except Request.DoesNotExist:
            req = None
        
        if req is not None:
            print("Calling add")
            rec = reqToRec(req)
            deleteOverlappingReq(req)
            req.delete()
            addRec(rec)

    return  redirect('req:viewRequests')

def addRec(rec = Record()):
    print("AA")
    rec.save()
    return

def overlapping(req = Request()):

    if Request.objects.filter(from_ts__lte = req.from_ts, to_ts__gte = req.to_ts, requested_by = req.requested_by, room = req.room).exists():
        return True
    else:
        return False

def deleteOverlappingReq(req = Request()):
    Request.objects.filter(from_ts__gt = req.from_ts, from_ts__lt = req.to_ts, room = req.room).delete()
    Request.objects.filter(to_ts__lt = req.to_ts, to_ts__gt = req.from_ts, room = req.room).delete()


def cleanExpiredRequests():
    Request.objects.filter(date__lt = date.today(), from_ts__lt = datetime.now().strftime("%H:%M")).delete()

def reqToRec(req = Request()):
    return Record(details = req.details, room = req.room, event = req.event, requested_by = req.requested_by, date = req.date, from_ts = req.from_ts, to_ts = req.to_ts)