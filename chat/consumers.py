# chat/consumers.py
import asyncio
import json
import time
from datetime import datetime
import pytz

from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer

from django.contrib.auth.signals import user_logged_in, user_logged_out

groups = []
broadcast_socket = None

class clock(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.start_periodic_task()

    async def start_periodic_task(self):
        while True:
            bucharest = pytz.timezone('Europe/Bucharest')
            now_local = datetime.now(tz=bucharest)
            current_time = now_local.strftime("%H:%M:%S - %d/%m/%Y -") + " Europe/Bucharest"
            #now = datetime.now()
            #current_time = now.strftime("%H:%M:%S")
            await self.send(text_data=json.dumps({
               'message': current_time
            }))
            await asyncio.sleep(1)


def get_unique(data):
    norepeat = set()
    for n in data:
        norepeat.add(n)
    return norepeat


def set2dict(set_val):
    mydict = {}
    n = 1
    for v in set_val:
        mydict[n] = v
        n +=1
    return mydict    

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from accounts.models import CustomUser
from django.utils import timezone

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

    return users



def send_logged_users(sender, user, request, **kwargs):

    #users_dict = {}
    #users = get_all_logged_in_users()
    #for user in users:
    #    users_dict[user.pk] = user.username
    #print(users_dict)

    print("here-here", sender,user)
    ret = get_all_logged_in_users()
    print(ret)
    print("B SOCKET",broadcast_socket)

#    #send to channel: update lists of all opened channels and users online
#    await broadcast_socket.channel_layer.group_send(
#        "all_users_group",
#        {
#            'type': 'broadcast_connections',
#            'groups': json.dumps(groups_dict),
#            'users': '{}',
#        }
#    )    


user_logged_in.connect(send_logged_users)
user_logged_out.connect(send_logged_users)


class broadcast(AsyncWebsocketConsumer):
    
    async def connect(self):

        global groups

        await self.channel_layer.group_add(
            "all_users_group",
            self.channel_name
        )

        await self.accept()

        self.socket_port = self.scope['client'][1]

        global broadcast_socket
        broadcast_socket = self
        print(broadcast_socket)

        groups_dict = set2dict(get_unique(groups))  
        print(groups_dict)

        #when open page, (no channel/user selected yet): update data by broadcast socket
        await self.send(text_data=json.dumps({
            'socket_port' : self.socket_port, 
            'groups': json.dumps(groups_dict),
            'users1': '{}',
        }))        

    #this will be launched from chat consumer!
    async def broadcast_connections(self, event):
        msg = {}
        groups = event['groups']
        users1 = event['users1']
        users2 = event['users2']
        if(groups != {}): msg['groups'] = groups
        if(users1 != {}): msg['users1'] = users1
        if(users2 != {}): msg['users2'] = users2
        #socket_port = event['socket_port']
        print(groups)
        print(msg)
        #await self.send(text_data=json.dumps({
        #    'groups' : groups, 
        #    'users1' : users1,
        #    'users2' : users2,
        #}))
        await self.send(text_data=json.dumps(
            msg
        ))    



class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        global groups
        global broadcast_socket
        self.groups = groups

        self.group_name = self.scope['url_route']['kwargs']['group_name']
        self.user_name = self.scope['url_route']['kwargs']['user_name']
        #self.channel_name = 'chat_%s' % self.group_name

        groups.append(self.group_name);    

        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        #send welcome to user
        await self.send(text_data=json.dumps({
           "message": "Welcome: you are connected to group - " + self.group_name
        }))        
        
        #using broadcast port as identification for anonymous users (groups and users update)
        self.b_socket_port = broadcast_socket.scope['client'][1]
        groups_dict = set2dict(get_unique(groups))  

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
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        groups.remove(self.group_name);
        groups_dict = set2dict(get_unique(groups))
        print(groups_dict)

        await broadcast_socket.channel_layer.group_send(
            "all_users_group",
            {
                'type': 'broadcast_connections',
                'groups': json.dumps(groups_dict),
                'users1': '{}',
                'users2': '{}',
            }
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

    # Send message to group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'socket_port': self.b_socket_port
        }))

       





#testing 
#class update_groups(AsyncWebsocketConsumer):
#    
#    async def connect(self):
#        await self.accept()
#        await self.start_periodic_task()
#
#    async def start_periodic_task(self):
#        global groups
#                
#        while True:
#            groups_dict = set2dict(groups)
#            #await self.send(text_data=json.dumps({
#            #   '1': "One", '2': "Two", '3': "Three"
#            #}))
#            await self.send(text_data=json.dumps( groups_dict ))
#            await asyncio.sleep(5)