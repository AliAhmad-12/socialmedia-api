from rest_framework import serializers
from .models import *
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from datetime import datetime
import pytz



class Register_Serializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True,validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    password = serializers.CharField(write_only=True,required=True, validators=[validate_password])
    password_confirmation = serializers.CharField(write_only=True)
    class Meta:
        model=CustomUser
        fields=['username','email','password','password_confirmation']

    def validate(self, attrs):
   
        if attrs['password'] != attrs['password_confirmation']:
            raise serializers.ValidationError({"password": "password and password_confirmation are not the same !"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirmation')  # إزالة حقل التأكيد
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])  # تعيين كلمة المرور بشكل آمن
        user.save()
        return user


class LoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(required=True)
    class Meta:
        model=CustomUser
        fields=['email','password']


class ChangePasswordSerializer(serializers.ModelSerializer):

    password1=serializers.CharField(max_length=150,write_only=True,style={'input_type':'password'})
    password2=serializers.CharField(max_length=150,write_only=True,style={'input_type':'password'})
    class Meta:
        model=CustomUser
        fields=['password1','password2']

    def validate(self,data):

        password1=data.get('password1')
        password2=data.get('password2')
        user=self.context.get('user')
        if password1 != password2:
            raise serializers.ValidationError({'password':"password and confirm password  does't match"})
        user.set_password(password1)
        user.save()
        return data


class UserSerializer(serializers.ModelSerializer):
    bio=serializers.CharField(source='userprofile.bio')
    image=serializers.ImageField(source='userprofile.image')
    date_joined=serializers.DateTimeField(format="%Y/%m %a at %I:%M %p")
    last_seen=serializers.SerializerMethodField(read_only=True)

    class Meta:
        model=CustomUser
        fields=['id','username','date_joined','bio','image','last_seen','online_status']

    def to_representation(self,instance):
        data=super().to_representation(instance)
        image=data['image']

        if image:
            if image.startswith('/media/users_photo/'):
                image= f'http://localhost:8000{image}'
                data['image']=image
            else:
                data['image']=f'https://lh3{image[19:]}'

        return data
    

    def get_last_seen(self,obj):
       
        utc_time = obj.last_seen  # استبدل date_field بحقل التاريخ الخاص بك
        if isinstance(utc_time, str):
            utc_time = datetime.fromisoformat(utc_time[:-1]) 

        utc_time = utc_time.replace(tzinfo=pytz.UTC)  
        local_tz=pytz.timezone('Asia/Damascus')
        local_time=utc_time.astimezone(local_tz)
        return local_time.strftime('%I:%M %p')
    

class ProfileUserSerializer(UserSerializer):
    num_posts=serializers.SerializerMethodField()
    follower_count=serializers.SerializerMethodField()
    following_count=serializers.SerializerMethodField()
    class Meta:
        model=CustomUser
        fields=UserSerializer.Meta.fields + ['num_posts','follower_count','following_count']

    def get_follower_count(self,obj):
        return obj.follow_to.count()

    def get_following_count(self,obj):
        return obj.follow_from.count()
    def get_num_posts(self,obj):
        return obj.user_posts.count()


class CommentSerializer(serializers.ModelSerializer):
    user=serializers.CharField(read_only=True,source='user.username')
    user_id=serializers.IntegerField(read_only=True,source='user.id')
    user_image=serializers.ImageField(read_only=True,source='user.userprofile.image')
    created=serializers.SerializerMethodField()
    class Meta:
        model=Comment
        fields=['uid','content','created','user','user_image','user_id']

    def to_representation(self,instance):
        data=super().to_representation(instance)
        image=data['user_image']
        
        if image:
            if image.startswith('/media/users_photo/'):
                image= f'http://localhost:8000{image}'
                data['user_image']=image
            else:
                data['user_image']=f'https://lh3{image[19:]}'
        return data

    def get_created(self,obj):
        return obj.created.strftime("%a at %I:%M %p")


class PostSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    created=serializers.SerializerMethodField()
    likes_count=serializers.SerializerMethodField()
    comments_count=serializers.SerializerMethodField()
    is_save=serializers.SerializerMethodField()
    is_liked=serializers.SerializerMethodField()
    edit_info=serializers.SerializerMethodField()
    post_comments=CommentSerializer(read_only=True,many=True)


    class Meta:
        model=Post
        fields=['uid','content','image','created','user','likes_count','comments_count','is_save','is_liked','post_comments','edit_info']

    def get_edit_info(self,obj):
        user=self.context.get('selfuser')
        return user.id ==obj.user.id


    def get_is_save(self,obj):
        user=self.context.get('selfuser')
        if user in obj.saves.all():
            return True
        return False

    def get_is_liked(self,obj):
        user=self.context.get('selfuser')
        if user in obj.likes.all():
            return True
        return False

    def get_likes_count(self,obj):
        return obj.likes.count()

    def get_comments_count(self,obj):
        return obj.post_comments.count()        

    def get_created(self, obj):
        return obj.created.strftime("%a at %I:%M %p")



class MessageSerializer(serializers.ModelSerializer):
    sender=serializers.StringRelatedField()
    timestamp=serializers.SerializerMethodField()
    class Meta:
        model=Message
        fields=['id','sender','text','attachment','timestamp','is_read']
       
    
    def get_timestamp(self, obj):
        utc_time = obj.timestamp 
        if isinstance(utc_time, str):
            utc_time = datetime.fromisoformat(utc_time[:-1])

        utc_time = utc_time.replace(tzinfo=pytz.UTC)
        local_tz=pytz.timezone('Asia/Damascus')
        local_time=utc_time.astimezone(local_tz)
        return local_time.strftime('%I:%M %p | %b %d')

class ChatSerializer(serializers.ModelSerializer):
    messages=MessageSerializer(many=True)

    class Meta:
        model=Chat
        fields=['id','messages']



class ChatListSerializer(serializers.ModelSerializer):

    last_message=serializers.SerializerMethodField()
    start_time=serializers.SerializerMethodField()
    user_detail=serializers.SerializerMethodField()
    class Meta:
        model=Chat
        fields=['id','sender','receiver','last_message','start_time','user_detail']
     
    def get_start_time(self, obj):
        return obj.start_time.strftime("%m/%d/%Y")
    def get_last_message(self,obj):
        last_message=obj.messages.last()
        if last_message:
            message_data={
                "text":last_message.text,
                "attachment":last_message.attachment or '',
                "timestamp":last_message.timestamp
                }
            return message_data
        else:
            return None
        
    def get_user_detail(self,obj):
        request=self.context.get('request')
        user=request.user
        participant_user=obj.receiver if user == obj.sender else obj.sender
        serializer=UserSerializer(participant_user)
        data={'id':serializer.data['id'],'username':serializer.data['username'],'image':serializer.data['image'],'online_status':serializer.data['online_status']}
        return data