from django.shortcuts import render
from home.models import Record, Rooms
from datetime import date, datetime, time
import time as t
from collections import defaultdict 
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

'''
request.user.is_staff to know if is admin
'''

@csrf_exempt
def homePage(request):
    empty_slots = {}
    if request.method == 'GET':

        now = datetime.now()
        current_time = now.strftime( "%I:%M %p")
        #search for all empty slots
        empty_slots = generateEmptySlots(None,current_time,time(23,59,59), date.today())

    else:
        room = None
        _from = None
        to = None
        datereq = None
        #print("AA               ")
        
        # Set defaults to empty fileds
        if 'room' in request.POST and request.POST['room'] is not '':
            room = request.POST['room']

        if 'date' in request.POST:
            try:
                datereq =  datetime.datetime.strptime(request.POST['date'], "%d/%m/%Y")
            except ValueError:
                datereq = date.today()
        else:
            datereq = date.today()
        
        if 'to' in request.POST:
            try:
                to =  datetime.strptime(request.POST['to'], "%I:%M %p")
            except ValueError:
                to = time(23,59,59)
        else:
            to = time(23,59,59)

        if 'from' in request.POST:
            try:
                _from =  datetime.strptime(request.POST['from'], "%I:%M %p")
            except ValueError:
                _from = datetime.now().time()
        else:
            _from = datetime.now().time()

        empty_slots = generateEmptySlots(room,_from,to,datereq)




    empty_slots = dict(empty_slots)
    return  render(request, 'home_page.html', {'empty_slots':empty_slots})

"""
give args of room, from and to with date corresponding
It returns a dict with key as room and valuue as the list of Record objects
"""
def generateRoomDict(room,_from,to,datereq):
    record_query_set = None

    '''
    print(_from)
    print(to)
    print(room)
    print(datereq)
    '''

    # or None
    if room is None:
        #print("get all rooms")
        record_query_set = Record.objects.filter(date__exact = datereq, from_ts__gt = _from, to_ts__lt = to).order_by('room','from_ts')

    else:
        record_query_set = Record.objects.filter(room__exact = room, date__exact = datereq, from_ts__gt = _from, to_ts__lt = to).order_by('room','from_ts')

    room_dict = defaultdict(list)

    for rec in record_query_set:
        room_dict[rec.room].append(rec)

    #print(room_dict)
    return room_dict


def generateEmptySlots(room,_from,to,datereq):
    room_dict = generateRoomDict(room,_from,to,datereq)

    if room is None:
        empty_slot = {new_list.room: [] for new_list in Rooms.objects.all()}
    else:
        empty_slot = {room : []}

    for rooms in room_dict.keys():

        begin_time = None

        # if the slot beginning of day is not boooked
        if room_dict[rooms][0].from_ts is not _from: # time to begin shool 
            empty_slot[rooms].append((_from, room_dict[rooms][0].from_ts))
        
        begin_time = room_dict[rooms][0].to_ts

        for rec_ind in range(1, len(room_dict[rooms])):
            empty_slot[rooms].append((begin_time, room_dict[rooms][rec_ind].from_ts))
            begin_time = room_dict[rooms][0].to_ts
        
        if room_dict[rooms][-1].from_ts is not time(23,59,59):
            empty_slot[rooms].append((room_dict[rooms][0].to_ts,to))
    
    #if there is no record of a room then it is empty whole day
    for key,value in empty_slot.items():
        if len(value) is 0:
            if Record.objects.filter(room = key, date = datereq).count() is 0:
                value.append((_from,to))

    return empty_slot
             
