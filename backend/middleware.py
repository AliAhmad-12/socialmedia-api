from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from http.cookies import SimpleCookie
from app.authentication import CookiesJWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


@database_sync_to_async
def get_user_from_jwt(token):
    try:
        jwt_auth = CookiesJWTAuthentication()
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
        print(user)
        return user
    except (InvalidToken, TokenError):
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):


 async def __call__(self, scope, receive, send):
        """
        Middleware للتحقق من المستخدم باستخدام access_token من Query Parameters.
        """
        # استخراج Query Parameters من scope
        query_string = scope.get("query_string", b"").decode("utf-8")  # تحويلها إلى نص
        query_params = dict(param.split('=') for param in query_string.split('&') if '=' in param)  # تحويلها إلى dict

        # الحصول على access_token من Query Parameters
        access_token = query_params.get("access_token", None)

        if access_token:
            # إذا تم العثور على access_token، التحقق من المستخدم
            user = await get_user_from_jwt(access_token)
            scope['user'] = user
        else:
            # إذا لم يتم العثور على access_token، اجعل المستخدم AnonymousUser
            scope['user'] = AnonymousUser()

        # استدعاء باقي الـ Middleware
        return await super().__call__(scope, receive, send)




    # async def __call__(self, scope, receive, send):
    #     print("JWTAuthMiddleware is being called!")  # تحقق من استدعاء Middleware
    #     headers = dict(scope.get('headers', []))
    #     print(headers.get(b'cookie', b''))
    #     cookie_header = headers.get(b'cookie', b'').decode('utf-8')  # Decode cookie header
    #     cookies = SimpleCookie(cookie_header)

    #     access_token = cookies.get('access_token').value if 'access_token' in cookies else None

    #     print(f"Access Token: {access_token}")  # تحقق من قيمة access_token

    #     if access_token:
    #         user = await get_user_from_jwt(access_token)
    #         print(f"Authenticated User: {user}")  # تحقق من المستخدم
    #         scope['user'] = user
    #     else:
    #         print("No access token found, setting AnonymousUser.")
    #         scope['user'] = AnonymousUser()

    #     return await super().__call__(scope, receive, send)
