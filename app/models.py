from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager,PermissionsMixin
from django.conf import settings
import uuid

from django.utils import timezone
from datetime import datetime
class CustomUserManger(BaseUserManager):
    def create_user(self,email,password=None,**extra_fields):
        if not email:
            raise ValueError("The email must be set")
        email=self.normalize_email(email)
        user=self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self,email,password=None,**extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser,PermissionsMixin):
    username=models.CharField(max_length=100)
    email=models.EmailField(unique=True)
    follow=models.ManyToManyField('self',through='Contact',related_name='followers',symmetrical=False)
    last_seen=models.DateTimeField(blank=True,null=True,default=datetime.now())
    online_status=models.BooleanField(default=False)

    USERNAME_FIELD="email"
    REQUIRED_FIELDS=[]
    objects=CustomUserManger()

    def __str__(self):
        return self.username
    
    def update_last_seen(self,timestamp=None):
        self.last_seen=timestamp or timezone.now()
        self.save()


class Contact(models.Model):
    user_to=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='follow_to')
    user_from=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='follow_from')
    created=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-created']
        indexes=[
        models.Index(fields=['-created'])
        ]
        unique_together=('user_to','user_from')
        
    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'


class ProfileUser(models.Model):
    uid=models.UUIDField(primary_key=True,editable=False,default=uuid.uuid4,unique=True)
    user=models.OneToOneField('CustomUser',on_delete=models.CASCADE,related_name='userprofile')
    image=models.ImageField(upload_to='users_photo',blank=True,null=True)
    # cover=models.ImageField(upload_to='users_photo',blank=True,null=True)
    bio=models.TextField(max_length=150,blank=True,null=True)


    def __str__(self):
        return self.user.username


class Post(models.Model):
    uid=models.UUIDField(primary_key=True,editable=False,default=uuid.uuid4,unique=True)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,related_name='user_posts',on_delete=models.CASCADE)
    content=models.TextField(max_length=500)
    image=models.ImageField(upload_to="images/%Y/%m/%d/",blank=True,null=True)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)
    saves=models.ManyToManyField(settings.AUTH_USER_MODEL,blank=True,related_name="user_saves")
    likes=models.ManyToManyField(settings.AUTH_USER_MODEL,blank=True,related_name='user_likes')
    class Meta:
        ordering=['-created']
        indexes=[models.Index(fields=['-created']),]
    def __str__(self):
        return self.content


class Comment(models.Model):
    uid=models.UUIDField(primary_key=True,editable=False,default=uuid.uuid4,unique=True)
    post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name='post_comments')
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="user_comments")
    content=models.TextField(max_length=150,blank=False)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)
    def __str__(self):
        return f'" {self.content} "  on  " {self.post.content} "'
    class Meta:
        ordering=['-created']
        indexes=[models.Index(fields=['-created'])]


class Chat(models.Model):
    sender=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,related_name='chat_starter')
    receiver=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,related_name='chat_participant')
    start_time=models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.sender.username+':'+self.receiver.username
    
class Message(models.Model):
    sender=models.ForeignKey(CustomUser,on_delete=models.SET_NULL,null=True,related_name='message_sender')
    text=models.TextField(blank=True,null=True)
    attachment=models.FileField(blank=True)
    conversation_id=models.ForeignKey(Chat,on_delete=models.CASCADE,related_name='messages')
    timestamp=models.DateTimeField(auto_now_add=True)
    is_read=models.BooleanField(default=False)

    class Meta:
        ordering=['timestamp']

