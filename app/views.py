
from rest_framework.views import APIView
from .serializers import *
from .models import *
from django.db.models import Q,Count
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework.generics import DestroyAPIView,UpdateAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView,ListAPIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from .authentication import CookiesJWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework_simplejwt.views import (
    TokenRefreshView
)

from social_django.utils import load_strategy
from social_core.backends.google import GoogleOAuth2
from social_django.models import UserSocialAuth


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class Register(APIView):
    def post(self,request,format=None):
        serializers=Register_Serializer(data=request.data)
        if serializers.is_valid(raise_exception=True):
            user=serializers.save()
            token=get_tokens_for_user(user)
            response=Response({'msg':'your account created successfully'},status=status.HTTP_201_CREATED)
            response.set_cookie(
                key='access_token',
                value=token['access'],
                httponly=True,
                secure=False,
                max_age=1800
                )
            response.set_cookie(
                key='refresh_token',
                value=token['refresh'],
                httponly=True,
                secure=False,
                # max_age=604800  #refresh_token له صلاحية أطول (أسبوع).
                max_age=172800
             
                )
            return response
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)



class Login(APIView):
    permission_classes=[AllowAny]
    def post(self,request,format=None):
        serializers=LoginSerializer(data=request.data)
        if serializers.is_valid(raise_exception=True):
            email=serializers.data.get('email')
            password=serializers.data.get('password')
            if not email or not password:
                return Response({'error':"username and password are required !!"})
            user=authenticate(email=email,password=password)
            if user is not None:
                token=get_tokens_for_user(user)
                response=Response({'msg':"Login Success"},status=status.HTTP_200_OK)
                response.set_cookie(
                key='access_token',
                value=str(token['access']),
                httponly=True,
                secure=False,
                max_age=1800
                )
                response.set_cookie(
                key='refresh_token',
                value=str(token['refresh']),
                httponly=True,
                secure=False,
                # max_age=604800  #refresh_token له صلاحية أطول (أسبوع).
                max_age=172800
             
                  #refresh_token له صلاحية أطول (أسبوع).
                
                )
                return response
                # return Response({'msg':'Login Success','access_token':token['access'],'refresh_token':token['refresh']},status=status.HTTP_200_OK)
            else:
                return Response({'error':'Email or Password not Valid '},status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializers.errors)



class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'detail': 'Refresh token not provided'}, status=status.HTTP_400_BAD_REQUEST)

        request.data['refresh'] = refresh_token
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data.get('access')
            custom_response = Response({'refreshed':True,'access_token':access_token}, status=status.HTTP_200_OK)

            custom_response.set_cookie(
                'access_token',
                str(access_token),
                httponly=True,
                secure=False,
                max_age=1800
            )
            return custom_response

        return response



class ChangePasswordView(APIView):
    authentication_classes=[CookiesJWTAuthentication]
    permission_classes=[IsAuthenticated]
    def post(self,request,format=None):
        serializers=ChangePasswordSerializer(data=request.data,context={'user':request.user})
        if serializers.is_valid(raise_exception=True):
            serializers.save
            return Response({'msg':'password was updated successfully '},status=status.HTTP_200_OK)
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)



class IsAuthenticatedView(APIView):
    def get(self,request):
        
        access_token=request.COOKIES.get('access_token')
        if not access_token:
            return Response({'is_authenticated':False},status=status.HTTP_401_UNAUTHORIZED)
        try:
            jwt_auth=CookiesJWTAuthentication()
            validated_token=jwt_auth.get_validated_token(access_token)
            user=jwt_auth.get_user(validated_token)
            serializers=UserSerializer(user)
            return Response({'is_authenticated':True,'user':serializers.data,'access_token':access_token},status=status.HTTP_200_OK)
        except AuthenticationFailed:
            return Response({'is_authenticated':False},status=status.HTTP_401_UNAUTHORIZED)


    

