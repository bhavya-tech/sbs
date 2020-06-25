from django.shortcuts import render, redirect
from home.models import Record, Rooms
from datetime import date, datetime, time
import time as t
from collections import defaultdict 
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models import Q
import json

'''
request.user.is_staff to know if is admin
'''


"""
req_status      meaning
0               None
1               Successfully requested
2               overlapped request
"""
@csrf_exempt
def homePage(request,req_status):
    room,_from,to,datereq,todt,_fromdt = parseRequest(request)
    empty_slots = generateEmptySlots(room,_from,to,datereq)
    empty_slots = dict(empty_slots)
    #print(empty_slots)
    return  render(request, 'home_page.html',
                                            {'empty_slots':empty_slots,
                                            'req_status':req_status,
                                            'date':datereq.strftime("%Y-%m-%d"),
                                            'from':_fromdt,
                                            'to':todt.strftime("%H:%M"),
                                            'room':room,
                                            'max_date':(datereq + relativedelta(years=1)).strftime("%Y-%m-%d"),
                                            })

def viewRecords(request):

    room,_from,to,datereq,todt,_fromdt = parseRequest(request)
    
    record_slot,record_details = generateRecordDict(room,_from,to,datereq)
    print(record_details)
    record_details = json.dumps(record_details)

    return render(request,'record_home.html',{'record_slot':record_slot,
                                              'record_details':record_details,
                                              'date':datereq.strftime("%Y-%m-%d"),
                                              'from':_fromdt,
                                              'to':todt.strftime("%H:%M"),
                                              'room':room,
                                              'max_date':(datereq + relativedelta(years=1)).strftime("%Y-%m-%d"),
                                              })

def generateRecordDict(room,_from,to,datereq):
    room_dict = generateRoomDict(room,_from,to,datereq)
    record_details = defaultdict(dict)

    if room is None:
        record_slot = {new_list.room: [] for new_list in Rooms.objects.all()}
    else:
        record_slot = {room : []}

    for rooms in room_dict.keys():
        for rec in room_dict[rooms]:
            record_details[rec.id].update(recToDict(rec))
            record_slot[rooms].append({'from_ts':rec.from_ts,
                                        'to_ts':rec.to_ts,
                                        'id':rec.id,
                                    })

    rec_slot_delete_key = []
    for key in record_slot.keys():
        if len(record_slot[key]) == 0:
            rec_slot_delete_key.append(key)
    
    for del_key in rec_slot_delete_key:
        del record_slot[del_key]

    return record_slot,record_details

def generateEmptySlots(room,_from,to,datereq):
    room_dict = generateRoomDict(room,_from,to,datereq)

    if room is None:
        empty_slot = {new_list.room: [] for new_list in Rooms.objects.all()}
    else:
        empty_slot = {room : []}

    delete_record_key = []
    for rooms in room_dict.keys():

        begin_time = None

        # if the slot beginning of day is not boooked
        if room_dict[rooms][0].from_ts != _from and _from < room_dict[rooms][0].from_ts: # time to begin shool 
            empty_slot[rooms].append((_from, room_dict[rooms][0].from_ts))
        
        begin_time = room_dict[rooms][0].to_ts

        for rec_ind in range(1, len(room_dict[rooms])):
            
            empty_slot[rooms].append((begin_time, room_dict[rooms][rec_ind].from_ts))
            begin_time = room_dict[rooms][rec_ind].to_ts
        
        if room_dict[rooms][-1].to_ts != time(23,59) and room_dict[rooms][-1].to_ts < to:
            empty_slot[rooms].append((room_dict[rooms][-1].to_ts,to))

        if len(empty_slot[rooms]) == 0:
            delete_record_key.append(rooms)
    
    #if there is no record of a room then it is empty whole day
    for value in empty_slot.values():
        if len(value) is 0:
            value.append((_from,to))
    
    for del_key in delete_record_key:
        del empty_slot[del_key]

    return empty_slot

def recToDict(rec = Record()):
    rec_dict = {}

    rec_dict['details'] = rec.details
    rec_dict['room'] = rec.room
    rec_dict['event'] = rec.event
    rec_dict['requested_by'] = rec.requested_by
    rec_dict['date'] = str(rec.date)
    rec_dict['from_ts'] = str(rec.from_ts)
    rec_dict['to_ts'] = str(rec.to_ts)

    return rec_dict

"""
give args of room, from and to with date corresponding
It returns a dict with key as room and valuue as the list of Record objects
"""
def generateRoomDict(room,_from,to,datereq):
    record_query_set = None

    if room is None:
        record_query_set = Record.objects.filter(Q(date__exact = datereq) & ((Q(from_ts__gte = _from) & Q(from_ts__lte = to)) | (Q(to_ts__gte = _from) & Q(to_ts__lte = to)))).order_by('room','from_ts')
    else:
        record_query_set = Record.objects.filter(Q(room__exact = room) & Q(date__exact = datereq) &  ((Q(from_ts__gte = _from) & Q(from_ts__lte = to)) | (Q(to_ts__gte = _from) & Q(to_ts__lte = to)))).order_by('room','from_ts')

    room_dict = defaultdict(list)

    for rec in record_query_set:
        room_dict[rec.room].append(rec)

    return room_dict

def parseRequest(request):

    room = None
    _from = None
    to = None
    datereq = None
    _fromdt = None

    if request.method == 'GET':
        now = datetime.now().strftime("%H:%M")
        _from = datetime.strptime(now,"%H:%M").time()
        _fromdt = now
        to = time(23,59)
        todt = datetime.combine(date.today(),time(23,59)).time()
        datereq = date.today()

    else:

        # Set defaults to empty fileds
        if 'room' in request.POST:
            try:
                room = Rooms.objects.get(room = request.POST['room'])
            except Rooms.DoesNotExist:
                room = None

        if 'date' in request.POST:
            try:
                datereq =  datetime.datetime.strptime(request.POST['date'], '%Y-%m-%d')
            except ValueError:
                datereq = date.today()
        else:
            datereq = date.today()
        
        if 'to' in request.POST:
            try:
                to = datetime.strptime(request.POST['to'], '%H:%M').time()
            except ValueError:
                to = time(23,59)
            todt = datetime.combine(datereq,to).time()
        else:
            to = time(23,59)
            todt = datetime.combine(datereq,to).time()

        if 'from' in request.POST:
            try:
                _from = datetime.strptime(request.POST['from'], '%H:%M').time()
            except ValueError:
                if datereq is date.today():
                    _from = datetime.now().time()
                else:
                    _from = time(0)
            _fromdt = datetime.combine(datereq,_from).time()

        else:
            _from = datetime.now().time()
            _fromdt = datetime.combine(datereq,_from)
            
           

    return room,_from,to,datereq,todt,_fromdt