import os, sys, django

project_path = "."
project_settings = "config"

if project_path == "":
    sys.path.append(os.getcwd())
else:
    sys.path.append(project_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", project_settings + ".settings")
django.setup()


import channels.layers

channel_layer = channels.layers.get_channel_layer()
from asgiref.sync import async_to_sync
async_to_sync(channel_layer.send)('test_channel', {'type': 'hello'})
ret = async_to_sync(channel_layer.receive)('test_channel')
print(ret)

if(ret == {'type': 'hello'}):
    print("Ok: redis is working")
else:
    print("Error: redis not working")