class Logout(APIView):
    # permission_classes=[IsAuthenticated]
    def post(self,request):
        refresh_token=request.COOKIES.get('refresh_token')
        if refresh_token:
            try:
                token=RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        response=Response({'msg':"Successfully logged out"},status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response



class ProfileUserView(APIView):

    permission_classes=[IsAuthenticated]
    def get(self,request,user_id=None):
        user=get_object_or_404(CustomUser,id=request.user.id)
        if user_id is not None:
            user=get_object_or_404(CustomUser,id=user_id)
        serializers=ProfileUserSerializer(user)
        return Response(serializers.data,status=status.HTTP_200_OK)


class PostApiView(APIView):

    permission_classes=[IsAuthenticated]
    
    def get(self,request,format=None):
        posts=Post.objects.all()
        serializers=PostSerializer(posts,many=True,context={'selfuser':request.user})
        return Response(serializers.data,status=status.HTTP_200_OK)
    def post(self,request,format=None):
        serializers=PostSerializer(data=request.data,context={'selfuser':request.user})
        serializers.is_valid(raise_exception=True)
        serializers.validated_data['user']=request.user
        serializers.save()
        return Response(serializers.data,status=status.HTTP_201_CREATED)
    def put(self,request,post_uid,format=None):
        post=get_object_or_404(Post,uid=post_uid)
        serializers=PostSerializer(post,data=request.data,partial=True,context={'selfuser':request.user})
        serializers.is_valid(raise_exception=True)
        serializers.validated_data['user']=request.user
        serializers.save()
        return Response(serializers.data,status=status.HTTP_201_CREATED)
    def delete(self,request,post_id,format=None):
        post=get_object_or_404(Post,uid=post_id)
        post.delete()
        return Response({'deleted_post':True},status=status.HTTP_200_OK)





class MyPostsView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request,user_id=None,format=None):
        user=request.user
        if user_id:
            user=get_object_or_404(CustomUser,id=user_id)
        
        posts=Post.objects.filter(user=user)
        serializers=PostSerializer(posts,many=True,context={'selfuser':request.user})
        return Response(serializers.data,status=status.HTTP_200_OK)




class CommentApiView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,post_id,format=None):
        user=request.user
        post=get_object_or_404(Post,uid=post_id)
        serializer=CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['post']=post
        serializer.validated_data['user']=user
        serializer.save()
        return Response(serializer.data,status=status.HTTP_200_OK)
    def put(self,request,post_id,comment_id,format=None):
        user=request.user
        post=get_object_or_404(Post,uid=post_id)
        comment=get_object_or_404(Comment,uid=comment_id)
        serializer=CommentSerializer(comment,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['post']=post
        serializer.validated_data['user']=user
        serializer.save()
        return Response(serializer.data,status=status.HTTP_200_OK)
    def delete(self,request,comment_id,format=None):
        comment=get_object_or_404(Comment,uid=comment_id)
        print(comment)
        comment.delete()
        return Response({'deleted_comment':True},status=status.HTTP_200_OK)



class LikePost(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,post_uid):
        user=request.user
        post=get_object_or_404(Post,uid=post_uid)
        if user in post.likes.all():
            post.likes.remove(user)
            return Response({'dislike':True},status=status.HTTP_200_OK)
        else:
            post.likes.add(user)
            return Response({'like':True},status=status.HTTP_200_OK)



class SavePost(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,post_uid):
        user=request.user
        post=get_object_or_404(Post,uid=post_uid)
        if user in post.saves.all():
            post.saves.remove(user)
            return Response({'save':False},status=status.HTTP_200_OK)
        else:
            post.saves.add(user)
            return Response({'save':True},status=status.HTTP_200_OK)

    def get(self,request,format=None):
        user=request.user
        saved_posts=user.user_saves.all()
        serializers=PostSerializer(saved_posts,many=True,context={'selfuser':request.user})
        return Response(serializers.data,status=status.HTTP_200_OK)





class FollowUser(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,user_id,format=None):
        user_to=get_object_or_404(CustomUser,id=user_id)

        user,created=Contact.objects.get_or_create(user_to=user_to,user_from=request.user)
        if created:
            return Response({'action':'follow'},status=status.HTTP_200_OK)
        else:
            user.delete()
            return Response({'action':'unfollow'},status=status.HTTP_200_OK)

    def get(self,request,format=None):
        user=request.user
        following=user.followers.all()
        serializers=UserSerializer(following,many=True)
        return Response(serializers.data,status=status.HTTP_200_OK)





class SuggestionView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,format=None):
        followers_id=Contact.objects.filter(user_from=request.user).values('user_to_id')
        arr_id=[i['user_to_id'] for i in followers_id]
        arr_id.append(request.user.id)
        suggestion=Contact.objects.filter(user_from__in=arr_id).exclude(user_to__in=arr_id).values('user_to_id')
        
        users_id=[i['user_to_id'] for i in suggestion]
        users=CustomUser.objects.filter(id__in=users_id)

        serializers=UserSerializer(users,many=True)
        return Response(serializers.data,status=status.HTTP_200_OK)







