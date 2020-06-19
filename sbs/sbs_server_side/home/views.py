from django.shortcuts import render
from home.models import Record
from datetime import date, datetime, time
import time as t
from collections import defaultdict 


def homePage(request):
    empty_slots = {}
    if request.method == 'GET':

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        #search for all empty slots
        empty_slots = generateEmptySlots(None,current_time,time(23,59,59), date.today())

    else:
        room = request.POST['room']
        _from = request.POST['from']
        to = request.POST['to']
        datereq = request.POST['date']
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
    empty_slot = defaultdict(list)

    for rooms in room_dict.keys():

        begin_time = None

        # if the slot beginning of day is not boooked
        if room_dict[rooms][0].from_ts is not time(7): # time to begin shool 
            empty_slot[rooms].append((time(7), room_dict[rooms][0].from_ts))
        
        begin_time = room_dict[rooms][0].to_ts

        for rec_ind in range(1, len(room_dict[rooms])):
            empty_slot[rooms].append((begin_time, room_dict[rooms][rec_ind].from_ts))
            begin_time = room_dict[rooms][0].to_ts
        
        if room_dict[rooms][-1].from_ts is not time(23,59,59):
            empty_slot[rooms].append((room_dict[rooms][0].to_ts,time(23,59,59)))
    
    #print(room_dict)
    #print(empty_slot)
    return empty_slot
             
