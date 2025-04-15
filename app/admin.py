from django.contrib import admin

from .models import *


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display=['id','username','email']



@admin.register(ProfileUser)
class ProfileUser(admin.ModelAdmin):
    list_display=['uid','user','image','bio']


@admin.register(Contact)
class ContactUser(admin.ModelAdmin):
    list_display=['user_from','user_to','created']



@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('uid','user', 'content', 'image', 'created', 'updated')
    list_filter = ('user', 'created', 'updated')
    raw_id_fields = ('saves', 'likes')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ( 'uid','post', 'user', 'content', 'created', 'updated')
    list_filter = ('post', 'user', 'created', 'updated')

@admin.register(Chat)
class Chat(admin.ModelAdmin):
    list_display=("id",'sender','receiver','start_time')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display=('id','sender',"text",'attachment','conversation_id','timestamp')