class GoogleLoginView(APIView):
    def post(self, request):
        google_token = request.data.get('token')

        if not google_token:
            return Response({'error': 'Missing Google token'}, status=400)

        try:
            strategy = load_strategy(request)
            backend = GoogleOAuth2(strategy=strategy)

            user_data = backend.user_data(google_token)
            email = user_data.get('email')
            picture=user_data.get('picture')

            if not email:
                return Response({'error': 'Email not provided by Google'}, status=400)

            user = CustomUser.objects.filter(email=email).first()
            if user:
                social_auth = UserSocialAuth.objects.filter(user=user, provider='google-oauth2').first()
                if not social_auth:
                    UserSocialAuth.objects.create(user=user, provider='google-oauth2', uid=email)
            else:
                user = backend.do_auth(google_token)
            profile=ProfileUser.objects.get(user=user)

            profile.image=picture
            profile.save()
            if user and user.is_active:
                refresh = RefreshToken.for_user(user)
                response = Response({'message': 'Login successful'})
                response.set_cookie(
                    key='access_token',
                    value=str(refresh.access_token),
                    httponly=True,
                    secure=False
                )
                response.set_cookie(
                    key='refresh_token',
                    value=str(refresh),
                    httponly=True,
                    secure=False
                )
                return response

            return Response({'error': 'Invalid credentials'}, status=401)

        except Exception as e:
            return Response({'error': str(e)}, status=400)
        


class StartChat(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,format=None):
        data=request.data
        user_id=data["id"]

        participant=get_object_or_404(CustomUser,id=user_id)

        conversation=Chat.objects.filter(Q(sender=request.user,receiver=participant)|Q(sender=participant,receiver=request.user))
        if conversation.exists():
            return redirect(reverse('get_conversation', args=(conversation[0].id,)))
        else:
            conversation=Chat.objects.create(sender=request.user,receiver=participant)
            serializer=ChatSerializer(instance=conversation)
            participant_serializer = UserSerializer(participant)
            user_detail={"username":participant_serializer.data["username"],"user_image":participant_serializer.data["image"]}
            response_data={"conversation":serializer.data,"last_seen":participant_serializer.data['last_seen'],"online_status":participant_serializer.data['online_status'],"user_detail":user_detail}
            return Response(response_data,status=status.HTTP_200_OK)
        

class get_conversation(APIView):
    def get(self,request,chat_id,format=None):
        conversation=Chat.objects.filter(id=chat_id)
        if not conversation.exists():
            return Response({'message': 'Conversation does not exist'})

        else:
            participant=conversation[0].receiver if conversation[0].sender == request.user else conversation[0].sender
            print('participant',participant)
            participant_serializer = UserSerializer(participant)
            serializer = ChatSerializer(instance=conversation[0])
            user_detail={"username":participant_serializer.data["username"],"user_image":participant_serializer.data["image"]}

            response_data={"conversation":serializer.data,"last_seen":participant_serializer.data['last_seen'],"online_status":participant_serializer.data['online_status'],"user_detail":user_detail}

            return Response(response_data,status=status.HTTP_200_OK)


class UpdateMessage(APIView):
    permission_classes=[IsAuthenticated]
    def put(self,request,message_id,format=None):
        message=get_object_or_404(Message,id=message_id,sender=request.user)
        serializer=MessageSerializer(message,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_200_OK)


class DeleteMessage(APIView):
    permission_classes=[IsAuthenticated]
    def delete(self,request,message_id,format=None):
        message=get_object_or_404(Message,id=message_id,sender=request.user)
        message.delete()
        return Response({"msg":"ok"},status=status.HTTP_200_OK)



class Conversations(ListAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=ChatListSerializer

    def get_queryset(self):
            chats = Chat.objects.filter(
                Q(sender=self.request.user) | Q(receiver=self.request.user)
            ).annotate(
                message_count=Count('messages')
            ).filter(
                message_count__gt=0 
            )
            return chats

    def get_serializer_context(self):
        return {'request':self.request}



