import asyncio
import json
import time
from datetime import datetime
import pytz

from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer

#call synchronous code from an asynchronous consumer
from asgiref.sync import sync_to_async, async_to_sync
from channels.db import database_sync_to_async

from django.contrib.auth.signals import user_logged_in, user_logged_out

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from accounts.models import CustomUser
from django.utils import timezone

def get_unique(data):
    norepeat = set()
    for n in data:
        norepeat.add(n)
    return norepeat

def list2dict(set_val):
    mydict = {}
    n = 1
    for v in set_val:
        mydict[n] = v
        n +=1
    return mydict 

def get_all_logged_in_users():
    # Query all non-expired sessions
    # use timezone.now() instead of datetime.now() in latest versions of Django
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    uid_list = []

    # Build a list of user ids from that query
    for session in sessions:
        data = session.get_decoded()
        uid_list.append(data.get('_auth_user_id', None))
    #print(uid_list)

    # Query all logged in users based on id list (for default user)
    #print(User.objects.filter(id__in=uid_list))
    # but 'auth.User' has been swapped for 'accounts.CustomUser' in our project
    users = CustomUser.objects.filter(id__in=uid_list)

    mydict = {}
    n = 1
    for user in users:
        mydict[n] = user.email
        n +=1        

    return mydict

auth_users = []
anonymous_users = []
groups = []
broadcast_socket = None

class broadcast(AsyncWebsocketConsumer):
    global groups
    global anonymous_users
    
    async def connect(self):

        await self.channel_layer.group_add(
            "all_users_group",
            self.channel_name
        )

        await self.accept()

        users1 = await sync_to_async(get_all_logged_in_users)()

        self.socket_port = self.scope['client'][1]

        anonymous_users.append(self.socket_port)
        #print(anonymous_users)

        anonymous_users_dict = list2dict(anonymous_users)
        print("anonymous users",anonymous_users_dict)   

        global broadcast_socket
        broadcast_socket = self
        print("broadcast socket",broadcast_socket)

        groups_dict = list2dict(get_unique(groups))  
        print(groups_dict)

        #when open page, (no channel/user selected yet !): update data by broadcast socket
        await self.send(text_data=json.dumps({
            'socket_port' : self.socket_port, 
            'groups': json.dumps(groups_dict),
            'users1': json.dumps(users1),  #'{"1":"none"}',
            #'users2': json.dumps(anonymous_users_dict), 
        }))

        #broadcast anonymous users
        await self.channel_layer.group_send(
            "all_users_group",
            {
                'type': 'broadcast_connections',
                'users2': json.dumps(anonymous_users_dict),
            }
        )  

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            "all_users_group",
            self.channel_name
        )   

        anonymous_users.remove(self.socket_port)  
        print(anonymous_users) 
        anonymous_users_dict = list2dict(anonymous_users)        

        #broadcast anonymous users
        await self.channel_layer.group_send(
            "all_users_group",
            {
                'type': 'broadcast_connections',
                'users2': json.dumps(anonymous_users_dict),
            }
        )

    #this will be launched also from chat consumer!
    async def broadcast_connections(self, event):
        msg = {}
        if 'groups' in event:
            groups = event['groups']
            if(groups != {}): msg['groups'] = groups
        if 'users1' in event:    
            users1 = event['users1']
            if(users1 != {}): msg['users1'] = users1
        if 'users2' in event: 
            users2 = event['users2']
            if(users2 != {}): msg['users2'] = users2
                    
        print(msg)

        await self.send(text_data=json.dumps(
            msg
        ))





class ChatConsumer(AsyncWebsocketConsumer):
    global groups
    global broadcast_socket

    async def connect(self):
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        self.user_name = self.scope['url_route']['kwargs']['user_name']

        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        groups.append(self.group_name)

        await self.accept()

        #send welcome to user
        await self.send(text_data=json.dumps({
           "message": "Welcome: you are connected to group - " + self.group_name
        }))    

        #using broadcast port as identification for anonymous users (groups and users update)
        self.b_socket_port = broadcast_socket.scope['client'][1]
        groups_dict = list2dict(get_unique(groups))  

        print(groups_dict)
        
        #send to channel: update lists of all opened channels and users online
        await broadcast_socket.channel_layer.group_send(
            "all_users_group",
            {
                'type': 'broadcast_connections',
                'groups': json.dumps(groups_dict),
                'users1': '{}',
                'users2': '{}',
            }
        )                   

    async def disconnect(self, close_code):
        # Leave group channel
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
           
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to group channel
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Send message to room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'socket_port': self.b_socket_port
        }))

