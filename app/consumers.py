from channels.consumer import StopConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import *
from .serializers import *

import base64
import os
from django.core.files.base import ContentFile
from django.utils.timezone import make_aware
from datetime import datetime
class ChatConsumer(AsyncWebsocketConsumer):

    
    async def connect(self):
        print('websocket connected !')
        self.room_id=self.scope['url_route']['kwargs']['room_id']
        self.room_group_name=f'chat_{self.room_id}'
        # self.user=self.scope['user']
        self.user=await database_sync_to_async(CustomUser.objects.get)(id=self.scope['user'].id)

        await self.set_online_status(True)
        await self.send_online_status(self.user.id,True)
        if self.user.is_authenticated:
            conversation =await database_sync_to_async(Chat.objects.get)(id=int(self.room_id))
            await self.mark_messages_as_read(self.user,conversation)
        await self.channel_layer.group_add(self.room_group_name,self.channel_name)
        await self.accept()




    @database_sync_to_async
    def mark_messages_as_read(self,user,conversation):
        messages=Message.objects.filter(conversation_id=conversation,is_read=False).exclude(sender=user)
        for message in messages:
            message.is_read=True
            message.save()


    @database_sync_to_async
    def set_online_status(self,is_online):
        if self.user.is_authenticated:
            self.user.online_status=is_online
            self.user.save()
            

    async def receive(self, text_data=None, bytes_data=None):
            message=json.loads(text_data)
            
            if message.get("type")=="last_seen":
                print('last_seen',message)
                lastSeenTime=message["time_stamp"]
                if lastSeenTime and self.user.is_authenticated:
                    await database_sync_to_async(self.user.update_last_seen)(lastSeenTime)
            elif message.get("type")=="chat_message":
                print('chat_message',message)
                await self.channel_layer.group_send(self.room_group_name,{
                'type':'chat.message',
                'message':message
                })
            elif message.get("type")=="mark_as_read":
                print('message_mark',message)
                user_id=message["user_id"]
                message_id=message["message_id"]
                await self.send_mark_messages_as_read(message_id,user_id)


    async def chat_message(self,event):
        message=event["message"]
        message_text=message["text"] if "text" in message else None
        is_read=message["is_read"]
        message_attachment=message["attachment"] if "attachment" in message else None
        if message_attachment:

            format, imgstr = message_attachment.split(';base64,')
            ext = format.split('/')[-1]  # الحصول على امتداد الصورة

            image_file = ContentFile(base64.b64decode(imgstr), name=f"image.{ext}")
        else:
            image_file = None
        conversation =await database_sync_to_async(Chat.objects.get)(id=int(self.room_id))
        
        sender=self.user
        if(message_text):
            message =await database_sync_to_async(Message.objects.create) (
                sender=sender,
                text=message_text,
                attachment=image_file,
                is_read=is_read,
                conversation_id=conversation,
            )
        else:
            message =await database_sync_to_async(Message.objects.create) (
                sender=sender,
                attachment=image_file ,
                is_read=is_read,
                conversation_id=conversation,
            )
             
        serializer=MessageSerializer(instance=message)
        await self.send(text_data=json.dumps(serializer.data))


    @database_sync_to_async
    def send_mark_messages_as_read(self,message_id,user_id):
        try:
            message=Message.objects.get(id=message_id)
            user=CustomUser.objects.get(id=user_id)
            if message.sender!=user:
                message.is_read=True
                message.save()
            self.channel_layer.group_send(self.room_group_name,{
                'type':'chat.message_read',
                'message_id':message_id
            })

        except Message.DoesNotExist:
            print(f"message with id{message_id} not found")

    
    async def chat_message_read(self,event):
        message_id=event['message_id']
        await self.send(text_data=json.dumps({"type":"message_read","message_id":message_id}))



    async def send_online_status(self,user_id,is_online):
        await self.channel_layer.group_send(self.room_group_name,{
            'type':'chat.online_status',
            'user_id':user_id,
            'is_online':is_online
            })
        


    async def chat_online_status(self,event):
        user_id=event['user_id']
        is_online=event['is_online']
        await self.send(text_data=json.dumps({"type":"online_status","user_id":user_id,"is_online":is_online}))


    async def disconnect(self,close_code):
        print('websocket disconnected .. !')
        await self.channel_layer.group_discard(self.room_group_name,self.channel_name)
        await self.set_online_status(False)
        await self.send_online_status(self.user.id,False)